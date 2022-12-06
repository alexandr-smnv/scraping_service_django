from django.urls import path

from scraping import views


urlpatterns = [
    path('home/', views.home_view),
]
