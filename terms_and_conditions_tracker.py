import requests
from datetime import datetime, timedelta
import os
from flask import Flask, request, jsonify  # For webhook server
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pdfkit


def readConfig(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            config[name] = value
    return config


config = readConfig("/home/bear/Documents/Projects/AI/TrackerAITesting/Terms and Conditions Demo/config.txt")

# Thieves Configuration
API_TOKEN = config['API_TOKEN']
WEBHOOK_URL = config['WEBHOOK_URL']
COMPLIANCE_EMAIL = config['COMPLIANCE_EMAIL']
BASE_URL = config['BASE_URL']
COMPLIANCE_EMAIL_ALERT_METHOD_ID=config['COMPLIANCE_EMAIL_ALERT_METHOD_ID']
COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=config['COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID']

# Asana Configuration
ASANA_API_KEY = config['ASANA_API_KEY']
ASANA_PROECT_ID = config['ASANA_PROECT_ID']
ASANA_SECTION_ID = config['ASANA_SECTION_ID']
ASANA_ASSIGNEE_ID = config['ASANA_ASSIGNEE_ID']


# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE = config['GOOGLE_DRIVE_CREDENTIALS_FILE']
GOOGLE_DRIVE_FOLDER_ID = config['GOOGLE_DRIVE_FOLDER_ID']


app = Flask(__name__)

def format_date(date_string):
    try:
        # Parse the date string into a datetime object
        dt_object = datetime.fromisoformat(date_string)

        # Format the datetime object to the desired format
        formatted_date = dt_object.strftime("%d %B %Y")

        return formatted_date
    except ValueError:
        # Handle the case where the input string is not a valid ISO 8601 date
        print(f"Error: Invalid date string: {date_string}")
        return None


def create_asana_task(taskContent, taskName):
    """Create task in Asana with section placement and assignment"""
    headers = {
        "Authorization": f"Bearer {ASANA_API_KEY}",
        "Content-Type": "application/json"
    }

    # Calculate due date 1 week from now
    due_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    task_data = {
        "data": {
            "name": taskName,
            "notes": taskContent,
            "projects": [ASANA_PROECT_ID],
            "memberships": [
                {
                    "project": ASANA_PROECT_ID,
                    "section": ASANA_SECTION_ID
                }
            ],
            "assignee": ASANA_ASSIGNEE_ID,
            "due_on": due_date  # Added due date field
        }
    }

    response = requests.post(
        "https://app.asana.com/api/1.0/tasks",
        json=task_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print(f"Created task in section 'Terms and Conditions Changes' assigned to Robert Smith")
    else:
        print(f"Asana API Error: {response.text}")
    
    return response.json()

def download_and_upload_to_drive(url, filename):
    try:
        output_pdf = f"{filename}.pdf"
        pdfkit.from_url(url, output_pdf)

        # Authenticate and build the Drive service
        creds = service_account.Credentials.from_service_account_file(GOOGLE_DRIVE_CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])
        service = build('drive', 'v3', credentials=creds)


        # Upload the PDF (or original HTML if conversion failed) to Google Drive
        file_metadata = {
            'name': os.path.basename(output_pdf), # Use the actual filename
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(output_pdf, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        print(f"File uploaded to Google Drive: {file.get('id')}")
        return file.get('id')


    except Exception as e:
        print(f"Error downloading or uploading to Drive: {e}")
        return None

    

def create_tracker(url, alert_method_ids, date, tracker_name):
    """Create a tracker for terms and conditions"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    tracker_data = {
        "name": tracker_name,
        "url": url,
        "running": True,
        "check_frequency": 1440,  # 24 hours in minutes
        "condition": f"the last updated date has changed since {date}",
        "alert_methods": alert_method_ids
    }
    
    response = requests.post(
        f"{BASE_URL}/create_tracker",
        json=tracker_data,
        headers=headers
    )
    
    return response.json()

def modify_tracker(tracker_id, new_condition, running):
    """Update tracker condition with new date"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    response = requests.post(
        f"{BASE_URL}/modify_tracker",
        json={
            "id": tracker_id,
            "condition": new_condition,
            "running":  running,
            "delayed_start": 1440*60 # in seconds. 24 hours.
        },
        headers=headers
    )
    
    return response.json()


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    print("Received webhook")
    """Handle incoming webhook notifications"""
    data = request.json

    print(f"data:{data}")

    new_condition = ""

    if data['result']:
        last_checked_date_string = format_date(data['checked_at'])
        print(f"last_checked_date_string:{last_checked_date_string}")
        new_condition = f"the last updated date has changed since {last_checked_date_string}"
        modify_tracker(data["tracker_id"], new_condition, True)
        create_asana_task("Determine if these changes require any action from our side", f"{data['tracker_name']} changed") 
        download_and_upload_to_drive(data['url'], f"{data['tracker_name']}-{last_checked_date_string}")
        
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    # Create trackers
    trackers = [
        {"url": "https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html", "date": "10 Jan 2025", "tracker_name": "Deepseek Terms of Use"},
        {"url": "https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html", "date": "10 Jan 2025", "tracker_name": "DeepSeek Privacy Policy"},
        {"url": "https://ai.google.dev/gemini-api/terms", "date": "10 Jan 2025", "tracker_name": "Gemini API Additional Terms of Service"},
        {"url": "https://www.llama.com/llama3_3/license/", "date": "10 Jan 2025", "tracker_name": "LLAMA 3.3 COMMUNITY LICENSE AGREEMENT"},
        {"url": "https://asana.com/terms/privacy-statement", "date": "10 Jan 2025", "tracker_name": "Asana Privacy Statement"},
        {"url": "https://www.docusign.com/legal/terms-and-conditions", "date": "10 Jan 2025", "tracker_name": "DOCUSIGN SITES & SERVICES TERMS AND CONDITIONS"},
        {"url": "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement", "date": "10 Jan 2025", "tracker_name": "GitHub General Privacy Statement"},
        {"url": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service", "date": "10 Jan 2025", "tracker_name": "GitHub Terms of Service"},
    ]
    
    for tracker in trackers:
        response = create_tracker(tracker["url"], [COMPLIANCE_EMAIL_ALERT_METHOD_ID, COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID], tracker["date"], tracker["tracker_name"])
        print(f"Created tracker for {tracker['url']}: {response}")
    
    # Start webhook server
    app.run(port=5000)