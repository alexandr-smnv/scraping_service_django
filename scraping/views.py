from django.shortcuts import render

from .forms import FindForm
from .models import *


# Create your views here.


def home_view(request):
    form = FindForm()
    city = request.GET.get('city')
    language = request.GET.get('language')
    queryset = []
    if city or language:
        _filter = {}
        if city:
            _filter['city__slug'] = city
        if language:
            _filter['language__slug'] = language

    queryset = Vacancy.objects.filter(**_filter)

    return render(request, 'scraping/home.html', {'object_list': queryset, 'form': form})
