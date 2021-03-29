from enum import Enum


class BtTripCategory(Enum):
    kr = 'krajowa'
    zg = 'zagraniczna'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtApplicationStatus(Enum):
    saved = 'Zapisany'
    in_progress = 'W akceptacji'
    approved = 'Zaakcdptowany'
    settled = 'Rozliczony'
    canceled = 'Anulowany'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtTransportType(Enum):
    train = "pociąg"
    plane = 'samolot'
    company_car = 'samochód służbowy'
    own_car = 'własny samochód'
    other = 'inny'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtEmployeeLevel(Enum):
    lvl1 = 'podstawowy'
    lvl2 = 'kierownik'
    lvl3 = 'dyrektor'
    lvl4 = 'dyrektor regionu'
    lvl5 = 'dyrektor dywizji'
    lvl6 = 'członek zarządu'
    lvl7 = 'prezes zarządu'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtCostCategory(Enum):
    accommodation = 'nocleg'
    transport = 'dojazd'
    luggage = 'bagaż'
    other = 'inne'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtVatRates(Enum):
    W1 = '23 %'
    W7 = '7 %'
    WN = 'nie dotyczy'
    W0 = 'zwolniony'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class BtMileageVehicleTypes(Enum):
    car_under_900cm3 = 'auto o pojemności do 900cm3'
    car_above_900cm3 = 'auto o pojemności powyżej 900cm3'
    motorbike = 'motocykl'
    moped = 'motorowe'

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


