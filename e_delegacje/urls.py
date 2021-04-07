from django.urls import path
from e_delegacje.views import index, BtApplicationCreateView, BtApplicationListView, BtApplicationDetailView

app_name = 'e_delegacje'
urlpatterns = [

    path('', index, name='index'),

    # BtApplicatons - wnioski o delegacje
    path('applications-create/', BtApplicationCreateView.as_view(), name='applications-create'),
    path('applications-list', BtApplicationListView.as_view(), name='applications-list'),
    path('application-details/<pk>', BtApplicationDetailView.as_view(), name='application-details'),

    ]
