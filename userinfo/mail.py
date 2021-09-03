import smtplib, ssl
from email.message import EmailMessage
from smtplib import SMTP
import userinfo.config as config
import logging, time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

def connect_smtp():
    connection = smtplib.SMTP(  config.get('email', 'smtp_server'), 
                                config.get('email', 'smtp_port')
                            )
    if config.get('email', 'smtp_server') == 'smtp.uq.edu.au':
        context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.set_ciphers('DEFAULT@SECLEVEL=1')
    connection.ehlo()
    if config.get('email', 'smtp_server') == 'smtp.uq.edu.au':
        connection.starttls(context=context)
    else:
        connection.starttls()
    connection.ehlo()
    connection.login(config.get('email', 'username'), config.get('email', 'password'))
    return connection


def send_email(from_address, to_address, ccemail, subject, contents, subtype):
    """
    Send email
    """
    ### create connectoin first
    ### try 3 times
    connected = False
    attempts = 0
    while not connected:
        attempts = attempts + 1
        try:
            connection = connect_smtp()
            connected = True
        except Exception as e:
            logger.error(f"Problem with create smtp connection: {str(e)}")
            if attempts < 3:
                logger.debug("Try connecting to smtp server again...")
                time.sleep(3)
            else:
                raise
    ### send the email
    try:
        email = EmailMessage()
        email['Subject'] = subject
        email['From'] = from_address
        email['To'] = to_address
        if ccemail.strip() != "":
            logger.info(f"Cc to {ccemail}")
            email['Cc'] = ccemail
        email.set_content(contents, subtype=subtype)
        connection.send_message(email)
    finally:
        # close connection
        connection.close()

def send_mail(to_address, subject, contents, subtype='html', ccemail=''):
    """
    Send email
    """
    from_address = config.get('email', 'username')
    send_email(from_address, to_address, ccemail, subject, contents, subtype)


def send_email_with_file(from_address, to_address, ccemail, subject, contents, filecontents, filename):
    """
    Send email
    """
    ### create connectoin first
    ### try 3 times
    connected = False
    attempts = 0
    while not connected:
        attempts = attempts + 1
        try:
            connection = connect_smtp()
            connected = True
        except Exception as e:
            logger.error(f"Problem with create smtp connection: {str(e)}")
            if attempts < 3:
                logger.debug("Try connecting to smtp server again...")
                time.sleep(3)
            else:
                raise
    ### send the email
    try:
        email = MIMEMultipart()
        email['Subject'] = subject
        email['From'] = from_address
        email['To'] = to_address
        if ccemail.strip() != '':
            logger.info(f"Cc to {ccemail}")
            email['Cc'] = ccemail
        email.attach(MIMEText(contents, "html"))
        if filecontents:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(filecontents)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            email.attach(part)
        connection.send_message(email)
    finally:
        # close connection
        connection.close()

def send_mail_with_file(to_address, subject, contents, filecontents, filename, ccemail=""):
    """
    Send email
    """
    from_address = config.get('email', 'username')
    send_email_with_file(from_address, to_address, ccemail, subject, contents, filecontents, filename)


def main(argv):
    """
    main method
    """
    you = "xxx"
    contents = """
    <html>
        <head></head>
        <body>
            <p>Hi!<br>
            These are the following samples need to be fixed:<br>
                 <ul>
                    <li>sample 1</li>
                    <li>sample 2</li>
                    <li>sample 3</li>
                </ul> 
            </p>
        </body>
        </html>
    """
    send_mail(you, 'This is another test', contents)
if __name__ == '__main__':
    main([])    
