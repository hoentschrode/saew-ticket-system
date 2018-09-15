from django.urls import path
from django.views.generic import TemplateView

app_name = 'closed_for_renovation'
urlpatterns = [
    path('', TemplateView.as_view(template_name='closed_for_renovation/index.html'), name='index')
]
