from e_delegacje.enums import BtApplicationStatus
from setup.models import BtUser
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from delegacje import settings
from django.core.mail import EmailMultiAlternatives

def new_application_notification(user_mail, sent_app):

    application_number = sent_app.id
    sent_app_date = sent_app.application_date
    country = sent_app.bt_country
    target_user = sent_app.target_user
    application_author = sent_app.application_author
    application_status = BtApplicationStatus.saved.value
    trip_purpose_text = sent_app.trip_purpose_text
    CostCenter = sent_app.CostCenter
    transport_type = sent_app.transport_type
    travel_route = sent_app.travel_route
    planned_start_date = sent_app.planned_start_date
    planned_end_date = sent_app.planned_end_date
    advance_payment = sent_app.advance_payment
    advance_payment_currency = sent_app.advance_payment_currency
    employee_level = BtUser.objects.get(id=target_user.id)

    html_content = render_to_string(
        'bt_mail_notification.html',
        {
            'application_number': application_number,
            'country': country,
            'target_user': target_user,
            'sent_app_date': sent_app_date,
            # 'sent_app_sstatus': sent_app_sstatus,
            'application_author': application_author,
            'application_status': application_status,
            'trip_purpose_text': trip_purpose_text,
            'CostCenter': CostCenter,
            'transport_type': transport_type,
            'travel_route': travel_route,
            'planned_start_date': planned_start_date,
            'planned_end_date': planned_end_date,
            'advance_payment': advance_payment,
            'advance_payment_currency': advance_payment_currency,
            'employee_level': employee_level,
        }
    )
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        # subject
        f'Proszę o akceptację wniosku nr {application_number}.',
        # content
        text_content,
        # from email
        settings.EMAIL_HOST_USER,
        # receipients list
        [user_mail]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def approved_or_rejected_notification(user_mail, sent_app):

    application_number = sent_app.id
    sent_app_date = sent_app.application_date
    country = sent_app.bt_country
    target_user = sent_app.target_user
    application_author = sent_app.application_author
    application_status = BtApplicationStatus.saved.value
    trip_purpose_text = sent_app.trip_purpose_text
    CostCenter = sent_app.CostCenter
    transport_type = sent_app.transport_type
    travel_route = sent_app.travel_route
    planned_start_date = sent_app.planned_start_date
    planned_end_date = sent_app.planned_end_date
    advance_payment = sent_app.advance_payment
    advance_payment_currency = sent_app.advance_payment_currency
    employee_level = BtUser.objects.get(id=target_user.id)

    html_content = render_to_string(
        'bt_mail_notification.html',
        {
            'application_number': application_number,
            'country': country,
            'target_user': target_user,
            'sent_app_date': sent_app_date,
            # 'sent_app_sstatus': sent_app_sstatus,
            'application_author': application_author,
            'application_status': application_status,
            'trip_purpose_text': trip_purpose_text,
            'CostCenter': CostCenter,
            'transport_type': transport_type,
            'travel_route': travel_route,
            'planned_start_date': planned_start_date,
            'planned_end_date': planned_end_date,
            'advance_payment': advance_payment,
            'advance_payment_currency': advance_payment_currency,
            'employee_level': employee_level,
        }
    )
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        # subject
        f'Proszę o akceptację wniosku nr {application_number}.',
        # content
        text_content,
        # from email
        settings.EMAIL_HOST_USER,
        # receipients list
        [user_mail]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


# na później
def new_settlement_notification(user_mail, sent_app):

    application_number = sent_app.id
    sent_app_date = sent_app.application_date
    country = sent_app.bt_country
    target_user = sent_app.target_user
    application_author = sent_app.application_author
    application_status = BtApplicationStatus.saved.value
    trip_purpose_text = sent_app.trip_purpose_text
    CostCenter = sent_app.CostCenter
    transport_type = sent_app.transport_type
    travel_route = sent_app.travel_route
    planned_start_date = sent_app.planned_start_date
    planned_end_date = sent_app.planned_end_date
    advance_payment = sent_app.advance_payment
    advance_payment_currency = sent_app.advance_payment_currency
    employee_level = BtUser.objects.get(id=target_user.id)

    html_content = render_to_string(
        'bt_mail_notification.html',
        {
            'application_number': application_number,
            'country': country,
            'target_user': target_user,
            'sent_app_date': sent_app_date,
            # 'sent_app_sstatus': sent_app_sstatus,
            'application_author': application_author,
            'application_status': application_status,
            'trip_purpose_text': trip_purpose_text,
            'CostCenter': CostCenter,
            'transport_type': transport_type,
            'travel_route': travel_route,
            'planned_start_date': planned_start_date,
            'planned_end_date': planned_end_date,
            'advance_payment': advance_payment,
            'advance_payment_currency': advance_payment_currency,
            'employee_level': employee_level,
        }
    )
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        # subject
        f'Proszę o akceptację wniosku nr {application_number}.',
        # content
        text_content,
        # from email
        settings.EMAIL_HOST_USER,
        # receipients list
        [user_mail]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
    