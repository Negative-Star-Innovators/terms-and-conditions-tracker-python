# Terms & Conditions Change Detection System

Monitor changes to Terms & Conditions across multiple websites. Get alerts via email, Asana tasks, and Google Drive backups when changes are detected.

## Features

- 🚨 **Real-time Monitoring**: Tracks multiple legal documents simultaneously.
- 📨 **Multi-channel Alerts**: Email notifications and Asana task creation.
- ☁️ **Cloud Backup**: Automatic PDF snapshots to Google Drive.
- 🤖 **Webhook Integration**: Customizable POST endpoint for system integrations.
- ⏰ **Scheduled Checks**:  Configurable monitoring intervals (default: 24 hours).

## Installation

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/Negative-Star-Innovators/terms-and-conditions-tracker-python.git
    cd terms-change-detector
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **System Dependencies (for PDF generation on Linux):**
    ```bash
    sudo apt-get update  # Important: Update package lists first
    sudo apt-get install -y wkhtmltopdf  # The -y flag automatically answers yes to prompts
    ```

## Configuration

1.  **Create `config.txt`:**

    Enter the requried values in the file named `config.txt` which is located at the root directory of the project.  This file will store your sensitive configuration values. It will look like this

    ```ini
    API_TOKEN=your_thieves_api_token
    WEBHOOK_URL=https://your-domain.com/webhook  # Or a service like ngrok for local testing
    COMPLIANCE_EMAIL=compliance@yourcompany.com  # You will meed to accept the verification email after this is created before using this email
    BASE_URL=https://negativestarinnovators.com/api/v1
    ASANA_API_KEY=your_asana_key
    ASANA_PROECT_ID=your_asana_project_id
    ASANA_SECTION_ID=your_asana_section_id
    ASANA_ASSIGNEE_ID=your_asana_assignee_id
    GOOGLE_DRIVE_CREDENTIALS_FILE=service-account.json  # Path to your Google service account credentials file
    GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
    COMPLIANCE_EMAIL_ALERT_METHOD_ID=  # Leave this blank initially
    COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=  # Leave this blank initially
    ```

2.  **Obtain Credentials:**

    *   **Thieves API Token:** Obtain your API token from the [Thieves API documentation](https://negativestarinnovators.com/documentation/rest_api.html).
    *   **Asana API Key:** Generate an Asana Personal Access Token (PAT) from the [Asana Developer Console](https://developers.asana.com/docs).
    *   **Google Service Account:** Create a Google Cloud service account and download its credentials file (`service-account.json`).  Follow the instructions in the [Google Cloud documentation](https://cloud.google.com/iam/docs/service-accounts).  You'll need to enable the Google Drive API for this service account.
    *   **Webhook URL:**  This is the URL where the system will send POST requests when changes are detected.
        *   For local testing, you can use a tool like [ngrok](https://ngrok.com/) to expose your local Flask server to the internet.  Run `ngrok http 5000` (assuming your Flask app runs on port 5000) and use the provided ngrok URL as your `WEBHOOK_URL`.
        *   For production, you'll need a publicly accessible server and domain name.

3.  **Set Up Alert Methods and Get IDs (Important!):**

    The `COMPLIANCE_EMAIL_ALERT_METHOD_ID` and `COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID` values are *not* manually obtained.  They are *automatically* generated by the `create_alert_methods.py` script.  Here's how to get them:

    *   **Ensure `config.txt` is Partially Filled:** Make sure you've filled in all the values in `config.txt` *except* for `COMPLIANCE_EMAIL_ALERT_METHOD_ID` and `COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID`.  Leave those two lines blank, like this:
        ```ini
        COMPLIANCE_EMAIL_ALERT_METHOD_ID=
        COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=
        ```
    *   **Run `create_alert_methods.py`:** Execute the script:
        ```bash
        python create_alert_methods.py
        ```
        *   This script will:
            1.  Check if the alert method IDs already exist in `config.txt`.
            2.  If they *don't* exist, it will:
                *   Use the `API_TOKEN`, `BASE_URL`, `COMPLIANCE_EMAIL`, and `WEBHOOK_URL` from your `config.txt` to create the alert methods via the Thieves API.
                *   Retrieve the newly generated IDs.
                *   *Automatically update* your `config.txt` file with the correct IDs.
            3.  If the IDs *do* already exist, the script will skip the creation process and exit.

    *   **Verify `config.txt`:** After running `create_alert_methods.py`, check your `config.txt` file.  It should now have the alert method IDs filled in:
        ```ini
        COMPLIANCE_EMAIL_ALERT_METHOD_ID=55  # Example ID
        COMPLIANCE_WEBHOOK_URL_ALERT_METHOD_ID=66  # Example ID
        ```

    * **Troubleshooting**:
        *  **Email Verification:** If you're setting up an email alert method for the first time, you *must* verify the `COMPLIANCE_EMAIL` address with the Thieves API. The script *will* create the email alert method, but it won't be usable until the email is verified. To verify simply click the accept button in the verification email sent to you once the email alert method is created.

## Usage

```bash
python terms_and_conditions_tracker.py