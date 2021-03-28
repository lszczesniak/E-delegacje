from django.db import models
from django.contrib.auth.models import User
from e_delegacje.enums import BtTripCategoryChoice, BtApplicationStatus, BtTransportType, BtEmployeeLevel


# Create your models here.

class BtRegion(models.Model):
    name = models.CharField(max_length=100)


class BtDivision(models.Model):
    name = models.CharField(max_length=100)
    manager = models.CharField(max_length=100)


class BtLocation(models.Model):
    name = models.CharField(max_length=100)
    profit_center = models.CharField(max_length=10)


class BtCostCenter(models.Model):
    text = models.CharField(max_length=20)
    profit_center_id = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_CostCenters")


class BtRatesTax(models.Model):
    diet_rates = models.IntegerField(max_length=10)
    etc = models.CharField(max_length=10)


class BtSubmissionStatus(models.Model):
    submission_text = models.CharField(max_length=20)


class BtDepartment(models.Model):
    name = models.CharField(max_length=100)
    manager_id = models.CharField(max_length=10)
    profit_center = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_Departments")
    cost_center = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name="Bt_Departments")


class BtUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(BtDepartment, on_delete=models.PROTECT, related_name="Bt_Users")
    division = models.ForeignKey(BtDepartment, on_delete=models.PROTECT, related_name="Bt_Users")
    employee_level = models.CharField(max_length=100)
    manager = models.ForeignKey(BtDivision, on_delete=models.PROTECT, related_name="Bt_Users")


class BtApplication(models.Model):
    trip_category = models.CharField(max_length=2, choices=BtTripCategoryChoice)
    target_user = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications')
    application_author = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name='bt_applications')
    application_status = models.CharField(max_length=30, choices=BtApplicationStatus)
    employee_level = models.CharField(max_length=30, choices=BtEmployeeLevel)
    application_date = models.DateField(auto_now_add=True)
    trip_purpose_text = models.CharField(max_length=250)
    CostCenter = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name='bt_applications')
    transport_type = models.CharField(max_length=30, choices=BtTransportType)
    travel_route = models.CharField(max_length=120)
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    advance_payment = models.DecimalField(decimal_places=2, null=True, blank=True)


class BtApplicationSettlement(models.Model):
    bt_application_id = models.ForeignKey(
        BtApplication,
        on_delete=models.CASCADE,
        related_name='bt_applications_settlements'
    )


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
    advance_payment = models.OneToOneField(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application_settlement_info'
    )


class BtApplicationSettlementCost(models.Model):
    bt_application_settlement = models.OneToOneField(
        BtApplicationSettlement,
        on_delete=models.CASCADE,
        related_name='bt_application'
    )







