from django.views.generic import TemplateView


class DashboardTemplateView(TemplateView):
    template_name = 'admin/dashboard.html'
