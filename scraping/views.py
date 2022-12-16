from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from .forms import FindForm
from .models import *


def home_view(request):
    form = FindForm()

    return render(request, 'scraping/home.html', {'form': form})


def list_view(request):
    form = FindForm()
    city = request.GET.get('city')
    language = request.GET.get('language')
    context = {'city': city, 'language': language, 'form': form}

    if city or language:
        _filter = {}
        if city:
            _filter['city__slug'] = city
        if language:
            _filter['language__slug'] = language

        queryset = Vacancy.objects.filter(**_filter)
        paginator = Paginator(queryset, 25)

        page_number = request.GET.get('page', 1)

        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            # Если передан тип данных не int
            page_obj = paginator.get_page(1)
        except EmptyPage:
            # Если передана пустая страница
            page_obj = paginator.get_page(paginator.num_pages)

        context['object_list'] = page_obj

    return render(request, 'scraping/list_view.html', context)


