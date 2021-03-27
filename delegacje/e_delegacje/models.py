from django.db import models
from enum import Enum


class BtTripCategoryChoices(Enum):
    kr = 'krajowa'
    zg = 'zagraniczna'


class BtApplicationStatuses(Enum):
    saved = 'Zapisany'
    in_progress = 'W akceptacji'
    approved = 'Zaakcdptowany'
    settled = 'Rozliczony'
    canceled = 'Anulowany'


class BtTransportType(Enum):
    train = "pociąg"
    plane = 'samolot'
    company_car = 'samochód służbowy'
    own_car = 'własny samochód'
    other = 'inny'


class BtApplication(models.Model):
    trip_category = models.CharField(max_length=2, choices=BtTripCategoryChoices)
    # nie jestem pewien czy dobrze wpisałem related names -
    # dwa pola z FK do tego samego modelu i z tego samego modelu - ale znaczenia pól inne kompletnie

    target_user = models.ForeignKey(BtUsers, on_delete=models.PROTECT, related_name='Bt_applications')
    application_author = models.ForeignKey(BtUsers, on_delete=models.PROTECT, related_name='Bt_applications')
    application_status = models.CharField(max_length=30, choices=BtApplicationStatuses)
    emploee_level = models.CharField(max_length=30, choices=BtEmploeeLevels)
    application_date = models.DateField(auto_now_add=True)
    trip_purpose_text = models.CharField(max_length=250)
    CostCenter = models.ForeignKey(BtCostCenters, on_delete=models.PROTECT, related_name='Bt_applications')
    transport_type = models.CharField(max_length=30, choices=BtTransportType)
    travel_route = models.CharField(max_length=120)
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
