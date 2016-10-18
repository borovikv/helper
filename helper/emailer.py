import smtplib
from email.mime.text import MIMEText

from helper import settings

COMMASPACE = ', '


def send_email(subject, text, me=settings.MY_EMAIL, to=None):
    msg = MIMEText(text, 'html')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = COMMASPACE.join(to or [me])
    with smtplib.SMTP('mail.yopeso.com') as s:
        s.ehlo()
        s.starttls()
        s.login(settings.MY_EMAIL, settings.MY_EMAIL_PASSWORD)
        s.sendmail(me, to, msg.as_string())
