from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, CreateView
from django.views import View
from e_delegacje.enums import BtApplicationStatus
from e_delegacje.forms import BtApplicationForm, BtApplicationSettlementInfoForm
from e_delegacje.models import (
    BtUser,
    BtApplication,
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    BtApplicationSettlementCost,
    BtApplicationSettlementMileage,
    BtApplicationSettlementFeeding,
    )


def index(request):
    return render(request, template_name='index_del.html')
    # return render(request, template_name='example_navbars.html')


class BtApplicationCreateView(View):
    def get(self, request):
        form = BtApplicationForm()
        return render(request, template_name="form_template.html", context={"form": form})

    def post(self, request):
        form = BtApplicationForm(request.POST)
        if form.is_valid():
            trip_category = form.cleaned_data['trip_category']
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
            employee_level = BtUser.objects.get(id=target_user.id)

            BtApplication.objects.create(
                trip_category=trip_category,
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
                employee_level=employee_level,
            )
            # form.send_mail(user_mail=request.user.email)
            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:index"))


class BtApplicationListView(ListView):
    model = BtApplication
    template_name = "bt_applications_list.html"


class BtApplicationDetailView(DetailView):
    model = BtApplication
    template_name = "bt_application_details.html"


class BtApplicationDeleteView(DeleteView):
    model = BtApplication
    template_name = "bt_application_delete.html"


class BtApplicationSettlementView(DetailView):
    template_name = "settlement_form_template.html"
    model = BtApplicationSettlement
    fields = "__all__"
    success_url = reverse_lazy("e_delegacje:applications-list")


class BtApplicationSettlementCreateView(View):
    def get(self, request, pk):
        # if BtApplicationSettlement.object.get(bt_application_id=pk).exists():
        #     raise Exception("Rozliczenie już istnieje")
        # else:
        settlement = BtApplicationSettlement.objects.create(bt_application_id=BtApplication.objects.get(id=pk))
        settlement.save()
        settlement_id = BtApplicationSettlement.objects.last()

        return HttpResponseRedirect(reverse("e_delegacje:settlement-add-forms", args=[settlement_id.id]))


class BtApplicationSettlementsListView(ListView):
    model = BtApplicationSettlement
    template_name = "bt_applications_list.html"


class BtApplicationSettlementDetailView(DetailView):

    model = BtApplicationSettlement
    template_name = "bt_settlement_details.html"
    extra_context = {'info_form': BtApplicationSettlementInfoForm}


class BtApplicationSettlementInfoCreateView(CreateView):
    template_name = "settlement_subform.html"
    model = BtApplicationSettlementInfo
    fields = "__all__"


class BtApplicationSettlementCostCreateView(CreateView):
    template_name = "settlement_subform.html"
    model = BtApplicationSettlementCost
    fields = "__all__"


class BtApplicationSettlementMileageCreateView(CreateView):
    template_name = "settlement_subform.html"
    model = BtApplicationSettlementMileage
    fields = "__all__"


class BtApplicationSettlementFeedingCreateView(CreateView):
    template_name = "settlement_subform.html"
    model = BtApplicationSettlementFeeding
    fields = "__all__"