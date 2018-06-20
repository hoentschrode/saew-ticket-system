from django.urls import path
from . import views

app_name = 'booking'
urlpatterns = [
    path('', views.BookingView.as_view(), name='index'),
    path('<str:booking_code>/confirmation/', views.confirmation, name='confirmation'),
    path('<str:ticket_code>/pdf/', views.pdf_view, name='pdf'),
    path('services/', views.ServiceView.as_view(), name='services'),
    path('policies/', views.PolicyView.as_view(), name='policies'),
    path('<str:ticket_code>/verify', views.VerificationView.as_view(), name='verify')
]
