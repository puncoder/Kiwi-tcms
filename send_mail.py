import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from gmail_auth import username,  password
import socket
from tcms_utils import get_auth_user
hostname = socket.gethostname()


def get_contacts():
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = []
    emails = []
    data = get_auth_user()

    for item in data:
        if item[-2] or item[-1]:
            names.append(item[1])
            emails.append(item[4])
    return names, emails


def main():

    names, emails = get_contacts()  # read contacts

    # set up the SMTP server

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)

    s.ehlo()
    s.starttls()
    s.login(username, password)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        if not (name and email):
            continue
        msg = MIMEMultipart()  # create a message
        message = 'Hi %s,\nThis is simple message for testing...\n\n\n\nSent from : %s' %(name, hostname)

        # setup the parameters of the message
        msg['From'] = username
        msg['To'] = email
        msg['Subject'] = "Plivo TCMS auto generated mail."

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.

        s.sendmail(username, email,str(msg))
        print('Mail Successfully sent to ', email)

    s.close()

    # Terminate the SMTP session and close the connection


if __name__ == '__main__':
    main()