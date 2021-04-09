from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from e_delegacje.enums import (
    BtTripCategory,
    BtApplicationStatus,
    BtTransportType,
    BtEmployeeLevel,
    BtCostCategory,
    BtVatRates,
    BtMileageVehicleTypes

)


class BtRegion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class BtDivision(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Bt_Divisions')

    def __str__(self):
        return f'{self.name}'


class BtLocation(models.Model):
    name = models.CharField(max_length=100)
    profit_center = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name} - {self.profit_center}'


class BtCostCenter(models.Model):
    text = models.CharField(max_length=20)
    cost_center_number = models.CharField(max_length=10)
    profit_center_id = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_CostCenters")

    def __str__(self):
        return f'{self.text} - {self.cost_center_number}'


class BtRatesTax(models.Model):
    diet_rates = models.IntegerField()
    etc = models.CharField(max_length=10)


class BtMileageRates(models.Model):
    vehicle_type = models.CharField(max_length=20, choices=BtMileageVehicleTypes.choices())
    rate = models.DecimalField(decimal_places=4, max_digits=6)

    def __str__(self):
        return f'{self.vehicle_type} - rate: {self.rate}'


class BtSubmissionStatus(models.Model):
    submission_text = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.submission_text}'


class BtDepartment(models.Model):
    name = models.CharField(max_length=100)
    manager_id = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Bt_Departments')
    profit_center = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_Departments")
    cost_center = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name="Bt_Departments")

    def __str__(self):
        return f'{self.name}'


class BtUser(models.Model):
    bt_user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(BtDepartment, on_delete=models.PROTECT, related_name="bt_Users")
    division = models.ForeignKey(BtDivision, on_delete=models.PROTECT, related_name="bt_Users")
    employee_level = models.CharField(max_length=15, choices=BtEmployeeLevel.choices())
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bt_Users")

    def __str__(self):
        return f'{self.bt_user_id.first_name}'


class BtApplication(models.Model):
    trip_category = models.CharField(max_length=2, choices=BtTripCategory.choices())
    target_user = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications')
    application_author = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications_author')
    application_status = models.CharField(max_length=30, choices=BtApplicationStatus.choices())
    employee_level = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications_emp_lvl')
    application_date = models.DateField(auto_now_add=True)
    trip_purpose_text = models.CharField(max_length=250)
    CostCenter = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name='bt_applications')
    transport_type = models.CharField(max_length=30, choices=BtTransportType.choices())
    travel_route = models.CharField(max_length=120)
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    advance_payment = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True)

    def __str__(self):
        return f'{self.trip_purpose_text}'


class BtApplicationSettlement(models.Model):
    bt_application_id = models.ForeignKey(
        BtApplication,
        on_delete=models.CASCADE,
        related_name='bt_applications_settlements'
    )

    def __str__(self):
        return f'{self.bt_application_id}'


class BtApplicationSettlementInfo(models.Model):
    bt_application_settlement = models.OneToOneField(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application'
    )
    bt_completed = models.BooleanField()
    bt_start_date = models.DateField()
    bt_start_time = models.TimeField()
    bt_end_date = models.DateField()
    bt_end_time = models.TimeField()
    # gdzie referowac do którego modelu? czy w ogóle poninienem to wstawiac ponownie do drugiego modelu
    advance_payment = models.OneToOneField(
        BtApplication,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_info'
    )

    def __str__(self):
        return f'Informacje do rozliczenia wniosku {self.bt_application_settlement}'


class BtApplicationSettlementCost(models.Model):
    bt_application_settlement = models.ForeignKey(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_costs'
    )
    bt_cost_category = models.CharField(max_length=40, choices=BtCostCategory.choices())
    bt_cost_amount = models.DecimalField(decimal_places=2, max_digits=8)
    bt_cost_currency = models.ForeignKey(
        BtRatesTax,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_costs'
    )
    bt_cost_document_date = models.DateField()
    bt_cost_VAT_rate = models.CharField(max_length=10, choices=BtVatRates.choices())

    def __str__(self):
        return f'{self.bt_application_id}'


class BtApplicationSettlementMileage(models.Model):
    bt_application_settlement = models.ForeignKey(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_mileages'
    )
    bt_car_reg_number = models.CharField(max_length=8)
    bt_milage_rate = models.ForeignKey(
        BtMileageRates,
        on_delete=models.PROTECT,
        related_name='bt_application_settlement_mileages'
    )
    trip_start_place = models.CharField(max_length=50)
    trip_date = models.DateField()
    trip_description = models.CharField(max_length=120)
    trip_purpose = models.CharField(max_length=240)
    mileage = models.DecimalField(decimal_places=2, max_digits=8)


class BtApplicationSettlementFeeding(models.Model):
    bt_application_settlement = models.ForeignKey(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_feeding'
    )
    breakfast_quantity = models.IntegerField()
    dinner_quantity = models.IntegerField()
    supper_quantity = models.IntegerField()
