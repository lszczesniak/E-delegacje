from django.urls import path
from e_delegacje.views import index
app_name = 'e_delegacje'
urlpatterns = [

    path('', index, name='home'),

    ]
