from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from django.views import View

from e_delegacje.enums import BtApplicationStatus
from e_delegacje.forms import BtApplicationForm
from e_delegacje.models import BtUser, BtApplication


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
            result = super().clean()
            trip_category = result['trip_category']
            target_user = result['target_user']
            application_author = result['application_author']
            application_status = BtApplicationStatus.saved.value
            trip_purpose_text = result['trip_purpose_text']
            CostCenter = result['CostCenter']
            transport_type = result['transport_type']
            travel_route = result['travel_route']
            planned_start_date = result['planned_start_date']
            planned_end_date = result['planned_end_date']
            advance_payment = result['advance_payment']
            employee_level = BtUser.objects.get(id=target_user.id)

            BtApplication.objects.create(
                trip_category= trip_category,
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
            form.send_mail(user_mail=request.user.email)
            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))


class BtApplicationListView(ListView):
    model = BtApplication
    template_name = "bt_applications_list.html"

