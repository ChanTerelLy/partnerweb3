import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

def send_mail_ticket(text):
    sender_email = "support@arh-beeline.ru"
    password = '123456QqQq'
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
    with smtplib.SMTP_SSL("smtp.beget.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, text['mail_to'], message.as_string()
        )