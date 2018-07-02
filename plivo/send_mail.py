import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plivo.product_managers import managers

# Authenticating Gmail
home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
credential_path = os.path.join(credential_dir, 'plivo_auth.json')
with open(credential_path) as file:
    credentials = json.loads(file.read())
username, password = credentials['gmail_id'], credentials['gmail_password']


def get_contacts(product):
    """
    Return two lists names, emails containing names and email addresses
    reads from a file (module) plivo.product_managers
    """
    data = managers[product]

    names, emails = [item.split(',')[0].strip() for item in data], [item.split(',')[1].strip() for item in data]

    return names, emails


def send_mail(**kwargs):
    # set up the SMTP server

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)

    s.ehlo()
    s.starttls()
    s.login(username, password)
    user = kwargs.get('user', 'admin')
    tp = kwargs.get('tp')
    tc = kwargs.get('tc')
    tc_name = str(tc)
    tc_id = tc.case_id
    tp_name = str(tp)
    tp_id = tp.plan_id
    product = str(tp.product)
    url = tp.get_full_url() + "#reviewcases"

    names, emails = get_contacts(product.lower())  # read contacts

    # For each contact, send the email:
    for name, email in zip(names, emails):
        if not (name and email):
            continue
        msg = MIMEMultipart()  # create a message
        message = """Hi %s,
        A new Test Case has been created for the  Review.
        Test Case Name = %s
        Test Case id = %s
        Test Plan name = %s 
        Test Plan id = %s
        Product = %s
        Url for review cases = %s
        
        Sent from : %s""" % (name,tc_name,tc_id,tp_name,tp_id,product,url,user)

        # setup the parameters of the message
        msg['From'] = username
        msg['To'] = email
        msg['Subject'] = "Plivo TCMS Auto Generated Mail."

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.

        s.sendmail(username, email,str(msg))
        print('Mail Successfully sent to ', email)

    s.close()

    # Terminate the SMTP session and close the connection


if __name__ == '__main__':
    send_mail(tc='tc')