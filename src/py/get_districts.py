import requests
import json
import psycopg2
import time
from utils import get_db_connection

api_base_url = "https://cdn-api.co-vin.in/api"

conn = get_db_connection()

def main():
    start_t = time.time()

    print("Accessing API at {}".format(api_base_url))
    clear_db()
    states = get_states()['states']
    get_districts(states)
    conn.close()

    end_t = time.time()
    print("Time taken to get districts: {:.2f}s".format(end_t - start_t))


def clear_db():
    cur = conn.cursor()
        
	# execute a statement
    print('Clearing states in db')
    cur.execute('DELETE from public.states')
       
	# close the communication with the PostgreSQL
    cur.close()

def get_states():
    url = api_base_url + "/v2/admin/location/states"
    response = requests.get(url, headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Cache-Control': 'no-cache'
        })
    if response:
        states = response.json()            
        return states
    else:
        print("Failed to get states from API. Response code: {}".format(response.status_code))


def get_districts(states):
    cur = conn.cursor()
    
    for state in states:
        state_id = state['state_id']
        state_name = state['state_name']
        try:
            print("State id: {} name: {}".format(state_id, state_name))

            insert_query = """ INSERT INTO public.states (id, name) VALUES (%s,%s)"""
            record = (state_id, state_name)
            cur.execute(insert_query, record)

            districts_url = api_base_url + "/v2/admin/location/districts/{}".format(state_id)
            response = requests.get(districts_url, headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Cache-Control': 'no-cache'
            })
            if response:
                districts = response.json()['districts']
                for district in districts:
                    district_id = district['district_id']
                    district_name = district['district_name']
                    print("\tDistrict id: {} name: {}".format(district_id, district_name))

                    district_insert_query = """ INSERT INTO public.districts (id, name, state_id) VALUES (%s,%s,%s)"""
                    district_record = (district_id, district_name, state_id)
                    cur.execute(district_insert_query, district_record)

            else:
                print("Failed to get districts from API for state_id: {} name: {}. Response code: {}".format(state_id, state_name, response.status_code))

        
            conn.commit()
        except Exception as error:
            print("Error handling state id: {} name: {} error: {}".format(state_id, state_name, error))
            raise
            

    cur.close()

if __name__ == "__main__":
    main()