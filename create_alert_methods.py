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


def update_config_file(config_file, updates):
    """Update config file with new values while preserving structure"""
    # Read original file
    with open(config_file, 'r') as f:
        original_lines = f.readlines()

    # Apply updates
    updated_lines = []
    for line in original_lines:
        stripped_line = line.strip()
        if stripped_line and '=' in stripped_line:
            key, value = stripped_line.split('=', 1)
            key = key.strip()
            if key in updates:
                new_value = updates[key]
                updated_lines.append(f"{key}={new_value}\n")
                del updates[key]  # Remove handled key
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    # Write back to file
    with open(config_file, 'w') as f:
        f.writelines(updated_lines)


def create_alert_methods(name, type, contact_details):
    """Create email and webhook alert methods"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Create email alert
    alert_method = requests.post(
        f"{BASE_URL}/create_alert_method",
        json={
            "name": name,
            "method": type,
            "contact_info": contact_details
        },
        headers=headers
    ).json()
    
    return alert_method.get('new_alert_method_id')

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
            if alertMethod['method'] == 'Email' and alertMethod['name'] == "Compliance Email":
                alertMethodsResult['COMPLIANCE_EMAIL_ALERT_METHOD_ID'] = alertMethod['id']
            elif alertMethod['method'] == 'Webhook' and alertMethod['name'] == "Compliance Webhook":
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
    if not alert_methods.get('COMPLIANCE_EMAIL_ALERT_METHOD_ID'):
        complianceAlertMethodId = create_alert_methods("Compliance Email", "Email", COMPLIANCE_EMAIL)
        alert_methods['COMPLIANCE_EMAIL_ALERT_METHOD_ID'] = complianceAlertMethodId
    if not alert_methods.get('COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID'):
        complianceWebhookAlertMethodId = create_alert_methods("Compliance Webhook", "Webhook", WEBHOOK_URL)
        alert_methods['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID'] = complianceWebhookAlertMethodId

    # Print the alert method IDs
    print("Alert methods created/retrieved with alert method IDs.")
    print(f"COMPLIANCE_EMAIL_ALERT_METHOD_ID: {alert_methods['COMPLIANCE_EMAIL_ALERT_METHOD_ID']}")
    print(f"COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID: {alert_methods['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID']}")

    # Update the config.txt with the alert method IDs
    update_config_file(CONFIG_FILE, alert_methods)

    print("Updated Config File")

    

    
