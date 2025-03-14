# Terms & Conditions Change Detection System

Monitor changes to Terms & Conditions across multiple websites. Get alerts via email, Asana tasks, and Google Drive backups when changes are detected.

## Features

- 🚨 **Real-time Monitoring**: Track multiple legal documents simultaneously
- 📨 **Multi-channel Alerts**: Email notifications + Asana task creation
- ☁️ **Cloud Backup**: Automatic PDF snapshots to Google Drive
- 🤖 **Webhook Integration**: Customizable POST endpoint for system integrations
- ⏰ **Scheduled Checks**: 24-hour monitoring cycle

## Installation

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/terms-change-detector.git
cd terms-change-detector
```
2. **Install Dependencies**
```bash
pip install -r requirements.txt
```
3. **System Dependencies**
```bash
# For PDF generation (Linux)
sudo apt-get install wkhtmltopdf
```

## Configuration

1. **Create config.txt**
```ini
API_TOKEN=your_thieves_api_token
WEBHOOK_URL=http://your-domain.com/webhook
COMPLIANCE_EMAIL=compliance@yourcompany.com
BASE_URL=https://negativestarinnovators.com/api/v1
ASANA_API_KEY=your_asana_key
ASANA_PROECT_ID=123456789
ASANA_SECTION_ID=987654321
ASANA_ASSIGNEE_ID=11223344
GOOGLE_DRIVE_CREDENTIALS_FILE=service-account.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
COMPLIANCE_EMAIL_ALERT_METHOD_ID=55
COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=66
```
2. **Obtain Credentials**
[Thieves API](https://negativestarinnovators.com/documentation/rest_api.html)
[Asana API Key](https://developers.asana.com/docs)
[Google Service Account](https://cloud.google.com/iam/docs/service-accounts)


## Usage
```bash
python main.py
```

The webhook server will start at http://localhost:5000

## Workflow Example
1. Tracker created for target URL
2. System checks page every 24 hours
3. On detected change:
Updates tracking condition
Creates Asana task with due date
Saves PDF snapshot to Drive
Sends email alert
