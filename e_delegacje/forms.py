from setup.models import BtMileageRates
from .models import BtUser, BtCostCenter, BtApplication, BtCurrency
from django.core.mail import EmailMultiAlternatives
from django import forms
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from delegacje import settings
from e_delegacje.enums import (
    BtTripCategory,
    BtApplicationStatus,
    BtTransportType,
    BtCostCategory,
    BtVatRates,
)


class DateInputWidget(forms.DateInput):
    input_type = 'date'


class TimeInputWidget(forms.TimeInput):
    input_type = 'time'


class BtApplicationForm(forms.Form):
    trip_category = forms.TypedChoiceField(choices=BtTripCategory.choices, label="Rodzaj delegacji", initial='')
    target_user = forms.ModelChoiceField(queryset=BtUser.objects.all(), label="Delegowany")
    application_author = forms.ModelChoiceField(queryset=BtUser.objects.all())
    trip_purpose_text = forms.CharField(
        max_length=250,
        widget=forms.Textarea,
        label="Cel podrózy")
    CostCenter = forms.ModelChoiceField(queryset=BtCostCenter.objects.all(), label="Cost Center")
    transport_type = forms.TypedChoiceField(choices=BtTransportType.choices, label="Rodzaj transportu")
    travel_route = forms.CharField(max_length=120, label="Trasa podróży")
    planned_start_date = forms.DateField(
        label="Data wyjazdu",
        widget=DateInputWidget
    )
    planned_end_date = forms.DateField(
        label="Data powrotu",
        widget=DateInputWidget
    )
    advance_payment = forms.DecimalField(decimal_places=2, max_digits=6, label="Zaliczka")

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


class BtApplicationSettlementForm(forms.Form):
    bt_application_id = forms.ModelChoiceField(
        queryset=BtApplication.objects.all(),
        label="",
        empty_label="wybierz wniosek do rozliczenia"
    )


class BtApplicationSettlementInfoForm(forms.Form):
    bt_completed = forms.TypedChoiceField(
        label="Czy delegacja się odbyła?",
        choices=[("", ""), ('tak', 'tak'), ('nie', 'nie')],
        )
    bt_start_date = forms.DateField(label="Data wyjazdu",widget=DateInputWidget)
    bt_start_time = forms.TimeField(label="Godzina wyjazdu", widget=TimeInputWidget)
    bt_end_date = forms.DateField(label="Data powrotu", widget=DateInputWidget)
    bt_end_time = forms.TimeField(label="Godzina powrotu", widget=TimeInputWidget)


class BtApplicationSettlementCostForm(forms.Form):
    bt_cost_category = forms.TypedChoiceField(choices=BtCostCategory.choices, label="Kategoria kosztu", initial="")
    bt_cost_description = forms.CharField(max_length=120, label="Opis")
    bt_cost_amount = forms.DecimalField(decimal_places=2, max_digits=8, label="Kwota" )
    bt_cost_currency = forms.ModelChoiceField(queryset=BtCurrency.objects.all(), label="Waluta", initial='')
    bt_cost_document_date = forms.DateField(label="Data dokumentu", widget=DateInputWidget)
    bt_cost_VAT_rate = forms.TypedChoiceField(choices=BtVatRates.choices, label="Stawka vat")


class BtApplicationSettlementMileageForm(forms.Form):
    bt_car_reg_number = forms.CharField(max_length=8, label='Numer rejestracyjny')
    bt_mileage_rate = forms.ModelChoiceField(queryset=BtMileageRates.objects.all(), label='Stawka')
    trip_start_place = forms.CharField(max_length=50, label='Miejsce wyjazdu')
    trip_date = forms.DateField(widget=DateInputWidget, label='Data przejazdu')
    trip_description = forms.CharField(max_length=120, label='Trasa przejazdu')
    trip_purpose = forms.CharField(max_length=240, label='Cel przejazdu')
    mileage = forms.DecimalField(decimal_places=2, max_digits=8, label='Liczba kilometrów')
