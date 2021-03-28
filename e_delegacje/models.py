from django.db import models
from django.contrib.auth.models import User


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
