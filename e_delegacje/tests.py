from django.test import TestCase
import datetime

from e_delegacje.enums import BtApplicationStatus, BtTransportType
from e_delegacje.views import (trip_duration,
                               get_diet_amount_poland,
                               diet_reconciliation_poland,
                               get_diet_amount_abroad,
                               get_diet_amount_abroad, diet_reconciliation_abroad
                               )
from e_delegacje.models import (
    BtApplicationSettlement,
    BtApplicationSettlementFeeding,
    BtApplicationSettlementInfo,
    BtApplication
)
from setup.models import BtMileageRates, BtUser, BtCostCenter, BtCurrency, BtCountry, BtLocation, BtDelegationRate


class EdelegacjeTestCase(TestCase):
    def setUp(self):
        BtCountry.objects.create(country_name='Polska', alpha_code='POL')
        BtCountry.objects.create(country_name='Niemcy', alpha_code='GER')
        BtCurrency.objects.create(code='PLN', text='zł')
        BtCurrency.objects.create(code='EUR', text='eur')
        BtLocation.objects.create(name='Test location', profit_center='2141111')
        BtCostCenter.objects.create(text='Test costcenter',
                                    cost_center_number='4811119204',
                                    profit_center_id=BtLocation.objects.first()
                                    )
        BtUser.objects.create(username='Lukasz', first_name="lukasz", last_name="Teststein")
        country_pl = BtCountry.objects.get(country_name='Polska')
        country_de = BtCountry.objects.get(country_name='Niemcy')
        BtDelegationRate.objects.create(delagation_rate=30, country=country_pl)
        BtDelegationRate.objects.create(delagation_rate=49, country=country_de)
        target_user = BtUser.objects.first()
        application_author = BtUser.objects.first()
        application_status = BtApplicationStatus.saved.value
        trip_purpose_text_pl = 'Delegacja krajowa - test'
        trip_purpose_text_abr = 'Delegacja zagraniczna - test'
        CostCenter = BtCostCenter.objects.first()
        transport_type = BtTransportType.plane.value
        travel_route_pl = 'Warsaw - Cracow - Warsaw'
        travel_route_abr = 'Warsaw - Berlin - Warsaw'
        planned_start_date = datetime.datetime(2021, 4, 28)
        planned_end_date = datetime.datetime(2021, 4, 30)
        advance_payment = 100
        advance_payment_currency_pl = BtCurrency.objects.get(code='PLN')
        advance_payment_currency_abr = BtCurrency.objects.get(code='EUR')
        employee_level = target_user.employee_level
        application_log = 'New testcase created'
        Application_pl = BtApplication.objects.create(
            bt_country=country_pl,
            target_user=target_user,
            application_author=application_author,
            application_status=application_status,
            trip_purpose_text=trip_purpose_text_pl,
            CostCenter=CostCenter,
            transport_type=transport_type,
            travel_route=travel_route_pl,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            advance_payment=advance_payment,
            advance_payment_currency=advance_payment_currency_pl,
            employee_level=employee_level,
            application_log=application_log
        )
        settlement_pl = BtApplicationSettlement.objects.create(bt_application_id=Application_pl)
        BtApplicationSettlementInfo.objects.create(
            bt_application_settlement=settlement_pl,
            bt_completed='tak',
            bt_start_date=datetime.datetime(2021, 4, 28),
            bt_start_time=datetime.time(8, 00),
            bt_end_date=datetime.datetime(2021, 4, 29),
            bt_end_time=datetime.time(16, 00),
            advance_payment=settlement_pl.bt_application_id
        )
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement_pl,
            breakfast_quantity=1,
            dinner_quantity=0,
            supper_quantity=1
        )
        Application_abr = BtApplication.objects.create(
            bt_country=country_de,
            target_user=target_user,
            application_author=application_author,
            application_status=application_status,
            trip_purpose_text=trip_purpose_text_abr,
            CostCenter=CostCenter,
            transport_type=transport_type,
            travel_route=travel_route_abr,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            advance_payment=advance_payment,
            advance_payment_currency=advance_payment_currency_abr,
            employee_level=employee_level,
            application_log=application_log
        )
        settlement_abr = BtApplicationSettlement.objects.create(bt_application_id=Application_abr)
        BtApplicationSettlementInfo.objects.create(
            bt_application_settlement=settlement_abr,
            bt_completed='tak',
            bt_start_date=datetime.datetime(2021, 4, 28),
            bt_start_time=datetime.time(8, 00),
            bt_end_date=datetime.datetime(2021, 4, 28),
            bt_end_time=datetime.time(17, 00),
            advance_payment=settlement_abr.bt_application_id
        )
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement_abr,
            breakfast_quantity=0,
            dinner_quantity=1,
            supper_quantity=1
        )

    def test_trip_duration(self):
        settlement_pl = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja krajowa - test')
        settlement_abr = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja zagraniczna - test')
        result_pl = datetime.datetime(2021, 4, 29, 16, 00) - datetime.datetime(2021, 4, 28, 8, 00)
        print(f'result_pl {result_pl}')
        result_abr = datetime.datetime(2021, 4, 28, 17, 00) - datetime.datetime(2021, 4, 28, 8, 00)
        print(f'result_abr {result_abr}')
        self.assertEqual(trip_duration(settlement_pl), result_pl)
        self.assertEqual(trip_duration(settlement_abr), result_abr)

    def test_get_diet_amount(self):
        settlement_pl = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja krajowa - test')
        settlement_abr = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja zagraniczna - test')
        delegation_rate_pl = float(BtDelegationRate.objects.get(country=settlement_pl.bt_application_id.bt_country).
                                   delagation_rate)
        delegation_rate_abr = float(BtDelegationRate.objects.get(country=settlement_abr.bt_application_id.bt_country).
                                    delagation_rate)

        result_pl = delegation_rate_pl * 1.5
        result_abr = delegation_rate_abr / 2

        self.assertEqual(get_diet_amount_poland(trip_duration(settlement_pl), settlement_pl), result_pl)
        self.assertEqual(get_diet_amount_abroad(trip_duration(settlement_abr), settlement_abr), result_abr)

    def test_def_diet_reconciliation(self):
        settlement_pl = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja krajowa - test')
        settlement_abr = BtApplicationSettlement.objects.get(
            bt_application_id__trip_purpose_text='Delegacja zagraniczna - test')
        delegation_rate_pl = float(BtDelegationRate.objects.get(country=settlement_pl.bt_application_id.bt_country).
                                   delagation_rate)
        delegation_rate_abr = float(BtDelegationRate.objects.get(country=settlement_abr.bt_application_id.bt_country).
                                    delagation_rate)
        diet_pl = delegation_rate_pl * 1.5
        diet_abr = delegation_rate_abr / 2

        breakfasts_pl = settlement_pl.bt_application_settlement_feeding.breakfast_quantity
        dinners_pl = settlement_pl.bt_application_settlement_feeding.dinner_quantity
        suppers_pl = settlement_pl.bt_application_settlement_feeding.supper_quantity

        meals_correction_pl = breakfasts_pl * delegation_rate_pl * 0.25 + dinners_pl*delegation_rate_pl * 0.5 + \
                              suppers_pl*delegation_rate_pl * 0.25
        breakfasts_abr = settlement_abr.bt_application_settlement_feeding.breakfast_quantity
        dinners_abr = settlement_abr.bt_application_settlement_feeding.dinner_quantity
        suppers_abr = settlement_abr.bt_application_settlement_feeding.supper_quantity
        meals_correction_abr = breakfasts_abr * delegation_rate_pl * 0.15 + dinners_abr * delegation_rate_pl * 0.3 + \
                               suppers_abr * delegation_rate_pl * 0.3
        print(f'diet: {diet_pl}meals_correction_pl: {meals_correction_pl}')
        print(f'diet: {diet_abr}meals_correction_pl: {meals_correction_abr}')

        result_pl = diet_pl - meals_correction_pl
        result_abr = diet_abr - meals_correction_abr

        self.assertEqual(diet_reconciliation_poland(
            get_diet_amount_poland(trip_duration(settlement_pl), settlement_pl), settlement_pl), result_pl)
        self.assertEqual(diet_reconciliation_abroad(
            get_diet_amount_abroad(trip_duration(settlement_abr), settlement_abr), settlement_abr), result_abr)
