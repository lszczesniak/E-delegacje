from enum import Enum


class BtTripCategoryChoice(Enum):
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
