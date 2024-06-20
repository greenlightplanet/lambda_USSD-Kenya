'''
Parse the event received from Africa's Talking API.
Based on what is received in the "text", run the corresponding if-else statement.
If the user inputs 9. It takes back to the home page.
'''

from base64 import b64encode
import pymysql.cursors
import os
import requests
from requests.auth import HTTPBasicAuth
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import Constants
import datetime
import json
import logging
import StringUtil
import concurrent.futures
import threading
from skp_utils import get_agent_roles_from_skp_using_phone_number
import boto3
import urllib.parse
from props import allowed_roles
import time

logger = logging.getLogger(__name__)

def lambda_handler_with_vault(event, context):
    set_secret()
    return lambda_handler(event, context)

def lambda_handler(event, context):
    lambda_start_time = time.time()
    logger.info("Kenya lambda start time: %s", lambda_start_time)

    try:
        user = os.environ['DB_USER']
        password = os.environ['DB_PASSWORD']
        host = os.environ['DB_HOST']
        database = os.environ['DB']

        logger.info('Event: %s', event)
        data = event.get('data', {})
        phoneNumber = data.get('phoneNumber', '')
        sessionId = data.get('sessionId', '')
        text = data.get('text', '')

        if not phoneNumber.startswith('+'):
            phoneNumber = '+' + phoneNumber

        # Persist USSD flow data
        data_to_persist = {
            'phoneNo': phoneNumber,
            'sessionId': sessionId,
            'text': text,
            'country': 'KENYA'
        }

        connection_attributes = {
            'DB_USER': user,
            'DB_PASSWORD': password,
            'DB_HOST': host,
            'DB': database
        }

        persist_ussd_flow(connection_attributes, data_to_persist)

        # Handle USSD menu choices
        message = handle_menu_choice(text, phoneNumber, connection_attributes)

    except Exception as e:
        logger.error("Error in lambda_handler: %s", str(e))
        message = "END An error occurred. Please try again later."

    lambda_end_time = time.time()
    logger.info("Kenya lambda end time: %s", lambda_end_time)
    logger.info("Overall Kenya lambda performance time: %s", lambda_end_time - lambda_start_time)
    return message

def handle_menu_choice(text, phoneNumber, connection_attributes):
    welcome_message = "CON \nMy Sun King EasyBuy Services \n1. Emergency Module"

    if not text:
        return welcome_message

    steps = text.split('*')
    current_choice = steps[-1] if steps else ''

    try:
        if current_choice == '1' and len(steps) == 1:
            return "CON Enter Your Registered Mobile Number."
        elif previous_choice(steps, 1) == '1' and len(steps) == 2:
            registered_mobile = format_phone_number(current_choice)
            if not validate_phone_number(registered_mobile):
                return "END Invalid registered mobile number. It should be 9 digits long."
            angaza_id = fetch_angaza_id_from_phone(registered_mobile, connection_attributes)
            options = get_options_from_api(angaza_id)
            options_message = "CON Choose an option:\n" + "\n".join(f"{i+1}. {option}" for i, option in enumerate(options))
            return options_message
        elif previous_choice(steps, 2) == '1' and len(steps) == 3:
            return "CON Do you want to enter alternate contact number?\n1. Yes\n2. No"
        elif current_choice == '1' and previous_choice(steps, 3) == '1':
            return "CON Enter alternate phone number"
        elif previous_choice(steps, 4) == '1' and previous_choice(steps, 1) == '1':
            alternate_mobile = current_choice
            if not validate_alternate_phone_number(alternate_mobile):
                return "END Invalid alternate mobile number. It should be 9 digits long."
            registered_mobile = format_phone_number(previous_choice(steps, 3))
            if not validate_phone_number(registered_mobile):
                return "END Invalid registered mobile number. It should be 9 digits long."
            angaza_id = fetch_angaza_id_from_phone(registered_mobile, connection_attributes)
            options = get_options_from_api(angaza_id)
            selected_option = options[int(previous_choice(steps, 2)) - 1]
            success = post_emergency_request(registered_mobile, angaza_id, selected_option, alternate_mobile)
            if success:
                return "END Emergency request is received."
            else:
                return "END Failed to process emergency request."
        elif current_choice == '2' and previous_choice(steps, 3) == '1':
            registered_mobile = format_phone_number(previous_choice(steps, 2))
            if not validate_phone_number(registered_mobile):
                return "END Invalid registered mobile number. It should be 9 digits long."
            angaza_id = fetch_angaza_id_from_phone(registered_mobile, connection_attributes)
            options = get_options_from_api(angaza_id)
            selected_option = options[int(previous_choice(steps, 1)) - 1]
            success = post_emergency_request(registered_mobile, angaza_id, selected_option, None)
            if success:
                return "END Emergency request is received."
            else:
                return "END Failed to process emergency request."
        else:
            return "END Invalid input. Please try again."
    except Exception as e:
        logger.error("Error in handle_menu_choice: %s", str(e))
        return "END An error occurred while processing your request. Please try again later."

def format_phone_number(phone_number):
    if not phone_number.startswith('+254'):
        return '+254' + phone_number[-9:]
    return phone_number

def validate_phone_number(phone_number):
    return len(phone_number) == 13 and phone_number.startswith('+254')

def validate_alternate_phone_number(phone_number):
    return len(phone_number) == 9

def test_vault_lambda_handler(event, context):
    set_secret()
    print(os.environ)

def set_secret():
    print('reading secret')
    res = requests.get('https://admin.glpapps.com/glpadmin/vault_cache/')
    valut_secrets = res.json()
    for os_vars_key, os_vars_value in valut_secrets.items():
        os.environ[os_vars_key] = os_vars_value

    # resetting db credentials
    # os.environ['DB'] = os.environ['USSD_KENYA_DB']
    # os.environ['DB_HOST'] = os.environ['DB_HOST']
    # os.environ['DB_PASSWORD'] = os.environ['USSD_KENYA_DB_PASSWORD']
    # os.environ['DB_USER'] = os.environ['USSD_KENYA_DB_USER']
    # os.environ['DB_STAFF'] = os.environ['DB_STAFF']
    # os.environ['AUTH_USERNAME'] = os.environ['KENYA_ANGAZA_BASIC_AUTH_USERNAME']
    # os.environ['AUTH_PASSWORD'] = os.environ['KENYA_ANGAZA_BASIC_AUTH_PASSWORD']
    
    os.environ['DB'] = os.environ['USSD_NIGERIA_DB']
    os.environ['DB_HOST'] = os.environ['DB_HOST']
    os.environ['DB_PASSWORD'] = os.environ['USSD_NIGERIA_DB_PASSWORD']
    os.environ['DB_USER'] = os.environ['USSD_NIGERIA_DB_USER']
    os.environ['DB_STAFF'] = os.environ['DB_STAFF']
    os.environ['AUTH_USERNAME'] = os.environ['KENYA_ANGAZA_BASIC_AUTH_USERNAME']
    os.environ['AUTH_PASSWORD'] = os.environ['KENYA_ANGAZA_BASIC_AUTH_PASSWORD']
    print('secret set to env')

def fetch_angaza_id_from_phone(phoneNumber, connection_attributes):
    try:
        user = connection_attributes['DB_USER']
        password = connection_attributes['DB_PASSWORD']
        host = connection_attributes['DB_HOST']
        database = connection_attributes['DB']

        query = "SELECT angaza_id FROM kazi.users WHERE primary_phone = %s"

        conn = pymysql.connect(user=user, password=password, host=host, database=database)
        cursor = conn.cursor()
        cursor.execute(query, [phoneNumber])
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            logger.info("No angaza_id found for phone number: %s", phoneNumber)
            return ''

    except Exception as e:
        logger.error("Error in fetch_angaza_id_from_phone: %s", str(e))
        return ''

def get_options_from_api(angaza_id):
    try:
        url = f"https://kazi.glpapps.com/kazi/kazi-core/v1.0/emergency/{angaza_id}"
        response = requests.get(url)
        response.raise_for_status()

        response_data = response.json()
        options = response_data.get("ResponseData", {}).get("emergencyOptions", [])
        return options
    except Exception as e:
        logger.error("Error in get_options_from_api: %s", str(e))
        return []

def post_emergency_request(phone_number, angaza_id, selected_option, alternate_phone_number):
    try:
        url = f"https://kazi.glpapps.com/kazi/kazi-core/v1.0/emergency/{angaza_id}"
        payload = {
            "userId": angaza_id,
            "type": [selected_option],
            "alternateContactNumber": alternate_phone_number,
            "latitude": "",
            "longitude": "",
            "accuracy": ""
        }
        print(payload)
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        logger.info("Emergency request successfully posted with payload: %s", payload)
        return True
    except Exception as e:
        logger.error("Error in post_emergency_request: %s", str(e))
        return False

def persist_ussd_flow(connection_attribute, data_to_persist):
    phoneNumber = str(data_to_persist['phoneNo'])
    sessionId = str(data_to_persist['sessionId'])
    text = str(data_to_persist['text'])
    country = str(data_to_persist['country'])

    user = connection_attribute['DB_USER']
    password = connection_attribute['DB_PASSWORD']
    host = connection_attribute['DB_HOST']
    database = connection_attribute['DB']

    query = 'INSERT INTO automation.ussd_requests(session_id, phone_number, text, country)  VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE text = VALUES(text);'
    try:
        connc = pymysql.connect(user=user, password=password, host=host, database=database)
        cursor = connc.cursor()
        response = cursor.execute(query, [sessionId, phoneNumber, text, country])
        connc.commit()
        connc.close()
        print(response)
    except Exception as e:
        logger.error("Exception Occured while persisting choices Exception : %s ", str(e))
        connc.close()


def retrive_current_choice(text):
    current_choice_finder_index = text.rfind('*')
    if current_choice_finder_index >= 0:
        text = text[current_choice_finder_index + 1:]
    return text


# def previous_choice(complete_text, level):
#     i = 0
#     choice = ''
#     if len(complete_text) == 1:
#         return choice
#     while i <= level:
#         choice_index = complete_text.rfind('*')
#         choice = complete_text[choice_index + 1:]
#         complete_text = complete_text[:choice_index]
#         i = i + 1
#     return choice
def previous_choice(steps, level):
    try:
        if len(steps) <= level:
            return ''
        return steps[-(level + 1)]
    except Exception as e:
        logger.error("Error in previous_choice: %s", str(e))
        return ''


def previous_whole_choices(text):
    index = text.rfind('*')
    return text[:index]