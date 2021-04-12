from django.urls import path
from e_delegacje.views import (
    index,
    BtApplicationCreateView,
    BtApplicationListView,
    BtApplicationDetailView,
    BtApplicationDeleteView,
    BtApplicationSettlementView,
    BtApplicationSettlementCreateView,
    BtApplicationSettlementsListView,
    BtApplicationSettlementDetailView,
    BtApplicationSettlementMileageCreateView,
    BtApplicationSettlementCostCreateView,
    BtApplicationSettlementFeedingCreateView,
    BtApplicationSettlementInfoCreateFormView,
)

app_name = 'e_delegacje'
urlpatterns = [

    path('', index, name='index'),

    # BtApplicatons - wnioski o delegacje
    path('applications-create/', BtApplicationCreateView.as_view(), name='applications-create'),
    path('applications-list', BtApplicationListView.as_view(), name='applications-list'),
    path('application-details/<pk>', BtApplicationDetailView.as_view(), name='application-details'),
    path('application-delete/<pk>', BtApplicationDeleteView.as_view(), name='application-delete'),
    # BtApplicatons - wnioski o rozliczenie delegacji
    path('settlement-create/<pk>', BtApplicationSettlementCreateView.as_view(), name='settlement-create'),
    path('settlement-add-forms/<pk>', BtApplicationSettlementView.as_view(), name='settlement-add-forms'),
    path('settlements-list', BtApplicationSettlementsListView.as_view(), name='settlements-list'),
    path('settlement-details/<pk>', BtApplicationSettlementDetailView.as_view(), name='settlement-details'),

    # podformularze do rozliczenia wniosku
    path(
        'settlement-info-create/<pk>',
        BtApplicationSettlementInfoCreateFormView.as_view(),
        name='settlement-info-create'
    ),
    path(
        'settlement-info-create/<pk>',
        BtApplicationSettlementCostCreateView.as_view(),
        name='settlement-info-create'
    ),
    path(
        'settlement-info-create/<pk>',
        BtApplicationSettlementMileageCreateView.as_view(),
        name='settlement-info-create'
    ),
    path(
        'settlement-info-create/<pk>',
        BtApplicationSettlementFeedingCreateView.as_view(),
        name='settlement-info-create'
    ),

]
