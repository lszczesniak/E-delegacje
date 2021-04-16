from django.urls import path
from setup.views import (
    BtUserListView,
    BtUserDetailView,
    BtRegionListView,
    BtRegionDetailView,
    BtRegionUpdateView,
    BtDivisionListView,
    BtDivisionDetailView,
    BtLocationListView,
    BtLocationDetailView,
    BtLocationCreateView,
    BtCostCenterListView,
    BtCostCenterDetailView,
    BtCostCenterCreateView,
    BtMileageRatesListView,
    BtMileageRatesDetailView,
    BtMileageRatesCreateView,
    BtDelegationRateListView,
    BtDelegationRateDetailView,
    BtDelegationRateCreateView,
    BtDelegationRateUpdateView,
    BtDepartmentListView,
    BtDepartmentDetailView,
    BtDepartmentCreateView,
    BtDepartmentUpdateView,


)
app_name = 'setup'
urlpatterns = [
    path('user-list-view/', BtUserListView.as_view(), name="user-list-view"),
    path('user-details-view/<pk>', BtUserDetailView.as_view(), name="user-details-view"),
    path('region-list-view/', BtRegionListView.as_view(), name="region-list-view"),
    path('region-details-view/<pk>', BtRegionDetailView.as_view(), name="region-details-view"),
    path('region-update-view/<pk>', BtRegionUpdateView.as_view(), name="region-update-view"),

    path('division-list-view/', BtDivisionListView.as_view(), name="division-list-view"),
    path('division-details-view/<pk>', BtDivisionDetailView.as_view(), name="division-details-view"),
    path('location-list-view/', BtLocationListView.as_view(), name="location-list-view"),
    path('location-details-view/<pk>', BtLocationDetailView.as_view(), name="location-details-view"),
    path('location-create-view/', BtLocationCreateView.as_view(), name="location-create"),

    path('costcenter-list-view/', BtCostCenterListView.as_view(), name="costcenter-list-view"),
    path('costcenter-details-view/<pk>', BtCostCenterDetailView.as_view(), name="costcenter-details-view"),
    path('costcenter-create-view/', BtCostCenterCreateView.as_view(), name="costcenter-create"),

    path('mileagetate-list-view/', BtMileageRatesListView.as_view(), name="mileagetate-list-view"),
    path('mileagetate-details-view/<pk>', BtMileageRatesDetailView.as_view(), name="mileagetate-details-view"),
    path('mileagetate-create-view/', BtMileageRatesCreateView.as_view(), name="mileagerate-create"),

    path('ratetax-list-view/', BtDelegationRateListView.as_view(), name="delegationrate-list-view"),
    path('delegationrate-details-view/<pk>', BtDelegationRateDetailView.as_view(), name="delegationrate-details-view"),
    path('delegationrate-create-view/', BtDelegationRateCreateView.as_view(), name="delegationrate-create"),
    path('delegationrate-update-view/<pk>', BtDelegationRateUpdateView.as_view(), name="delegationrate-update-view"),

    path('department-list-view/', BtDepartmentListView.as_view(), name="department-list-view"),
    path('department-details-view/<pk>', BtDepartmentDetailView.as_view(), name="department-details-view"),
    path('department-create-view/', BtDepartmentCreateView.as_view(), name="department-create"),
    path('department-update-view/<pk>', BtDepartmentUpdateView.as_view(), name="department-update-view"),



]
