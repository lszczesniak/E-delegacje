from django.db import models
from setup.models import BtUser, BtCostCenter, BtDelegationRate, BtMileageRates, BtCurrency, BtCountry
from django.contrib.auth.models import User, AbstractUser
from e_delegacje.enums import (
    BtApplicationStatus,
    BtTransportType,
    BtEmployeeLevel,
    BtCostCategory,
    BtVatRates,
)


class BtSubmissionStatus(models.Model):
    submission_text = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.submission_text}'


class BtApplication(models.Model):
    bt_country = models.ForeignKey(BtCountry, on_delete=models.PROTECT, related_name='bt_applications')
    target_user = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications')
    application_author = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications_author')
    application_status = models.CharField(max_length=30, choices=BtApplicationStatus.choices)
    employee_level = models.CharField(max_length=30, choices=BtEmployeeLevel.choices)
    application_date = models.DateField(auto_now_add=True)
    trip_purpose_text = models.CharField(max_length=250)
    CostCenter = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name='bt_applications')
    transport_type = models.CharField(max_length=30, choices=BtTransportType.choices)
    travel_route = models.CharField(max_length=120)
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    advance_payment = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)
    advance_payment_currency = models.ForeignKey(BtCurrency, on_delete=models.PROTECT, related_name='bt_applications')
    application_log = models.CharField(max_length=2400)

    def __str__(self):
        return f'{self.trip_purpose_text}'


class BtApplicationSettlement(models.Model):
    bt_application_id = models.OneToOneField(
        BtApplication,
        on_delete=models.CASCADE,
        related_name='bt_applications_settlements'
    )

    def __str__(self):
        return f'Settlement {self.id} to application {self.bt_application_id.id}'


class BtApplicationSettlementInfo(models.Model):
    bt_application_settlement = models.OneToOneField(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_info'
    )
    bt_completed = models.CharField(max_length=25, choices=[('tak', 'tak'), ('nie', 'nie')])
    bt_start_date = models.DateField()
    bt_start_time = models.TimeField()
    bt_end_date = models.DateField()
    bt_end_time = models.TimeField()
    advance_payment = models.OneToOneField(
        BtApplication,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_info'
    )
    settlement_log = models.CharField(max_length=2400)

    def __str__(self):
        return f'Informacje do rozliczenia wniosku {self.bt_application_settlement}'


class BtApplicationSettlementCost(models.Model):
    bt_application_settlement = models.ForeignKey(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_costs'
    )
    bt_cost_category = models.CharField(max_length=40, choices=BtCostCategory.choices)
    bt_cost_description = models.CharField(max_length=140)
    bt_cost_amount = models.DecimalField(decimal_places=2, max_digits=8)
    bt_cost_currency = models.ForeignKey(
        BtCurrency,
        on_delete=models.PROTECT,
        related_name='bt_application_settlement_costs'
    )
    bt_cost_document_date = models.DateField()
    bt_cost_VAT_rate = models.CharField(max_length=20, choices=BtVatRates.choices)
    attachment = models.FileField(null=True, blank=True)

    def __str__(self):
        return f'Koszty do rozliczenia wniosku{self.bt_application_settlement}'


class BtApplicationSettlementMileage(models.Model):
    bt_application_settlement = models.ForeignKey(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_mileages'
    )
    bt_car_reg_number = models.CharField(max_length=8)
    bt_mileage_rate = models.ForeignKey(
        BtMileageRates,
        on_delete=models.PROTECT,
        related_name='bt_application_settlement_mileages'
    )
    trip_start_place = models.CharField(max_length=50)
    trip_date = models.DateField()
    trip_description = models.CharField(max_length=120)
    trip_purpose = models.CharField(max_length=240)
    mileage = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return f'Kilometrówka do rozliczenia wniosku{self.bt_application_settlement}'


class BtApplicationSettlementFeeding(models.Model):
    bt_application_settlement = models.OneToOneField(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_feeding'
    )
    breakfast_quantity = models.IntegerField()
    dinner_quantity = models.IntegerField()
    supper_quantity = models.IntegerField()

    def __str__(self):
        return f'Wyżywienie do rozliczenia wniosku{self.bt_application_settlement}'



