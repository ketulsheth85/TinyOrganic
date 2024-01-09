from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from settings.minimal import env


def _scrub_email_address(email_address: str):
    if env.str('ENVIRONMENT', default='development') != 'production':
        if email_address.endswith('tinyorganics.com') and '+' in email_address:
            return f"{email_address.split('+')[0]}@tinyorganics.com".lower()
        elif email_address.endswith('tinyorganics.com'):
            return email_address.lower()
        return 'noreply@tinyorganics.com'
    return email_address


def send_email_message(
    subject: str,
    text_body: str,
    html_body: str,
    email_address: str,
):
    msg = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to=[_scrub_email_address(email_address), ],
    )
    msg.attach_alternative(html_body, "text/html")
    return msg.send()
