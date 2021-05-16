import requests
import json
import time
from datetime import datetime
from datetime import date
import pytz
import os

api_base_url = "https://cdn-api.co-vin.in/api"

def main():
    start_t = time.time()

    otp_url = api_base_url + "/v2/auth/public/generateOTP"

    mobile = os.environ.get('MOBILE', '1234567890')
    print("Generating OTP for number: {} at {}".format(mobile, datetime.now(pytz.timezone('Asia/Kolkata'))))

    response = requests.post(otp_url, json = {
        'mobile': mobile
    }, headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Cache-Control': 'no-cache'
    })
    if response:
        print("OTP generate sucessfully for number: {} \n{}".format(mobile, response.json()))
    else:
        print("Failed to generate OTP for number: {} Response code: {}".format(mobile, response.status_code))
        print("Reponse text: {}".format(response.content))

if __name__ == "__main__":
    main()
