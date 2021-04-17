from django.db import models
from django.contrib.auth.models import AbstractUser
from e_delegacje.enums import (
    BtEmployeeLevel,
    BtMileageVehicleTypes

)


class BtUser(AbstractUser):
    department = models.ForeignKey("BtDepartment", on_delete=models.PROTECT, related_name="bt_Users", null=True)
    employee_level = models.CharField(max_length=15, choices=BtEmployeeLevel.choices, default=BtEmployeeLevel.lvl7)
    manager = models.ForeignKey("BtUser", on_delete=models.PROTECT, related_name="bt_Users", null=True)

    def __str__(self):
        return f'{self.username}'


class BtRegion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class BtDivision(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name="Bt_Divisions")

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


class BtCountry(models.Model):
    country_name = models.CharField(max_length=20)
    alpha_code = models.CharField(max_length=3)

    def __str__(self):
        return f'{self.country_name}'


class BtDelegationRate(models.Model):
    delagation_rate = models.IntegerField()
    country = models.ForeignKey(BtCountry, on_delete=models.PROTECT, related_name="Bt_Delegation")

    def __str__(self):
        return f'{self.country.country_name} - {self.delagation_rate}'


class BtMileageRates(models.Model):
    vehicle_type = models.CharField(max_length=20, choices=BtMileageVehicleTypes.choices)
    rate = models.DecimalField(decimal_places=4, max_digits=6)

    def __str__(self):
        return f'{self.vehicle_type} - rate: {self.rate}'


class BtDepartment(models.Model):
    name = models.CharField(max_length=100)
    manager_id = models.ForeignKey("BtUser", on_delete=models.PROTECT, related_name="Bt_Departments")
    profit_center = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_Departments")
    cost_center = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name="Bt_Departments")

    def __str__(self):
        return f'{self.name}'


class BtCurrency(models.Model):
    code = models.CharField(max_length=3)
    text = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.code}'


