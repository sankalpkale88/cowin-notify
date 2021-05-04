import argparse
import requests
import json
import sys
import time
from datetime import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from playsound import playsound


port = 587  # For SSL
smtp_server = "smtp.gmail.com"
baseURL = "https://cdn-api.co-vin.in/api"
calendarByPinURLFormat = "/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}"
calendarByDistrictURLFormat = "/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}"
listStatesURLFormat = "/v2/admin/location/states"
listDistrictsURLFormat = "/v2/admin/location/districts/{0}"
state_id = None
district_id = None
reciever_email = None
driver = None

def get_available_slots(slots, age):
    centers_slots = slots['centers']
    available_slots = []
    for center in centers_slots:
        sessions = center["sessions"]
        for session in sessions:
            if session['available_capacity'] > 0 and session['min_age_limit'] <= int(age):
                available_slot = {}
                available_slot['name']=center['name']
                available_slot['state_name'] = center['state_name']
                available_slot['district_name'] = center['district_name']
                available_slot['pincode'] = center['pincode']
                available_slot['date'] = session['date']
                available_slot['available_capacity'] = session['available_capacity']
                available_slots.append(available_slot)
    return available_slots


def serach_by_pincode(pincode , age):
    current_date = datetime.today().strftime('%d-%m-%Y')
    url = baseURL + calendarByPinURLFormat.format(pincode,current_date)
    response = requests.request("GET", url)
    if response.status_code == 200:
        slots = json.loads(response.text)
        #print(slots)
        available_slots = get_available_slots(slots,age)
        return available_slots
    else:
        raise Exception("Error: Unexpected response {0}".format(response))


def get_state_id(state_name):
    global state_id
    if state_id:
        return state_id
    url = baseURL + listStatesURLFormat
    response = requests.request("GET", url)
    if response.status_code == 200:
        states_json  = json.loads(response.text)
        states = states_json['states']
        for state in states:
            if str(state['state_name']).lower() == state_name.lower():
                state_id = state['state_id']
                return
        raise Exception('Invalid state name')
    else:
        raise Exception("Error: Unexpected response {0}".format(response))


def get_districit_id(state_id , district_name):
    global district_id
    if district_id:
        return district_id
    url = baseURL + listDistrictsURLFormat.format(state_id)
    response = requests.request("GET", url)
    if response.status_code == 200:
        district_json = json.loads(response.text)
        for district in district_json['districts']:
            if district['district_name'].lower() == district_name.lower():
                district_id = district['district_id']
                return
        valid_districts = []
        for district in district_json['districts']:
            valid_districts.append(district['district_name'])
        raise Exception('Invalid district name name , valid districts are ' + str(valid_districts))
    else:
        raise Exception("Error: Unexpected response {0}".format(response))


def serach_by_district(district_id, age):
    current_date = datetime.today().strftime('%d-%m-%Y')
    url = baseURL + calendarByDistrictURLFormat.format(district_id, current_date)
    response = requests.request("GET", url)
    if response.status_code == 200:
        slots = json.loads(response.text)
        # print(slots)
        available_slots = get_available_slots(slots, age)
        return available_slots
    else:
        raise Exception("Error: Unexpected response {0}".format(response))


def send_notification(email_id,password, slots):
    print("Slots are available sending email notification ")
    for slot in slots:
        print(str(slot))

    message = MIMEMultipart()
    message['From'] = email_id
    message['To'] = email_id
    message['Subject'] = 'Vaccination Slot'
    message_text = ""
    for slot in slots:
        message_text = message_text + str(slot) + "\n"
    message.attach(MIMEText(message_text, 'plain'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_id, password)
        server.sendmail(email_id, email_id, message.as_string())
        print("Email sent!!")

def play_sound(slots, sound_mp3):
    print(slots)
    playsound(sound_mp3)


def search_slot(args):
    while(True):
        if args.pincode:
            slots = serach_by_pincode(args.pincode, args.age)
        if args.state:
            get_state_id(args.state)
            get_districit_id(state_id,args.district)
            slots = serach_by_district(district_id,args.age)

        if slots:
            if args.playsound:
                play_sound(slots,args.playsound)
            else:
                send_notification(args.email,args.password, slots)
        else:
            print("No Slots available retrying after 5 sec")
            time.sleep(5)

def parse(args):
    parser = argparse.ArgumentParser(description="script to send cowin availbility alert",prog="cowin")
    parser.add_argument("--state", help="state",required=False, action="store")
    parser.add_argument("--district", help="state", required=False, action="store")
    parser.add_argument("--pincode", help="state", required=False, action="store")
    parser.add_argument("--age", help="state", required=True, action="store")
    parser.add_argument("--playsound", help="path of mp3 file", required=False, action="store")
    parser.add_argument("--email", help="state", required=False, action="store")
    parser.add_argument("--password", help="state", required=False, action="store")
    return parser.parse_args(args)



if __name__ == '__main__':
    args = parse(sys.argv[1:])
    search_slot(args)
