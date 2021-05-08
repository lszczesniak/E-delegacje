from django.contrib.auth.admin import UserAdmin
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
from setup.forms import BtUserCreationForm


class BtUserAdmin(UserAdmin):
    add_form = BtUserCreationForm
    list_display = ('username', 'first_name', 'last_name', 'manager', 'id',)
    fieldsets = ((None, {'fields': ('username',
                                    'password',
                                    'first_name',
                                    'last_name',
                                    'email',
                                    'department',
                                    'manager',
                                    'employee_level',
                                    'is_superuser',
                                    'is_staff',
                                    'is_active',
                                    )}), )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('username',
                   'password',
                   'first_name',
                   'last_name',
                   'email',
                   'department',
                   'manager',
                   'employee_level',
                   'is_superuser',
                   'is_staff',
                   'is_active',
                   )
    },
                     ),)

    ordering = ('id',)





admin.site.register(BtUser, BtUserAdmin)
# admin.site.register(BtUser)
admin.site.register(BtRegion)
admin.site.register(BtLocation)
admin.site.register(BtCostCenter)
admin.site.register(BtDepartment)
admin.site.register(BtMileageRates)
admin.site.register(BtDivision)
admin.site.register(BtDelegationRate)
admin.site.register(BtCurrency)
admin.site.register(BtCountry)
