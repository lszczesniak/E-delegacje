from django.contrib.auth.models import User

from .models import BtUser, BtCostCenter
from django.db import models
from django.core.mail import EmailMultiAlternatives
from django import forms
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from delegacje import settings
from e_delegacje.enums import (
    BtTripCategory,
    BtApplicationStatus,
    BtTransportType,
    BtEmployeeLevel,
    BtCostCategory,
    BtVatRates,
    BtMileageVehicleTypes

)


class BtApplicationForm(forms.Form):
    trip_category = forms.TypedChoiceField(choices=BtTripCategory.choices())
    target_user = forms.ModelChoiceField(queryset=BtUser.objects.all())
    application_author = forms.ModelChoiceField(queryset=BtUser.objects.all())
    trip_purpose_text = forms.CharField(max_length=250, widget=forms.Textarea)
    CostCenter = forms.ModelChoiceField(queryset=BtCostCenter.objects.all())
    transport_type = forms.TypedChoiceField(choices=BtTransportType.choices())
    travel_route = forms.CharField(max_length=120)
    planned_start_date = forms.DateField(input_formats=['%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y'])
    planned_end_date = forms.DateField(input_formats=['%d.%m.%Y', '%d-%m-%Y', '%d/%m/%Y'])
    advance_payment = forms.DecimalField(decimal_places=2, max_digits=6)

    def send_mail(self, user_mail):

        result = super().clean()
        nr_wniosku = result['id']
        trip_category = result['trip_category']
        target_user = result['target_user']
        application_author = result['application_author']
        application_status = BtApplicationStatus.saved.value
        trip_purpose_text = result['trip_purpose_text']
        CostCenter = result['CostCenter']
        transport_type = result['transport_type']
        travel_route = result['travel_route']
        planned_start_date = result['planned_start_date']
        planned_end_date = result['planned_end_date']
        advance_payment = result['advance_payment']
        employee_level = BtUser.objects.get(id=target_user.id)

        html_content = render_to_string(
            'email_template.html',
            {
                'nr_wniosku': nr_wniosku,
                'trip_category': trip_category,
                'target_user': target_user,
                'application_author': application_author,
                'application_status': application_status,
                'trip_purpose_text': trip_purpose_text,
                'CostCenter': CostCenter,
                'transport_type': transport_type,
                'travel_route': travel_route,
                'planned_start_date': planned_start_date,
                'planned_end_date': planned_end_date,
                'advance_payment': advance_payment,
                'employee_level': employee_level,
            }
        )
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            # subject
            f'Proszę o akceptację wniosku nr {nr_wniosku}.',
            # content
            text_content,
            # from email
            settings.EMAIL_HOST_USER,
            # receipients list
            [user_mail]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        return result


