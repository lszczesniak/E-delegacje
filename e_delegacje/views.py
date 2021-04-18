from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.views import View
import datetime

from django.views.generic.edit import FormMixin

from e_delegacje.enums import BtApplicationStatus
from e_delegacje.forms import (
    BtApplicationForm,
    BtApplicationSettlementInfoForm,
    BtApplicationSettlementCostForm,
    BtApplicationSettlementMileageForm,
    BtApplicationSettlementFeedingForm
)
from e_delegacje.models import (
    BtUser,
    BtApplication,
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    BtApplicationSettlementCost,
    BtApplicationSettlementMileage,
    BtApplicationSettlementFeeding,
)
from setup.models import BtDelegationRate, BtMileageRates


def index(request):
    return render(request, template_name='index_del.html')


class BtApplicationCreateView(View):
    def get(self, request):
        form = BtApplicationForm()
        current_datetime = ""
        return render(request,
                      template_name="form_template.html",
                      context={"form": form, 'current_datetime': current_datetime}
                      )

    def post(self, request):
        form = BtApplicationForm(request.POST)
        if form.is_valid():
            bt_country = form.cleaned_data['bt_country']
            target_user = form.cleaned_data['target_user']
            application_author = form.cleaned_data['application_author']
            application_status = BtApplicationStatus.saved.value
            trip_purpose_text = form.cleaned_data['trip_purpose_text']
            CostCenter = form.cleaned_data['CostCenter']
            transport_type = form.cleaned_data['transport_type']
            travel_route = form.cleaned_data['travel_route']
            planned_start_date = form.cleaned_data['planned_start_date']
            planned_end_date = form.cleaned_data['planned_end_date']
            advance_payment = form.cleaned_data['advance_payment']
            advance_payment_currency = form.cleaned_data['advance_payment_currency']
            employee_level = BtUser.objects.get(id=target_user.id)
            current_datetime = form.cleaned_data['current_datetime']
            application_log = f'Wniosek o delegację utworzony przez: {application_author} - {current_datetime}\n'

            BtApplication.objects.create(
                bt_country=bt_country,
                target_user=target_user,
                application_author=application_author,
                application_status=application_status,
                trip_purpose_text=trip_purpose_text,
                CostCenter=CostCenter,
                transport_type=transport_type,
                travel_route=travel_route,
                planned_start_date=planned_start_date,
                planned_end_date=planned_end_date,
                advance_payment=advance_payment,
                advance_payment_currency=advance_payment_currency,
                employee_level=employee_level,
                application_log=application_log
            )
            # form.send_mail(user_mail=request.user.manager.email)

            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse("e_delegacje:index"))


class BtApplicationListView(ListView):
    model = BtApplication
    template_name = "bt_applications_list.html"


class BtApplicationDetailView(DetailView):
    model = BtApplication
    template_name = "bt_application_details.html"


class BtApplicationApprovalDetailView(View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        advance = float(settlement.bt_application_id.advance_payment)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))

        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = get_diet_amount_poland(trip_duration(settlement), settlement)
        else:
            diet = get_diet_amount_abroad(trip_duration(settlement), settlement)
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs
        if settlement_amount < 0:
            settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}.'
        else:
            settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'
        return render(
            request,
            template_name="bt_application_approval.html",
            context={'object': settlement,
                     'cost_sum': cost_sum,
                     'total_costs': total_costs,
                     'advance': advance,
                     'settlement_amount': settlement_amount,
                     'mileage_cost': mileage_cost,
                     'diet': diet
                     })


class BtApprovalListView(ListView):
    model = BtApplication
    template_name = "bt_approval_list.html"


# Settlement Views
class BtApplicationSettlementView(DetailView):
    template_name = "settlement_form_template.html"
    model = BtApplicationSettlement
    fields = "__all__"
    success_url = reverse_lazy("e_delegacje:applications-list")


class BtApplicationSettlementCreateView(View):

    def get(self, request, pk):
        bt_application = BtApplication.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.create(bt_application_id=bt_application)

        bt_application.application_status = BtApplicationStatus.settlement_in_progress.value
        bt_application.save()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[settlement.id]))


class BtApplicationSettlementsListView(ListView):
    model = BtApplicationSettlement
    template_name = "bt_applications_list.html"


class BtApplicationSettlementDetailView(View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        advance = float(settlement.bt_application_id.advance_payment)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = get_diet_amount_poland(trip_duration(settlement), settlement)
        else:
            diet = get_diet_amount_abroad(trip_duration(settlement), settlement)
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs
        if settlement_amount < 0:
            settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'
        else:
            settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'
        return render(
            request,
            template_name="bt_settlement_send.html",
            context={'object': settlement,
                     'cost_sum': cost_sum,
                     'total_costs': total_costs,
                     'advance': advance,
                     'settlement_amount': settlement_amount,
                     'mileage_cost': mileage_cost,
                     'diet': diet
                     })


def settlement_cost_sum(settlement):
    cost_sum = 0
    cost_list = BtApplicationSettlementCost.objects.filter(bt_application_settlement=settlement)
    for cost in cost_list:
        cost_sum += cost.bt_cost_amount
    return round(cost_sum, 2)


def mileage_cost_sum(settlement):
    mileage_cost = 0
    mileage_cost_list = BtApplicationSettlementMileage.objects.filter(bt_application_settlement=settlement)
    for mileage in mileage_cost_list:
        mileage_cost = mileage_cost + mileage.bt_mileage_rate.rate * mileage.mileage
    return round(mileage_cost, 2)


# Subform create Views
# Create Views
class BtApplicationSettlementInfoCreateFormView(View):

    def get(self, request, pk):
        form = BtApplicationSettlementInfoForm()
        settlement = BtApplicationSettlement.objects.get(id=pk)
        return render(
            request,
            template_name="settlement_subform_info.html",
            context={"form": form, 'settlement': settlement})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementInfoForm(request.POST)
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_completed = form.cleaned_data["bt_completed"]
            bt_start_date = form.cleaned_data["bt_start_date"]
            bt_start_time = form.cleaned_data["bt_start_time"]
            bt_end_date = form.cleaned_data["bt_end_date"]
            bt_end_time = form.cleaned_data["bt_end_time"]
            current_datetime = form.cleaned_data["current_datetime"]
            settlement_log = f'Nowe rozliczenie wniosku nr: {bt_application_settlement.bt_application_id.id} - ' \
                             f'{current_datetime}\n'
            advance_payment = BtApplication.objects.get(
                id=BtApplicationSettlement.objects.get(id=pk).bt_application_id.id
            )
            BtApplicationSettlementInfo.objects.create(
                bt_application_settlement=bt_application_settlement,
                bt_completed=bt_completed,
                bt_start_date=bt_start_date,
                bt_start_time=bt_start_time,
                bt_end_date=bt_end_date,
                bt_end_time=bt_end_time,
                advance_payment=advance_payment,
                settlement_log=settlement_log
            )
            return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:index"))


class BtApplicationSettlementCostCreateView(View):

    def get(self, request, pk):
        form = BtApplicationSettlementCostForm()
        cost_list = BtApplicationSettlementCost.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        settlement = BtApplicationSettlement.objects.get(id=pk)
        return render(
            request,
            template_name="settlement_subform_cost.html",
            context={"form": form, 'cost_list': cost_list, 'settlement': settlement})

    def post(self, request, pk, *args, **kwargs):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementCostForm(request.POST)
        cost_list = BtApplicationSettlementCost.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_cost_category = form.cleaned_data["bt_cost_category"]
            bt_cost_description = form.cleaned_data["bt_cost_description"]
            bt_cost_amount = form.cleaned_data["bt_cost_amount"]
            bt_cost_currency = form.cleaned_data["bt_cost_currency"]
            bt_cost_document_date = form.cleaned_data["bt_cost_document_date"]
            bt_cost_VAT_rate = form.cleaned_data["bt_cost_VAT_rate"]
            BtApplicationSettlementCost.objects.create(
                bt_application_settlement=bt_application_settlement,
                bt_cost_category=bt_cost_category,
                bt_cost_description=bt_cost_description,
                bt_cost_amount=bt_cost_amount,
                bt_cost_currency=bt_cost_currency,
                bt_cost_document_date=bt_cost_document_date,
                bt_cost_VAT_rate=bt_cost_VAT_rate
            )
            return HttpResponseRedirect(reverse("e_delegacje:settlement-cost-create", args=[pk]))
        return render(request, "settlement_subform_cost.html", {"form": form, 'cost_list': cost_list})


class BtApplicationSettlementMileageCreateView(View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementMileageForm()
        trip_list = BtApplicationSettlementMileage.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        return render(
            request,
            template_name="settlement_subform_mileage.html",
            context={"form": form, 'settlement': settlement, 'trip_list': trip_list})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementMileageForm(request.POST)
        trip_list = BtApplicationSettlementMileage.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_car_reg_number = form.cleaned_data["bt_car_reg_number"]
            bt_mileage_rate = form.cleaned_data["bt_mileage_rate"]
            trip_start_place = form.cleaned_data["trip_start_place"]
            trip_date = form.cleaned_data["trip_date"]
            trip_description = form.cleaned_data["trip_description"]
            trip_purpose = form.cleaned_data["trip_purpose"]
            mileage = form.cleaned_data["mileage"]
            BtApplicationSettlementMileage.objects.create(
                bt_application_settlement=bt_application_settlement,
                bt_car_reg_number=bt_car_reg_number,
                bt_mileage_rate=bt_mileage_rate,
                trip_start_place=trip_start_place,
                trip_date=trip_date,
                trip_description=trip_description,
                trip_purpose=trip_purpose,
                mileage=mileage
            )
            return HttpResponseRedirect(reverse("e_delegacje:settlement-mileage-create", args=[pk]))
        return render(request, "settlement_subform_mileage.html", {"form": form, 'trip_list': trip_list})


class BtApplicationSettlementFeedingCreateView(View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementFeedingForm()
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = get_diet_amount_poland(trip_duration(settlement), settlement)
        else:
            diet = get_diet_amount_abroad(trip_duration(settlement), settlement)

        return render(
            request,
            template_name="settlement_subform_feeding.html",
            context={"form": form, 'settlement': settlement, 'diet': diet})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementFeedingForm(request.POST)
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            breakfast_quantity = form.cleaned_data["breakfast_quantity"]
            dinner_quantity = form.cleaned_data["dinner_quantity"]
            supper_quantity = form.cleaned_data["supper_quantity"]
            BtApplicationSettlementFeeding.objects.create(
                bt_application_settlement=bt_application_settlement,
                breakfast_quantity=breakfast_quantity,
                dinner_quantity=dinner_quantity,
                supper_quantity=supper_quantity
            )
            return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        return render(request, "settlement_subform_feeding.html", {"form": form})


def trip_duration(settlement):
    try:
        start_date = settlement.bt_application_info.bt_start_date
        start_time = settlement.bt_application_info.bt_start_time
        end_date = settlement.bt_application_info.bt_end_date
        end_time = settlement.bt_application_info.bt_end_time
        bt_start = datetime.datetime(start_date.year,
                                     start_date.month,
                                     start_date.day,
                                     start_time.hour,
                                     start_time.minute)
        bt_end = datetime.datetime(end_date.year, end_date.month, end_date.day, end_time.hour, end_time.minute)
        print('trip_duration:', bt_end - bt_start)
    except:
        bt_start = datetime.datetime.now()
        bt_end = datetime.datetime.now()
        print(bt_end - bt_start)
    return bt_end - bt_start


def get_diet_amount_poland(bt_duration, settlement):
    diet = 0
    country = settlement.bt_application_id.bt_country
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = 0
            print('pol ponizej doby, ponizej 8h')
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate / 2
            print('pol ponizej doby, od 8h do 12h')
        elif (bt_duration.seconds / 3600) >= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate
            print('pol ponizej doby, ponad 12h')
        else:
            print('pol poniżej żaden if')
    elif bt_duration.days >= 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
            print('pol powyżej doby, ponizej 8h')
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate
            print('pol powyżej doby, od 8h do 12h')
        elif (bt_duration.seconds / 3600) >= 12:
            diet = (bt_duration.days +1) * BtDelegationRate.objects.get(country=country).delagation_rate
            print('pol powyżej doby, ponad 12h')
        else:
            print('pol powyżej żaden if')
    try:
        breakfasts_correction = settlement.bt_application_settlement_feeding.breakfast_quantity * \
                                BtDelegationRate.objects.get(country=country).delagation_rate * 0.25
        dinners_correction = settlement.bt_application_settlement_feeding.dinner_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.5
        suppers_correction = settlement.bt_application_settlement_feeding.supper_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.25
    except:
        breakfasts_correction = 0
        dinners_correction = 0
        suppers_correction = 0
    return round(diet - breakfasts_correction - dinners_correction - suppers_correction, 2)


def get_diet_amount_abroad(bt_duration, settlement):
    country = settlement.bt_application_id.bt_country
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate / 3
            print('z ponizej doby, ponizej 8h')
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate / 2
            print('z ponizej doby, od 8h do 12h')
        elif (bt_duration.seconds / 3600) >= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate
            print('z ponizej doby, ponad 12h')
        else:
            print('poniżej żaden if')
    elif bt_duration.days > 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 3
            print('z powyżej doby, ponizej 8h')
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
            print(f'bt_duration.days {bt_duration.days} * '
                  f'BtDelegationRate{BtDelegationRate.objects.get(country=country).delagation_rate} +'
                  f'BtDelegationRate {BtDelegationRate.objects.get(country=country).delagation_rate}/2')
            print('z powyżej doby, od 8h do 12h')
        elif (bt_duration.seconds / 3600) >= 12:
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
            print('z powyżej doby, ponad 12h')
        else:
            print('z powyżej żaden if')

    try:
        breakfasts_correction = settlement.bt_application_settlement_feeding.breakfast_quantity * \
                                BtDelegationRate.objects.get(country=country).delagation_rate * 0.15
        dinners_correction = settlement.bt_application_settlement_feeding.dinner_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.30
        suppers_correction = settlement.bt_application_settlement_feeding.supper_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.30
    except:
        breakfasts_correction = 0
        dinners_correction = 0
        suppers_correction = 0
    return round(diet - breakfasts_correction - dinners_correction - suppers_correction, 2)


# Delete Views
class BtApplicationDeleteView(DeleteView):
    model = BtApplication
    template_name = "bt_application_delete.html"
    success_url = reverse_lazy("e_delegacje:index")


class BtApplicationSettlementCostDeleteView(View):

    def post(self, request, pk, *args, **kwargs):
        item_to_be_deleted = BtApplicationSettlementCost.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.get(id=item_to_be_deleted.bt_application_settlement.id)
        item_to_be_deleted.delete()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-cost-create", args=[settlement.id]))


class BtApplicationSettlementMileageDeleteView(View):

    def post(self, request, pk, *args, **kwargs):
        item_to_be_deleted = BtApplicationSettlementMileage.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.get(id=item_to_be_deleted.bt_application_settlement.id)
        item_to_be_deleted.delete()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-mileage-create", args=[settlement.id]))


# UpdateViews
class BtApplicationSettlementInfoUpdateView(FormMixin, View):
    def get_initial(self):
        initial = super(BtApplicationSettlementInfoUpdateView, self).get_initial()
        print('initial data', initial)
        bt_application_settlement_info = self.get_object()
        initial['bt_completed'] = bt_application_settlement_info.bt_completed,
        initial['bt_start_date'] = bt_application_settlement_info.bt_start_date,
        initial['bt_start_time'] = bt_application_settlement_info.bt_start_time,
        initial['bt_end_date'] = bt_application_settlement_info.bt_end_date,
        initial['bt_end_time'] = bt_application_settlement_info.bt_end_time
        return initial

    def get_object(self, *args, **kwargs):
        settlement_info = get_object_or_404(BtApplicationSettlementInfo, pk=self.kwargs['pk'])
        return settlement_info

    def get(self, request, pk):
        form = BtApplicationSettlementInfoForm(request.GET, initial=self.get_initial())
        settlement = BtApplicationSettlement.objects.get(id=pk)
        return render(
            request,
            template_name="settlement_subform_info.html",
            context={"form": form, 'settlement': settlement})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementInfoForm(request.POST)
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_application_settlement_info = BtApplicationSettlementInfo.objects.get(
                bt_application_settlement=bt_application_settlement)
            bt_application_settlement_info.bt_completed = form.cleaned_data["bt_completed"]
            bt_application_settlement_info.bt_start_date = form.cleaned_data["bt_start_date"]
            bt_application_settlement_info.bt_start_time = form.cleaned_data["bt_start_time"]
            bt_application_settlement_info.bt_end_date = form.cleaned_data["bt_end_date"]
            bt_application_settlement_info.bt_end_time = form.cleaned_data["bt_end_time"]
            bt_application_settlement_info.save()
            return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:index"))
