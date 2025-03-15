import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify  # For webhook server
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CONFIG_FILE = 'config.txt'

def readConfig(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            config[name] = value
    return config


config = readConfig(CONFIG_FILE)

# Thieves Configuration
API_TOKEN = config['API_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']
COMPLIANCE_EMAIL = config['COMPLIANCE_EMAIL']
BASE_URL = config['BASE_URL']
COMPLIANCE_EMAIL_ALERT_METHOD_ID=config['COMPLIANCE_EMAIL_ALERT_METHOD_ID']
COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=config['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID']


def update_config_file(config_file, alert_methods):

    # 1. Read existing config file
    existing_config = {}
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    existing_config[key.strip()] = value.strip()
    except FileNotFoundError:
        # If file doesn't exist, that is an issue that should be known.
        raise FileNotFoundError(f"Configuration file not found: {config_file}")


    # 2. Update with alert methods (with suffix)
    for key, value in alert_methods.items():
        full_key = key + "_ALERT_METHOD_ID"
        if full_key in existing_config:  # Only update if the key exists in the config
            existing_config[full_key] = value
        # else:  # Optional:  Log a warning if the key isn't found?
        #     print(f"Warning:  Key '{full_key}' not found in config file.")

    # 3. Write the updated configuration back to the file.
    #    Important: We need to preserve the *original order* of the file.
    with open(config_file, 'w') as f:
        with open(config_file, 'r') as original_file:
             for original_line in original_file:
                original_line = original_line.strip()
                if original_line and "=" in original_line:
                  original_key = original_line.split("=",1)[0].strip()
                  updated_value = existing_config.get(original_key,"")
                  f.write(f"{original_key}={updated_value}\n")
                else: #handles blank lines and comments from the original config file.
                   f.write(original_line + "\n")


def create_alert_methods(name, type, contact_details):
    """Create email and webhook alert methods"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Create email alert
    alert_method = requests.post(
        f"{BASE_URL}/create_alert_method",
        json={
            "name": name,
            "type": type,
            "contact_details": contact_details
        },
        headers=headers
    ).json()
    
    return alert_method.get('new_alert_method_id'),

def get_alert_methods_url():
    """Create email and webhook alert methods"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Create email alert
    alert_methods_respose = requests.post(
        f"{BASE_URL}/get_alert_methods",
        json={
            
        },
        headers=headers
    ).json()

    print(f"alert_methods_respose:{alert_methods_respose}")

    alertMethodsResult = {}

    if alert_methods_respose.get('success'):
        for alertMethod in alert_methods_respose['alert_methods']:
            if alertMethod['type'] == 'Email' and alertMethod['name'] == "Compliance Email":
                alertMethodsResult['COMPLIANCE_EMAIL_ALERT_METHOD_ID'] = alertMethod['id']
            elif alertMethod['type'] == 'Webhook' and alertMethod['name'] == "Compliance Webhook":
                alertMethodsResult['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID'] = alertMethod['id']

    return alertMethodsResult


if __name__ == "__main__":
    # Check if these values are already entered in config.txt. If want to replace these values then delete the value in config.txt but keep the key=
    if COMPLIANCE_EMAIL_ALERT_METHOD_ID != "" and COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID != "":
        print("Alert methods already exist. Skipping retrieval and creation. You can run terms_and_conditions_tracker.py. If want to replace these values then delete the value in config.txt but keep the key=")
        exit(0)

    # First check that there are alert methods existing. 
    alert_methods = get_alert_methods_url()

    # If there are no alert methods, create them. Ensure that your webhook (WEBHOOK_URL) and email address (COMPLIANCE_EMAIL) are set in the config.txt
    # If Compliance Email was created you must verify the email address before you are allowed to use it
    if not alert_methods[COMPLIANCE_EMAIL_ALERT_METHOD_ID]:
        complianceAlertMethodId = create_alert_methods("Compliance Email", "Email", COMPLIANCE_EMAIL_ALERT_METHOD_ID)
        alert_methods['COMPLIANCE_EMAIL_ALERT_METHOD_ID'] = complianceAlertMethodId
    if not alert_methods[COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID]:
        complianceWebhookAlertMethodId = create_alert_methods("Compliance Webhook", "Webhook", WEBHOOK_URL)
        alert_methods['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID'] = complianceWebhookAlertMethodId

    # Update the config.txt with the alert method IDs
    update_config_file(CONFIG_FILE, alert_methods)

    # Print the alert method IDs
    print("Alert methods created/retrieved and config.txt updated with alert method IDs.")
    print(f"COMPLIANCE_EMAIL_ALERT_METHOD_ID: {alert_methods['COMPLIANCE_EMAIL_ALERT_METHOD_ID']}")
    print(f"COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID: {alert_methods['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID']}")

    
