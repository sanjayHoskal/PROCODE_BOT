import os
import base64
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load env vars
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")
load_dotenv(ENV_PATH)

# Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME", "Procode Bot")


def send_proposal_email(pdf_path: str, recipient_email):
    """
    Sends the proposal PDF to one or multiple users via Brevo (Sendinblue).

    Args:
        pdf_path (str): Path to the generated PDF.
        recipient_email (str or list): Single email string or a list of emails.

    Returns:
        dict: API response or error status.
    """

    # Validate API key
    if not BREVO_API_KEY or not SENDER_EMAIL:
        return {"status": "error", "message": "Missing API keys or sender email in .env"}

    # Normalize email input (single or multiple)
    if isinstance(recipient_email, str):
        recipient_list = [recipient_email]
    elif isinstance(recipient_email, list):
        recipient_list = recipient_email
    else:
        return {"status": "error", "message": "recipient_email must be a string or a list"}

    print(f"Preparing to send email to: {recipient_list}")

    # Configure API client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # Prepare attachment
    try:
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
            encoded_content = base64.b64encode(pdf_content).decode("utf-8")

        filename = os.path.basename(pdf_path)

    except FileNotFoundError:
        return {"status": "error", "message": f'File "{pdf_path}" not found.'}

    # Construct email object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email} for email in recipient_list],
        sender={"name": SENDER_NAME, "email": SENDER_EMAIL},
        subject="Your Custom Project Proposal - ProCode Bot",
        html_content="""
            <html>
                <body>
                    <h2>Hello!</h2>
                    <p>Please find attached the project proposal generated based on your requirements.</p>
                    <p>Best regards,<br>ProCode Team</p>
                </body>
            </html>
        """,
        attachment=[
            {
                "content": encoded_content,
                "name": filename
            }
        ],
    )

    # Send email via Brevo
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent successfully! Message ID: {api_response.message_id}")

        return {"status": "success", "message_id": api_response.message_id}

    except ApiException as e:
        print(f"Error sending email: {e}")
        return {"status": "error", "message": str(e)}


# --- Test Block ---
if __name__ == "__main__":
    # Create a dummy file for testing
    test_pdf = os.path.join(BASE_DIR, "generated_proposals", "test_email.pdf")
    if not os.path.exists(test_pdf):
        os.makedirs(os.path.dirname(test_pdf), exist_ok=True)
        with open(test_pdf, "w") as f:
            f.write("Dummy PDF Content")

    # Test with multiple emails
    test_emails = ["sanjuhoskal@gmail.com", "sachinsachu9590@gmail.com"]

    send_proposal_email(test_pdf, test_emails)
