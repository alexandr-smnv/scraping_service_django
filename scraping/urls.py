from django.urls import path

from scraping import views


urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('list/', views.list_view, name='list'),
]
