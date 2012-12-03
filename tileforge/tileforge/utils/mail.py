# -*- coding: utf-8 -*-

import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from email.header import Header

def send_email(sender, to, subject, body_text, files=[], server="localhost", port=25):
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(body_text, _subtype='plain', _charset='utf-8'))
    
    for filename in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(filename,"rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))
        msg.attach(part)
    try:
        smtp = smtplib.SMTP(server, port)
        smtp.sendmail(sender, msg['To'].split(","), msg.as_string())
        smtp.quit()
    except Exception, exception:
        print "failed to send email: %s" % exception

if __name__ == "__main__":
    send_email(to=["stephane.brunner@camptocamp.com"], sender="test@example.com",
            subject="a test from tileforge/mail.py, test éàè",
            body_text="hello world ! été", files=['README.txt'])
    send_email(to=["courriel@stephane-brunner.ch"], sender="test@example.com",
            subject="a test from tileforge/mail.py, test éàè",
            body_text="hello world ! été")
    print "done"
