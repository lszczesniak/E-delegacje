from django.contrib import admin
from setup.models import (
    BtUser,
    BtDivision,
    BtCostCenter,
    BtLocation,
    BtRegion,
    BtDepartment,
    BtMileageRates,
    BtDelegationRate,
    BtCurrency,
    BtCountry
)
admin.site.register(BtUser)
admin.site.register(BtRegion)
admin.site.register(BtLocation)
admin.site.register(BtCostCenter)
admin.site.register(BtDepartment)
admin.site.register(BtMileageRates)
admin.site.register(BtDivision)
admin.site.register(BtDelegationRate)
admin.site.register(BtCurrency)
admin.site.register(BtCountry)
