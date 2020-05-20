import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os


class EmailSender():
    def __init__(self):
        self.sender_email = os.getenv('sender_email')
        self.password = os.getenv('email_password')

    def email_helper(self, subject):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        return message

    def email_sender(self, message, telegramma, to='zvezdolom1@gmail.com'):
        part2 = MIMEText(telegramma, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(
                self.sender_email, to, message.as_string()
            )

    def assign_mail_ticket(self, text):
        message = self.email_helper('Назначение заявки в график')
        text = json.loads(text.decode('utf-8'))
        message["To"] = ', '.join(text['mail_to'])
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
        self.email_sender(message, telegramma, message['To'])

    def fraud_ticket(self, text):
        message = self.email_helper('Заявка с активным договором')
        message["To"] = text['mail_to']
        telegramma = f'<html>' \
                     f'<p><b>Назначить в график: </b> {text["assigned"]} </p>' \
                     f'<p><b>Время: </b> {text["datetime"]} </p>' \
                     f'<p><b>Тариф: </b> {text["tariff"]} </p>' \
                     f'<p><b>Номер абонента: </b> {text["phone"]} </p>' \
                     f'<p><b>Комментарий: </b> {text["comment"]} </p>' \
                     f'<p><b>Агент: </b> {text["agent"]} </p>' \
                     f'<br>' \
                     f'<p><b>Клиент: </b> {text["client_name"]} </p>' \
                     f'<p><b>Адрес: </b> {text["address"]} </p>' \
                     f'</html>'
        self.email_sender(message, telegramma, message['To'])

    def agent_assign_ticket(self, text):
        message = self.email_helper('Агент назначил заявку')
        message["To"] = text['mail_to']
        telegramma = f'<html>' \
                     f'<p><b>Номер заявки: </b> {text["number"]} </p>' \
                     f'<p><b>Ссылка: </b> {text["link"]} </p>' \
                     f'<p><b>Агент: </b> {text["operator"]} </p>' \
                     f'</html>'
        self.email_sender(message, telegramma, message['To'])

    def fraud_mail_ticket(self, text):
        message = self.email_helper('Создать заявку')
        message["To"] = text['mail_to']
        telegramma = f'<html>' \
                     f'<p><b>Клиент: </b> {text["client_name"]} </p>' \
                     f'<p><b>Номер телефона: </b> {text["phone"]} </p>' \
                     f'<p><b>Адрес: </b> {text["address"]} </p>' \
                     f'<p><b>Тариф: </b> {text["tariff"]} </p>' \
                     f'<p><b>Агент: </b> {text["agent"]} </p>' \
                     f'</html>'
        self.email_sender(message, telegramma, message['To'])

    def feedback_mail(self, text):
        message = self.email_helper('Жалобы и предложения')
        message["To"] = 'zvezdolom1@gmail.com'
        # Turn these into plain/html MIMEText objects
        telegramma = f'{text}'
        self.email_sender(message, telegramma, message['To'])

    def error_mail(self, text):
        message = self.email_helper('Жалобы и предложения')
        message["To"] = 'zvezdolom1@gmail.com'
        # Turn these into plain/html MIMEText objects
        telegramma = f'{text}'
        self.email_sender(message, telegramma, message['To'])

if __name__ == '__main__':
    email = EmailSender()
    email.feedback_mail('test')