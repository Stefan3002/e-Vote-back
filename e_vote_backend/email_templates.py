from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

otp_message = MIMEMultipart("alternative")
otp_message["Subject"] = "voteGuardian - Log in request"


def format_otp_email(username, otp_value, content=''):
    html = f"""\
    <html>
      <body>
        <p>
        Hi, <b>{username}</b> <br />
        We just received a request to log in to your voteGuardian account. <br />
        Here is the one-time code generated for you: {otp_value} <br />
        </p>
        <p>
        If you <strong>did not request to log-in</strong>, please click <a href="">here</a> to automatically inform us. <br />
        </p>
        <p>
        {content}
        </p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    otp_message.attach(part)
