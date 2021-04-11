from django.contrib import admin
from e_delegacje.models import (
    BtApplication,
    BtApplicationSettlement,
    BtApplicationSettlementCost,
    BtApplicationSettlementFeeding,
    BtApplicationSettlementInfo,
    BtApplicationSettlementMileage,
    BtSubmissionStatus,
)

admin.site.register(BtApplication)
admin.site.register(BtApplicationSettlement)
admin.site.register(BtApplicationSettlementInfo)
admin.site.register(BtApplicationSettlementCost)
admin.site.register(BtApplicationSettlementMileage)
admin.site.register(BtApplicationSettlementFeeding)
admin.site.register(BtSubmissionStatus)