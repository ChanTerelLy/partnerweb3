import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
def assign_mail_ticket(text):
    sender_email = os.getenv('sender_email')
    password = os.getenv('email_password')
    text = json.loads(text.decode('utf-8'))
    message = MIMEMultipart("alternative")
    message["Subject"] = "Назначение заявки в график"
    message["From"] = sender_email
    message["To"] = ', '.join(text['mail_to'])
    # Turn these into plain/html MIMEText objects
    telegramma = f'<html>' \
                 f'<p><b>Номер заявки: </b> {text["number"]} </p>' \
                 f'<p><b>Время: </b> {text["time"]} </p>' \
                 f'<p><b>Тариф: </b> {text["tariff"]} </p>' \
                 f'<p><b>Дополнительно к тарифу: </b> {text["tariff_menu"]} </p>' \
                 f'<p><b>Номер абонента: </b> {text["phone1"]} </p>' \
                 f'<p>Подъезд - {text["entrance"]}, Этаж - {text["floor"]}</p>' \
                 f'<p><b>Комментарий: </b> {text["comment"]} </p>' \
                 f'<p><b>Агент: </b> {text["agent"]} </p>' \
                 f'<br>' \
                 f'<p><b>Клиент: </b> {text["client_name"]} </p>' \
                 f'<p><b>Адрес: </b> {text["address"]} </p>' \
                 f'</html>'
    part2 = MIMEText(telegramma, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, text['mail_to'], message.as_string()
        )

def fraud_mail_ticket(text):
    sender_email = os.getenv('sender_email')
    password = os.getenv('email_password')
    message = MIMEMultipart("alternative")
    message["Subject"] = "Создать заявку"
    message["From"] = sender_email
    message["To"] = text['mail_to']
    # Turn these into plain/html MIMEText objects
    telegramma = f'<html>' \
                 f'<p><b>Клиент: </b> {text["client_name"]} </p>' \
                 f'<p><b>Номер телефона: </b> {text["phone"]} </p>' \
                 f'<p><b>Адрес: </b> {text["address"]} </p>' \
                 f'<p><b>Тариф: </b> {text["tariff"]} </p>' \
                 f'<p><b>Агент: </b> {text["agent"]} </p>' \
                 f'</html>'
    part2 = MIMEText(telegramma, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, text['mail_to'], message.as_string()
        )

def feedback_mail(text):
    sender_email = os.getenv('sender_email')
    password = os.getenv('email_password')
    message = MIMEMultipart("alternative")
    message["Subject"] = "Жалобы и предложения"
    message["From"] = sender_email
    message["To"] = 'zvezdolom1@gmail.com'
    # Turn these into plain/html MIMEText objects
    telegramma = f'{text}'
    part2 = MIMEText(telegramma, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, 'zvezdolom1@gmail.com', message.as_string()
        )
