import smtplib
from email.mime.text import MIMEText
from services.mails import get_all_emailss
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from Utilities.mail_utilities import config,EmailRequest


'''def send_email_to_users(publication_name):
    # Replace with actual user email retrieval logic
    
    user_emails = get_all_emailss()  # Fetch user emails from Firestore or another source

    if not user_emails:
        raise ValueError("No users found to send emails")

    sender_email = "harshadkokkiniti@gmail.com"
    sender_password = "Harshad@786"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    subject = f"New Publication: {publication_name}"
    body = (
            f"Hello,\n\nA new publication '{publication_name}' has been added.\n"
            f"You can access it here: {publication_name}\n\nBest regards,\nThe Team")

    # Email sending logic
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        for email in user_emails:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = email
            server.sendmail(sender_email, email, msg.as_string()) '''



conf = config(
    MAIL_USERNAME="harshadkokkinti@gmail.com",
    MAIL_PASSWORD="rzxc hbei uirf jfze",
    MAIL_FROM="harshadkokkiniti@gmail.com",
    MAIL_FROM_NAME="De-Lit",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="",
)


mail_conf = ConnectionConfig(
    MAIL_USERNAME=conf.MAIL_USERNAME,
    MAIL_PASSWORD=conf.MAIL_PASSWORD,
    MAIL_FROM=conf.MAIL_FROM,
    MAIL_FROM_NAME=conf.MAIL_FROM_NAME,
    MAIL_PORT=conf.MAIL_PORT,
    MAIL_SERVER=conf.MAIL_SERVER,
    MAIL_STARTTLS=conf.MAIL_TLS,
    MAIL_SSL_TLS=conf.MAIL_SSL,
    USE_CREDENTIALS=conf.USE_CREDENTIALS,
    TEMPLATE_FOLDER=conf.TEMPLATE_FOLDER,
)


fast_mail = FastMail(mail_conf)

def plain_mail(email_request: EmailRequest):
    try:
        message = MessageSchema(
            subject=email_request.subject,
            recipients=["arshadkokkiniti@gmail.com"],
            body=email_request.body,
            subtype="plain",
        )
        print(f"Sending email to: {email_request.recipients}")
        fast_mail.send_message(message)
        print("Mail sent successfully.")
    except Exception as e:
        print(f"Error while sending mail: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error while sending mail: {str(e)}"
        )



def send_email_to_users(publication_name):
    try:
        user_emails = get_all_emailss() # Fetch user emails from Firestore or another source
        email_list = [entry['email'] for entry in user_emails['emails']]
        if not email_list:
            raise ValueError("No users found to send emails")
        print(f"Fetched emails: {email_list}")
        

        subject = f"New Publication: {publication_name}"
        body = (
            f"Hello,\n\nA new publication '{publication_name}' has been added.\n"
            f"You can access it here: {publication_name}\n\nBest regards,\nThe Team")

        for email in email_list:
            message = EmailRequest(
                subject=subject,
                recipients=[email],  # Ensure the recipients is a list
                body=body
            )
            plain_mail(message)  # Call the function to send the email

        return {"status": "success", "message": "Emails sent successfully."}

    except Exception as e:
        return {"status": "error", "message": str(e)}

