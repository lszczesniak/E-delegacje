import functools
import ssl

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.views import View
import datetime
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django_weasyprint.utils import django_url_fetcher
from e_delegacje.my_functions import new_application_notification, approved_or_rejected_notification
from e_delegacje.enums import BtApplicationStatus
from e_delegacje.forms import (
    BtApplicationForm,
    BtApplicationSettlementInfoForm,
    BtApplicationSettlementCostForm,
    BtApplicationSettlementMileageForm,
    BtApplicationSettlementFeedingForm,
    BtApplicationSettlementInfoFormset,
    BtApplicationSettlementFeedingFormset,
    BtRejectionForm,
    BtApprovedForm
)
from e_delegacje.models import (
    BtApplication,
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    BtApplicationSettlementCost,
    BtApplicationSettlementMileage,
    BtApplicationSettlementFeeding,
)
from setup.models import BtDelegationRate, BtMileageRates, BtUser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import CONTENT_TYPE_PNG, WeasyTemplateResponse
from django.core.files.storage import FileSystemStorage


@login_required
def index(request):
    applications = BtApplication.objects.all()
    items_number = BtApplication.objects.filter(application_author=request.user).count() + \
                   BtApplication.objects.filter(target_user=request.user).exclude(
                       application_author=request.user).count()
    approval_items = BtApplication.objects.filter(
        application_status=BtApplicationStatus.in_progress.value).filter(
        target_user__manager=request.user).count() + BtApplicationSettlement.objects.filter(
        settlement_status=BtApplicationStatus.in_progress.value).count()
    return render(request, template_name='index_del.html', context={'applications': applications,
                                                                    'items_number': items_number,
                                                                    'approval_items': approval_items})


class BtApplicationCreateView(View):
    def get(self, request):
        form = BtApplicationForm()
        form.fields['target_user'].queryset = \
            BtUser.objects.filter(department=request.user.department)

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
            application_author = self.request.user
            application_status = BtApplicationStatus.in_progress.value
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
            new_application_notification(user_mail=target_user.manager.email, sent_app=BtApplication.objects.last())

            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse("e_delegacje:applications-create"))


class BtApplicationListView(ListView):
    model = BtApplication
    template_name = "bt_applications_list.html"
    ordering = ['-id']


class BtApplicationDetailView(DetailView):
    model = BtApplication
    template_name = "bt_application_details.html"

class BtApplicationApprovalDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):

        application = BtApplication.objects.get(id=pk)
        rejected_form = BtRejectionForm()
        approved_form = BtApprovedForm()
        try:
            set_pk = application.bt_applications_settlements.id
            settlement = BtApplicationSettlement.objects.get(id=set_pk)
            advance = float(settlement.bt_application_id.advance_payment)
            cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
                diet = diet_reconciliation_poland(settlement)
            else:
                diet = diet_reconciliation_abroad(settlement)
            total_costs = cost_sum + mileage_cost + diet
            settlement_amount = round(advance - total_costs, 2)
            if settlement_amount < 0:
                settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text}.'
            else:
                settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text}'
            return render(
                request,
                template_name="bt_application_approval.html",
                context={
                    'application': application,
                    'cost_sum': round(cost_sum, 2),
                    'total_costs': round(total_costs, 2),
                    'advance': advance,
                    'settlement_amount': settlement_amount,
                    'mileage_cost': mileage_cost,
                    'diet': diet,
                    'rejected_form': rejected_form,
                    'approved_form': approved_form
                })
        except:
            return render(
                request,
                template_name="bt_application_approval.html",
                context={'application': application, 'rejected_form': rejected_form, 'approved_form': approved_form})

    def post(self, request, pk):
        rejected_form = BtRejectionForm(request.POST)
        if rejected_form.is_valid():
            bt_application = BtApplication.objects.get(id=pk)
            try:
                settlement = BtApplicationSettlement.objects.get(id=bt_application.bt_applications_settlements.id)
                settlement.settlement_status = BtApplicationStatus.rejected.value
                settlement.save()
                bt_application.application_log = \
                    bt_application.application_log + \
                    f"\n-----\nRozliczenie odrzucone przez {request.user.first_name} " \
                    f"{request.user.last_name}.\n\n Powód: " \
                    f"{rejected_form.cleaned_data['application_log']}.\n-----\n"
                bt_application.save()
                return HttpResponseRedirect(reverse("e_delegacje:approval-list"))
            except ObjectDoesNotExist:
                bt_application.application_status = BtApplicationStatus.rejected.value
                bt_application.application_log = bt_application.application_log + \
                                                 f"\n-----\nWniosek odrzucony przez {request.user.first_name} " \
                                                 f"{request.user.last_name}.\n\n Powód: " \
                                                 f"{rejected_form.cleaned_data['application_log']}.\n-----\n"
                bt_application.save()
                return HttpResponseRedirect(reverse("e_delegacje:approval-list"))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:approval", args=[pk]))
            
        approved_or_rejected_notification()


class BtApplicationApprovalMailDetailView(View):

    def get(self, request, pk):
        application = BtApplication.objects.get(id=pk)
        try:
            set_pk = application.bt_applications_settlements.id
            settlement = BtApplicationSettlement.objects.get(id=set_pk)
            advance = float(settlement.bt_application_id.advance_payment)
            cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
                diet = diet_reconciliation_poland(settlement)
            else:
                diet = diet_reconciliation_abroad(settlement)
            total_costs = cost_sum + mileage_cost + diet
            settlement_amount = round(advance - total_costs, 2)
            if settlement_amount < 0:
                settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.code}.'
            else:
                settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.code}'
            return render(
                request,
                template_name="bt_approval_mail_detail.html",
                context={
                    'application': application,
                    'cost_sum': round(cost_sum, 2),
                    'total_costs': round(total_costs, 2),
                    'advance': advance,
                    'settlement_amount': settlement_amount,
                    'mileage_cost': mileage_cost,
                    'diet': diet
                })
        except:
            return render(
                request,
                template_name="bt_approval_mail_detail.html",
                context={'application': application})


class BtApplicationUpdateView(UpdateView):
    model = BtApplication
    template_name = "form_template.html"
    form_class = BtApplicationForm
    success_url = reverse_lazy("e_delegacje:applications-list")

    def post(self, request, *args, **kwargs):
        application = self.get_object()

        form = BtApplicationForm(request.POST)
        if form.is_valid():
            application.bt_country = form.cleaned_data['bt_country']
            application.target_user = form.cleaned_data['target_user']
            application.application_status = BtApplicationStatus.in_progress.value
            application.trip_purpose_text = form.cleaned_data['trip_purpose_text']
            application.CostCenter = form.cleaned_data['CostCenter']
            application.transport_type = form.cleaned_data['transport_type']
            application.travel_route = form.cleaned_data['travel_route']
            application.planned_start_date = form.cleaned_data['planned_start_date']
            application.planned_end_date = form.cleaned_data['planned_end_date']
            application.advance_payment = form.cleaned_data['advance_payment']
            application.advance_payment_currency = form.cleaned_data['advance_payment_currency']
            application.current_datetime = form.cleaned_data['current_datetime']
            application.application_log = application.application_log + \
                              f'Wniosek o delegację poprawiony przez: {request.user.first_name} ' \
                              f'{request.user.last_name} - {application.current_datetime}\n'
            application.save()
            # form.send_mail(user_mail=target_user.manager.email, sent_app=BtApplication.objects.last())

            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse("e_delegacje:index"))


def bt_application_approved(request, pk):
    bt_application = BtApplication.objects.get(id=pk)
    if bt_application.application_status == BtApplicationStatus.in_progress.value:
        bt_application.application_status = BtApplicationStatus.approved.value
        bt_application.application_log = \
            bt_application.application_log + \
            f"\nWniosek zaakceptowany przez {request.user.first_name} {request.user.last_name} "

        bt_application.save()
    else:
        return render(request, template_name='already_processed.html', context={'application': bt_application})

    # return render(request, template_name='approve_reject_success.html', context={'application': bt_application})
    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def bt_application_rejected(request, pk):
    bt_application = BtApplication.objects.get(id=pk)
    if bt_application.application_status == BtApplicationStatus.in_progress.value:
        bt_application.application_status = BtApplicationStatus.rejected.value
        bt_application.application_log = \
            bt_application.application_log + \
            f"\nWniosek odrzucony przez {request.user.first_name} {request.user.last_name} \n\n" \
            f"Powód: "
        bt_application.save()
    else:
        return render(request, template_name='already_processed.html', context={'application': bt_application})

    return render(request, template_name='approve_reject_success.html', context={'application': bt_application})
    # return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def send_settlement_to_approver(request, pk):
    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.in_progress.value
    settlement.save()
    return HttpResponseRedirect(reverse("e_delegacje:applications-list"))


def bt_settlement_approved(request, pk):
    bt_application = BtApplication.objects.get(bt_applications_settlements__id=pk)
    bt_application.application_status = BtApplicationStatus.settled.value
    bt_application.approver = request.user
    bt_application.approval_date = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    bt_application.save()

    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.approved.value
    settlement.save()

    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def bt_settlement_rejected(request, pk):
    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.rejected.value
    settlement.save()

    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


class BtApprovalListView(LoginRequiredMixin, ListView):
    model = BtApplication
    template_name = "bt_approval_list.html"
    ordering = ['-id']

    def get_queryset(self):
        return BtApplication.objects.filter(
            application_status=BtApplicationStatus.in_progress.value).filter(
            target_user__manager=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settlements'] = BtApplicationSettlement.objects.filter(
            settlement_status=BtApplicationStatus.in_progress.value)
        return context


# Settlement Views

class BtApplicationSettlementCreateView(View):

    def get(self, request, pk):
        bt_application = BtApplication.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.create(
            bt_application_id=bt_application,
            settlement_status=BtApplicationStatus.saved.value
        )
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement,
            breakfast_quantity=0,
            dinner_quantity=0,
            supper_quantity=0
        )
        bt_application.application_status = BtApplicationStatus.settlement_in_progress.value
        bt_application.save()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[settlement.id]))

    def post(self, request, pk):
        bt_application = BtApplication.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.create(
            bt_application_id=bt_application,
            settlement_status=BtApplicationStatus.saved.value
        )
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement,
            breakfast_quantity=0,
            dinner_quantity=0,
            supper_quantity=0
        )
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
            diet = round(diet_reconciliation_poland(settlement), 2)
        else:
            diet = round(diet_reconciliation_abroad(settlement), 2)
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs
        if settlement_amount < 0:
            settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.text}'
        else:
            settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.text}'
        return render(
            request,
            template_name="bt_settlement_details.html",
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
            if form.cleaned_data["bt_completed"] == 'nie':

                bt_application_settlement.bt_application_id.application_status = BtApplicationStatus.canceled
                bt_application_settlement.bt_application_id.save()
                bt_application_settlement.delete()
                # return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
                return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
            else:
                bt_completed = form.cleaned_data["bt_completed"]
                bt_start_date = form.cleaned_data["bt_start_date"]
                bt_start_time = form.cleaned_data["bt_start_time"]
                bt_end_date = form.cleaned_data["bt_end_date"]
                bt_end_time = form.cleaned_data["bt_end_time"]
                settlement_exchange_rate = form.cleaned_data['settlement_exchange_rate']
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
                    settlement_exchange_rate=settlement_exchange_rate,
                    advance_payment=advance_payment,
                    settlement_log=settlement_log
                )
                return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:settlement-info-create", args=[pk]))


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
        form = BtApplicationSettlementCostForm(request.POST, request.FILES)
        cost_list = BtApplicationSettlementCost.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        uploaded_file = request.FILES.get('attachment')

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
                bt_cost_VAT_rate=bt_cost_VAT_rate,
                attachment=uploaded_file
            )

            return HttpResponseRedirect(reverse("e_delegacje:settlement-cost-create", args=[pk]))
        return render(request, "settlement_subform_cost.html", {"form": form,
                                                                'cost_list': cost_list,
                                                                'settlement': settlement}
                      )


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
            diet_rate = BtDelegationRate.objects.get(country=settlement.bt_application_id.bt_country).delagation_rate
            diet_amount = get_diet_amount_poland(settlement)  # dieta bez odliczeń
            diet = diet_reconciliation_poland(settlement)  # dieta bez odliczeń po korekcie o wyżywienie
        else:
            diet_rate = BtDelegationRate.objects.get(country=settlement.bt_application_id.bt_country).delagation_rate
            diet_amount = get_diet_amount_abroad(settlement)  # dieta bez odliczeń
            diet = diet_reconciliation_poland(settlement)  # dieta bez odliczeń po korekcie o wyżywienie
        return render(
            request,
            template_name="settlement_subform_feeding.html",
            context={"form": form,
                     'settlement': settlement,
                     'diet': diet,
                     'diet_amount': diet_amount,
                     'diet_rate': diet_rate
                     }
        )

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
    except:
        bt_start = datetime.datetime.now()
        bt_end = datetime.datetime.now()
    # print(f'{settlement.bt_application_id.trip_purpose_text} trip duration: {bt_end - bt_start}')
    return bt_end - bt_start


def get_diet_amount_poland(settlement):
    bt_duration = trip_duration(settlement)
    diet = 0
    country = settlement.bt_application_id.bt_country
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = 0
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif (bt_duration.seconds / 3600) >= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('pol poniżej żaden if')
    elif bt_duration.days >= 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif 8 < (bt_duration.seconds / 3600):
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        # elif (bt_duration.seconds / 3600) >= 12:
        #     diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        # else:
        #     print('pol powyżej żaden if')
    return diet


def diet_reconciliation_poland(settlement):
    diet = get_diet_amount_poland(settlement)
    country = settlement.bt_application_id.bt_country
    if diet > 0:
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
    else:
        return 0


def get_diet_amount_abroad(settlement):
    bt_duration = trip_duration(settlement)
    country = settlement.bt_application_id.bt_country
    diet = 0
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 3
        elif 8 < (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif (bt_duration.seconds / 3600) > 12:
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('poniżej żaden if')

    elif bt_duration.days >= 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 3
        elif 8 < (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif 12 < (bt_duration.seconds / 3600):
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('z powyżej żaden if')
    return diet


def diet_reconciliation_abroad(settlement):
    diet = get_diet_amount_abroad(settlement)
    country = settlement.bt_application_id.bt_country
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
    success_url = reverse_lazy("e_delegacje:applications-list")


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
class BtApplicationSettlementInfoUpdateView(SingleObjectMixin, FormView):
    model = BtApplicationSettlementInfo
    template_name = "settlement_subform_info.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())

        result = self.get_form().cleaned_data
        bt_completed = result[0]['bt_completed']
        print('bt completed jest: ', bt_completed)
        if bt_completed == 'nie':
            self.object.bt_application_id.application_status = BtApplicationStatus.canceled
            self.object.bt_application_id.save()
            self.object.delete()
            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))

        else:
            return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return BtApplicationSettlementInfoFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Zmiany zostąły zapisane"
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("e_delegacje:settlement-details", kwargs={'pk': self.object.id})


class BtApplicationSettlementFeedingUpdateView(SingleObjectMixin, FormView):
    model = BtApplicationSettlementFeeding
    template_name = "settlement_subform_feeding.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return BtApplicationSettlementFeedingFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("e_delegacje:settlement-details", kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settlement = BtApplicationSettlement.objects.get(id=self.object.id)
        diet_amount = get_diet_amount_poland(settlement)

        context['settlement'] = settlement
        context['diet_amount'] = diet_amount
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            context['diet'] = round(diet_reconciliation_poland(settlement), 2)
            context['diet_rate'] = BtDelegationRate.objects.get(
                country=settlement.bt_application_id.bt_country
            ).delagation_rate
        else:
            context['diet'] = round(diet_reconciliation_abroad(settlement), 2)
            context['diet_rate'] = BtDelegationRate.objects.get(
                country=settlement.bt_application_id.bt_country
            ).delagation_rate
        return context


class CreatePDF(DetailView):
    model = BtApplication
    template_name = 'PDF.html'
    target = '_blank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        settlement = BtApplicationSettlement.objects.get(id=application.bt_applications_settlements.id)
        advance = float(application.advance_payment)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = round(diet_reconciliation_poland(settlement), 2)
        else:
            diet = round(diet_reconciliation_abroad(settlement), 2)
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs
        if settlement_amount < 0:
            settlement_amount = f'Do zwrotu dla pracownika: {abs(round(settlement_amount, 4))} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'
        else:
            settlement_amount = f'Do zapłaty przez pracownika: {round(settlement_amount, 4)} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'

        context['settlement_amount'] = settlement_amount
        context['cost_sum'] = cost_sum
        context['total_costs'] = total_costs
        context['diet'] = diet
        context['mileage_cost'] = mileage_cost

        return context


def render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    get_object_or_404(BtApplication, pk=pk)
    application = get_object_or_404(BtApplication, pk=pk)
    settlement = BtApplicationSettlement.objects.get(id=application.bt_applications_settlements.id)
    advance = float(application.advance_payment)
    cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
    mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
    if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
        diet = round(diet_reconciliation_poland(settlement), 2)
    else:
        diet = round(diet_reconciliation_abroad(settlement), 2)
    total_costs = cost_sum + mileage_cost + diet
    settlement_amount = advance - total_costs
    if settlement_amount < 0:
        settlement_amount = f'Do zwrotu dla pracownika: {abs(round(settlement_amount, 4))} ' \
                            f'{settlement.bt_application_id.advance_payment_currency.code}'
    else:
        settlement_amount = f'Do zapłaty przez pracownika: {round(settlement_amount, 4)} ' \
                            f'{settlement.bt_application_id.advance_payment_currency.code}'
    context = {'object': application,
               'settlement_amount': settlement_amount,
               'cost_sum': cost_sum,
               'total_costs': total_costs,
               'diet': diet,
               'mileage_cost': mileage_cost
               }

    template_path = 'PDF.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download get this code
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display get this code
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class CustomWeasyTemplateResponse(WeasyTemplateResponse):
    # customized response class to change the default URL fetcher
    def get_url_fetcher(self):
        # disable host and certificate check
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return functools.partial(django_url_fetcher, ssl_context=context)


class PrintInLinePDFView(WeasyTemplateResponseMixin, CreatePDF):
    # output of MyModelView rendered as PDF with hardcoded CSS

    pdf_stylesheets = [
        settings.STATICFILES_DIRS[0] + '/css/bootstrap.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False

    response_class = CustomWeasyTemplateResponse

    def get_pdf_filename(self):
        obj = CreatePDF.get_object(self)
        return f'Rozliczenie delegacji nr: {obj.id}.pdf'


class DownloadPDFView(WeasyTemplateResponseMixin, CreatePDF):
    # suggested filename (is required for attachment/download!)
    pdf_stylesheets = [
        settings.STATICFILES_DIRS[0] + '/css/bootstrap.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = True
    # custom response class to configure url-fetcher
    response_class = CustomWeasyTemplateResponse

    def get_pdf_filename(self):
        obj = CreatePDF.get_object(self)
        return f'Rozliczenie delegacji nr: {obj.id}.pdf'
