from django.urls import path

from .views.dashboard import DashboardTemplateView


app_name = 'admin'

urlpatterns = [
    path('', DashboardTemplateView.as_view(), name='dashboard'),
]
