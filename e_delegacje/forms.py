import datetime
from django.core.exceptions import ValidationError

from django.forms.models import inlineformset_factory
from e_delegacje.models import (
    BtApplicationSettlement,
    BtApplicationSettlementFeeding,
    BtApplicationSettlementInfo,
    BtApplication
)
from setup.models import BtMileageRates, BtUser, BtCostCenter, BtCurrency, BtCountry

from django.core.mail import EmailMultiAlternatives
from django import forms
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from delegacje import settings
from e_delegacje.enums import (
    BtApplicationStatus,
    BtTransportType,
    BtCostCategory,
    BtVatRates,
)


class DateInputWidget(forms.DateInput):
    input_type = 'date'


class TimeInputWidget(forms.TimeInput):
    input_type = 'time'


class BtApplicationForm(forms.ModelForm):
    bt_country = forms.ModelChoiceField(
        queryset=BtCountry.objects.all(),
        label="Wybierz kraj",
        initial=BtCountry.objects.get(id=1)
    )
    target_user = forms.ModelChoiceField(queryset=BtUser.objects.all(), label="Delegowany")
    trip_purpose_text = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={'rows':3}),
        label="Cel podrózy")
    CostCenter = forms.ModelChoiceField(queryset=BtCostCenter.objects.all(), label="Cost Center")
    transport_type = forms.TypedChoiceField(choices=BtTransportType.choices, label="Rodzaj transportu",)
    travel_route = forms.CharField(max_length=120, label="Trasa podróży")
    planned_start_date = forms.DateField(
        label="Data wyjazdu",
        widget=DateInputWidget
    )
    planned_end_date = forms.DateField(
        label="Data powrotu",
        widget=DateInputWidget
    )
    advance_payment_currency = forms.ModelChoiceField(
        queryset=BtCurrency.objects.all(),
        label="Waluta",
        blank=True,
        initial=BtCurrency.objects.get(code='PLN')
    )
    advance_payment = forms.DecimalField(decimal_places=2, max_digits=6, label="Zaliczka", initial=0, min_value=0)
    current_datetime = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BtApplication
        exclude = ('employee_level',
                   'application_author',
                   'application_status',
                   'application_log',
                   'approver',
                   'approval_date')

    def clean(self):
        result = super().clean()
        if result['planned_start_date'] > result['planned_end_date']:
            raise ValidationError("Data wyjazdu musi być przed datą powrotu!")

    def send_mail(self, user_mail, sent_app):

        result = super().clean()
        application_number = sent_app.id
        sent_app_date = sent_app.application_date
        # sent_app_sstatus = sent_app.application_status
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
            'bt_approval_mail_detail.html',
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
        return result


class BtApplicationSettlementForm(forms.Form):
    bt_application_id = forms.ModelChoiceField(
        queryset=BtApplication.objects.all(),
        label="",
        empty_label="wybierz wniosek do rozliczenia"
    )


class BtApplicationSettlementInfoForm(forms.ModelForm):
    bt_completed = forms.TypedChoiceField(
        label="Czy delegacja się odbyła?",
        choices=[("", ""), ('tak', 'tak'), ('nie', 'nie')],
        )
    bt_start_date = forms.DateField(label="Data wyjazdu",widget=DateInputWidget)
    bt_start_time = forms.TimeField(label="Godzina wyjazdu", widget=TimeInputWidget)
    bt_end_date = forms.DateField(label="Data powrotu", widget=DateInputWidget)
    bt_end_time = forms.TimeField(label="Godzina powrotu", widget=TimeInputWidget)
    settlement_exchange_rate = forms.DecimalField(decimal_places=5,
                                                  max_digits=8,
                                                  label="Kurs rozliczenia",
                                                  min_value=0,
                                                  initial=1,
                                                  help_text='W przypadku zaliczki w walucie PLN wpisz "1".')
    current_datetime = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BtApplicationSettlementInfo
        exclude = ('bt_application_settlement', 'advance_payment', 'settlement_log')

    def clean(self):
        result = super().clean()
        comb_start_time = datetime.datetime(
            result['bt_start_date'].year,
            result['bt_start_date'].month,
            result['bt_start_date'].day,
            result['bt_start_time'].hour,
            result['bt_start_time'].minute)
        print(comb_start_time)
        comb_end_time = datetime.datetime(
            result['bt_end_date'].year,
            result['bt_end_date'].month,
            result['bt_end_date'].day,
            result['bt_end_time'].hour,
            result['bt_end_time'].minute)
        print(comb_end_time)
        if comb_start_time > comb_end_time:
            raise ValidationError("Data i godzina wyjazdu musi być przed datą i godziną powrotu!")
        return result


class BtApplicationSettlementCostForm(forms.Form):
    bt_cost_category = forms.TypedChoiceField(choices=BtCostCategory.choices, label="Kategoria kosztu", initial="")
    bt_cost_description = forms.CharField(max_length=120, label="Opis")
    bt_cost_amount = forms.DecimalField(decimal_places=2, max_digits=8, label="Kwota", min_value=0)
    bt_cost_currency = forms.ModelChoiceField(queryset=BtCurrency.objects.all(), label="Waluta", initial='')
    bt_cost_document_date = forms.DateField(label="Data dokumentu", widget=DateInputWidget)
    bt_cost_VAT_rate = forms.TypedChoiceField(choices=BtVatRates.choices, label="Stawka vat")
    # attachment = forms.FileField()


class BtApplicationSettlementMileageForm(forms.Form):
    bt_car_reg_number = forms.CharField(max_length=8, label='Numer rejestracyjny')
    bt_mileage_rate = forms.ModelChoiceField(queryset=BtMileageRates.objects.all(), label='Stawka')
    trip_start_place = forms.CharField(max_length=50, label='Miejsce wyjazdu')
    trip_date = forms.DateField(widget=DateInputWidget, label='Data przejazdu')
    trip_description = forms.CharField(max_length=120, label='Trasa przejazdu')
    trip_purpose = forms.CharField(max_length=240, label='Cel przejazdu')
    mileage = forms.IntegerField(label='Liczba kilometrów', min_value=0)


class BtApplicationSettlementFeedingForm(forms.ModelForm):
    breakfast_quantity = forms.IntegerField(label='Liczba zapewnionych śniadań', min_value=0, initial=0)
    dinner_quantity = forms.IntegerField(label='Liczba zapewnionych obiadów', min_value=0, initial=0)
    supper_quantity = forms.IntegerField(label='Liczba zapewnionych kolacji', min_value=0, initial=0)

    class Meta:
        model = BtApplicationSettlementInfo
        fields = ('breakfast_quantity', 'dinner_quantity', 'supper_quantity')
        widgets = forms.IntegerField.widget(attrs={'onchange': "get_onchange_meals_correction()"})


BtApplicationSettlementInfoFormset = inlineformset_factory(
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    fields=('bt_completed', 'bt_start_date', 'bt_start_time', 'bt_end_date', 'bt_end_time', 'settlement_exchange_rate'),
    form=BtApplicationSettlementInfoForm,
    labels={'bt_start_date': "Data wyjazdu",
            'bt_start_time': "Godzina wyjazdu",
            "bt_end_date": "Data powrotu",
            "bt_end_time": "Godzina powrotu",
            'bt_completed': "Czy delegacja się odbyła?",
            'settlement_exchange_rate': "Kurs rozliczenia",
            },
    widgets={'bt_start_date': DateInputWidget,
             'bt_end_date': DateInputWidget,
             'bt_start_time': TimeInputWidget,
             'bt_end_time': TimeInputWidget,
             },

    can_delete=False
)


BtApplicationSettlementFeedingFormset = inlineformset_factory(
    BtApplicationSettlement, BtApplicationSettlementFeeding,
    fields=(
        'breakfast_quantity',
        'dinner_quantity',
        'supper_quantity'),
    labels={'breakfast_quantity': 'Liczba zapewnionych śniadań',
            'dinner_quantity': 'Liczba zapewnionych obiadów',
            'supper_quantity': 'Liczba zapewnionych kolacji'},
    can_delete=False,
    # widgets=forms.IntegerField.widget(attrs={'onchange': "get_onchange_meals_correction()"})
)


class BtRejectionForm(forms.Form):
    application_log = forms.CharField(max_length=240,
                                      label="Przyczyna odrzucenia",
                                      widget=forms.Textarea(attrs={'rows': 5})
                                      )


class BtApprovedForm(forms.Form):
    application_log = forms.CharField(max_length=240,
                                      label="Przyczyna odrzucenia",
                                      widget=forms.HiddenInput(),
                                      initial='approved',

                                      )
