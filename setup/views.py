from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from setup.models import (
    BtUser,
    BtRegion,
    BtDivision,
    BtLocation,
    BtCostCenter,
    BtMileageRates,
    BtRatesTax,
    BtDepartment,

)


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


class BtDivisionListView(ListView):
    model = BtDivision
    template_name = "division_list_view.html"


class BtDivisionDetailView(DetailView):
    model = BtDivision
    template_name = "division_details_view.html"


class BtLocationListView(ListView):
    model = BtLocation
    template_name = "location_list_view.html"


class BtLocationCreateView(CreateView):
    model = BtLocation
    template_name = "my_name.html"
    fields = "__all__"
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
    success_url = reverse_lazy("setup:mileagerate-create")


class BtRatesTaxListView(ListView):
    model = BtRatesTax
    template_name = "ratetax_list_view.html"


class BtRatesTaxDetailView(DetailView):
    model = BtRatesTax
    template_name = "ratetax_details_view.html"


class BtRatesTaxCreateView(CreateView):
    model = BtRatesTax
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:ratetax-create")


class BtRatesTaxUpdateView(UpdateView):
    model = BtRatesTax
    fields = ("diet_rates","etc", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:ratetax-list-view")


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
