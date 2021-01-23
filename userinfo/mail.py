import smtplib, ssl
from email.message import EmailMessage
from smtplib import SMTP
import userinfo.config as config
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)s] %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

# create connection
try:
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
    connection.login(config.get('email', 'username'), 
                    config.get('email', 'password'))
except Exception as e:
    logger.error("Problem with creat smtp connection: " + str(e))
    exit(1)


def close_connection():
    connection.close()

def send_mail(to_address, subject, contents, subtype='html'):
    """
    Send email
    """
    email = EmailMessage()
    email['Subject'] = subject
    email['From'] = config.get('email', 'username')
    email['To'] = to_address
    email.set_content(contents, subtype=subtype)
    connection.send_message(email)


def main(argv):
    """
    main method
    """
    you = "xxxxxx"
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
    send_smtp_mail(you, 'This is another test', contents)
if __name__ == '__main__':
    main([])    
