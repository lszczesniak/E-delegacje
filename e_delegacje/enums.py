from enum import Enum


class BtTripCategory(Enum):
    kr = 'krajowa'
    zg = 'zagraniczna'


class BtApplicationStatus(Enum):
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


class BtEmployeeLevel(Enum):
    lvl1 = 'podstawowy'
    lvl2 = 'kierownik'
    lvl3 = 'dyrektor'
    lvl4 = 'dyrektor regionu'
    lvl5 = 'dyrektor dywizji'
    lvl6 = 'członek zarządu'
    lvl7 = 'prezes zarządu'


class BtCostCategory(Enum):
    accommodation = 'nocleg'
    transport = 'dojazd'
    luggage = 'bagaż'
    other = 'inne'


class BtVatRates(Enum):
    W1 = '23 %'
    W7 = '7 %'
    WN = 'nie dotyczy'
    W0 = 'zwolniony'


class BtMileageVehicleTypes(Enum):
    car_under_900cm3 = 'auto o pojemności do 900cm3'
    car_above_900cm3 = 'auto o pojemności powyżej 900cm3'
    motorbike = 'motocykl'
    moped = 'motorowe'



