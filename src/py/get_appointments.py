import requests
import json
import psycopg2
import time
from datetime import datetime
from datetime import date
import pytz

from utils import get_db_connection

api_base_url = "https://cdn-api.co-vin.in/api"

conn = get_db_connection()

insert_session_query = """ INSERT INTO public.appointments (session_id, district_id, center_id, center_name, pincode, vaccine, fee_type, date, available_capacity, min_age) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
appointments_district_query = """ SELECT session_id, district_id, center_id, center_name, pincode, vaccine, fee_type, date, available_capacity, min_age from public.appointments where district_id = %s"""
delete_appointments_district = """ DELETE FROM public.appointments where district_id = %s"""

subscriptions_query = """ SELECT id, name, email, district_id, webhook from public.slack_subscriptions"""


def main():
    start_t = time.time()
    print("Starting get_appointments {}".format(datetime.now(pytz.timezone('Asia/Kolkata'))))
    print("Accessing API at {}".format(api_base_url))
    clear_db()
    districts = load_districts()
    slack_subscriptions = load_subscriptions()


    get_appointments(districts, slack_subscriptions)
    conn.close()

    end_t = time.time()
    print("Time taken to get appointments: {:.2f}s".format(end_t - start_t))
    print("Finished get_appointments {}".format(datetime.now(pytz.timezone('Asia/Kolkata'))))

def clear_db():
    cur = conn.cursor()
        
	# close the communication with the PostgreSQL
    cur.close()

def load_districts():
    cur = conn.cursor()
        
    print('Loading districts from db')
    districts_query = "SELECT districts.id, districts.name, districts.state_id, states.name FROM districts JOIN states ON districts.state_id = states.id"
    cur.execute(districts_query)

    districts = cur.fetchall()
    
	# close the communication with the PostgreSQL
    cur.close()
    return districts

def get_appointments(districts, slack_subscriptions):
    today = date.today()
    today_str = today.strftime("%d-%m-%Y")

    appointments_url = api_base_url + "/v2/appointment/sessions/public/calendarByDistrict"


    for (district_id, district_name, state_id, state_name) in districts:
        print("Fetching appointments for district_id: {} district_name: {} state_id: {} state_name: {}".format(
            district_id, district_name, state_id, state_name
        ))

        response = requests.get(appointments_url, params = {
            'district_id': district_id,
            'date': today_str
        })
        if response:
            district_sessions = []
            centers = response.json()['centers']
            for center in centers:
                sessions = center['sessions']
                for session in sessions:
                    min_age_limit = session['min_age_limit']
                    available_capacity = session['available_capacity']
                    if min_age_limit is not None and min_age_limit < 45 and available_capacity is not None and available_capacity > 0:
                        center_id = center['center_id']
                        center_name = center['name']
                        pincode = center['pincode']
                        fee_type = center['fee_type']
                        session_id = session['session_id']
                        session_date_str = session['date']
                        dt = datetime.strptime(session_date_str, '%d-%m-%Y')
                        session_date = dt.strftime('%Y-%m-%d')
                        vaccine = session['vaccine']
                        district_sessions.append((center_id, center_name, pincode, fee_type, session_id, session_date, vaccine, available_capacity, min_age_limit))

            cur = conn.cursor()
            cur.execute(appointments_district_query, [district_id])
            old_appointments = cur.fetchall()
            num_old_appointments = len(old_appointments)
            if num_old_appointments > 0:
                print("Deleting {} old appointments for {} {}, {}".format(num_old_appointments, district_id, district_name, state_name))
                cur.execute(delete_appointments_district, [district_id])
                conn.commit()

            old_session_ids = set()
            for old_appointment in old_appointments:
                old_session_ids.add(old_appointment[0])

            if len(district_sessions) > 0:
                new_session_ids = set()
                print("Found {} sessions in district {} {}, {}".format(len(district_sessions), district_id, district_name, state_name))
                cur = conn.cursor()
                new_sessions = False
                sessions = []
                for (center_id, center_name, pincode, fee_type, session_id, session_date, vaccine, available_capacity, min_age_limit) in district_sessions:
                
                    insert_session_record = (session_id, district_id, center_id, center_name, pincode, vaccine, fee_type, session_date, available_capacity, min_age_limit)
                    cur.execute(insert_session_query, insert_session_record)
                    new_session = False
                    if session_id not in old_session_ids:
                        new_session_ids.add(session_id)
                        new_session = True
                        new_sessions = True
                    new_str = ""
                    if new_session:
                        new_str = " NEW!!!"
                    print("\t{} pin: {} {}({}) {} slots: {} min_age: {}{}".format(center_name, pincode, vaccine, fee_type, session_date, available_capacity, min_age_limit, new_str))
                    sessions.append((center_name, pincode, vaccine, fee_type, session_date, available_capacity, min_age_limit, new_session))
                cur.close()
                conn.commit()
                if new_sessions:
                    send_alerts(slack_subscriptions, district_id, district_name, state_name, sessions)
        else:
            print("Failed to get appointments from API for district_id: {} name: {}. Response code: {}".format(district_id, district_name, response.status_code))

def send_alerts(slack_subscriptions, district_id, district_name, state_name, sessions):
    for (subscription_id, name, email, sub_district_id, webhook) in slack_subscriptions:
        if district_id == sub_district_id:
            send_slack_alert(webhook, district_id, district_name, state_name, sessions)
            print("Sent slack alerts to subscription_id: {} name: {} email: {} for {}, {}".format(subscription_id, name, email, district_id, state_name))

def send_slack_alert(webhook, district_id, district_name, state_name, sessions):
    title = "<!channel> Found new 18+ appointments in {}, {}".format(district_name, state_name)
    requests.post(webhook, json={
        "username": "18+ Vaccine Alert!",
        "icon_emoji": ":hospital:",
        "text": title,
        "attachments": build_attachments(district_id, district_name, state_name, sessions)
    })
    return

def build_attachments(district_id, district_name, state_name, sessions):
    attachments = []
    blocks = []
    for (center_name, pincode, vaccine, fee_type, session_date, available_capacity, min_age_limit, new_session) in sessions:
        txt = "\t{} pin: {} {} {} slots: {} ({})".format(center_name, pincode, vaccine, session_date, available_capacity, fee_type)
        if new_session:
            txt = "*" + txt + "*"

        block = {}
        block["type"] = "section"
        block["text"] = {
            "type": "mrkdwn",
            "text": txt
        }
        blocks.append(block)
    attachments.append({
        "blocks": blocks
    })
    return attachments



def load_subscriptions():
    cur = conn.cursor()
    cur.execute(subscriptions_query)
    
    subscriptions = cur.fetchall()
    conn.commit()

    print("Found {} subscriptions".format(len(subscriptions)))
    return subscriptions
    
if __name__ == "__main__":
    main()