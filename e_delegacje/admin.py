from django.contrib import admin
from e_delegacje.models import (
    BtUser,
    BtApplication,
    BtDivision,
    BtCostCenter,
    BtLocation,
    BtApplicationSettlement,
    BtApplicationSettlementCost,
    BtRegion,
    BtApplicationSettlementFeeding,
    BtApplicationSettlementInfo,
    BtApplicationSettlementMileage,
    BtDepartment,
    BtMileageRates,
    BtSubmissionStatus,
    BtRatesTax
)

admin.site.register(BtUser)
admin.site.register(BtRegion)
admin.site.register(BtLocation)
admin.site.register(BtCostCenter)
admin.site.register(BtDepartment)
admin.site.register(BtApplication)
admin.site.register(BtDivision)
admin.site.register(BtApplicationSettlement)
admin.site.register(BtApplicationSettlementInfo)
admin.site.register(BtApplicationSettlementCost)
admin.site.register(BtApplicationSettlementMileage)
admin.site.register(BtApplicationSettlementFeeding)
