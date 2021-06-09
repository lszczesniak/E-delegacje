from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.contrib import messages
from setup.forms import LoginForm, BtUserCreationForm, LocationForm
from django.shortcuts import render, redirect
from setup.models import (
    BtUser,
    BtRegion,
    BtDivision,
    BtLocation,
    BtCostCenter,
    BtMileageRates,
    BtDelegationRate,
    BtDepartment,

)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            # entered_usr = BtUser.objects.get(username=cd['username'])
            # user = authenticate(request, username=entered_usr.username, password=cd['password'])
            user = form.get_user()
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('e_delegacje:index'))
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                print(f'user {form.cleaned_data["username"]} is none')
        else:
            for item in form.errors:
                print(f'form errors: {item}')
    else:

        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
#    messages.info(request, "logged successfylly!")
    return redirect('setup:login')


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('setup:password-change-done')


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_change_done.html'


class BtUserCreateView(CreateView):
    model = BtUser
    template_name = "my_name.html"
    form_class = BtUserCreationForm
    # fields = "__all__"
    success_url = reverse_lazy("setup:user-list-view")


class BtUserListView(ListView):
    model = BtUser
    template_name = "user_list_view.html"


class BtUserDetailView(DetailView):
    model = BtUser
    template_name = "user_details_view.html"


class BtRegionListView(ListView):
    model = BtRegion
    template_name = "region_list_view.html"


class BtRegionDetailView(DetailView):
    model = BtRegion
    template_name = "region_details_view.html"


class BtRegionUpdateView(UpdateView):
    model = BtRegion
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:region-list-view")


class BtRegionCreateView(CreateView):
    model = BtRegion
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:region-create")


class BtDivisionListView(ListView):
    model = BtDivision
    template_name = "division_list_view.html"


class BtDivisionDetailView(DetailView):
    model = BtDivision
    template_name = "division_details_view.html"


class BtDivisionUpdateView(UpdateView):
    model = BtDivision
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:division-list-view")


class BtDivisionCreateView(CreateView):
    model = BtDivision
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:division-create")


class BtLocationListView(ListView):
    model = BtLocation
    template_name = "location_list_view.html"


class BtLocationCreateView(CreateView):
    model = BtLocation
    template_name = "my_name.html"
    form_class = LocationForm
#    fields = "__all__"
    success_url = reverse_lazy("setup:location-create")


class BtLocationDetailView(DetailView):
    model = BtLocation
    template_name = "location_details_view.html"


class BtCostCenterListView(ListView):
    model = BtCostCenter
    template_name = "costcenter_list_view.html"


class BtCostCenterDetailView(DetailView):
    model = BtCostCenter
    template_name = "costcenter_details_view.html"


class BtCostCenterCreateView(CreateView):
    model = BtCostCenter
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:costcenter-create")


class BtMileageRatesListView(ListView):
    model = BtMileageRates
    template_name = "mileagetate_list_view.html"


class BtMileageRatesDetailView(DetailView):
    model = BtMileageRates
    template_name = "mileagetate_details_view.html"


class BtMileageRatesCreateView(CreateView):
    model = BtMileageRates
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:mileagetate-create")


class BtDelegationRateListView(ListView):
    model = BtDelegationRate
    template_name = "delegationrate_list_view.html"


class BtDelegationRateDetailView(DetailView):
    model = BtDelegationRate
    template_name = "delegationrate_details_view.html"


class BtDelegationRateCreateView(CreateView):
    model = BtDelegationRate
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:delegationrate-create")


class BtDelegationRateUpdateView(UpdateView):
    model = BtDelegationRate
    fields = ("delegation_rate","alpha_code", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:delegationrate-list-view")


class BtDepartmentListView(ListView):
    model = BtDepartment
    template_name = "department_list_view.html"


class BtDepartmentDetailView(DetailView):
    model = BtDepartment
    template_name = "department_details_view.html"


class BtDepartmentCreateView(CreateView):
    model = BtDepartment
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:department-create")


class BtDepartmentUpdateView(UpdateView):
    model = BtDepartment
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:department-list-view")
