from django.shortcuts import render


def index(request):
    return render(request, template_name='index_del.html')
    # return render(request, template_name='example_navbars.html')
