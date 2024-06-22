import os
import smtplib
import ssl

from dotenv import load_dotenv

port = 465  # For SSL

# Specify the full path to your .env file
dotenv_path = '../.env'

# Load environment variables from .env file
load_dotenv(dotenv_path)

password = os.environ['EMAIL_PASSWORD']

# Create a secure SSL context
context = ssl.create_default_context()

sender_email = 'stefan.secrieru02@e-uvt.ro'


def send_email(receiver_email, message):
    try:
        return 0
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            message['To'] = receiver_email
            message['From'] = sender_email
            server.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        print(e)
        return -1
