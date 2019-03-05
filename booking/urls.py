from django.urls import path
from . import views

app_name = 'booking'
urlpatterns = [
    path('', views.BookingView.as_view(), name='index'),
    path('<str:booking_code>/confirmation/', views.confirmation, name='confirmation'),
    path('<str:ticket_code>/pdf/', views.pdf_view, name='pdf'),
    path('<str:ticket_code>/verify', views.VerificationView.as_view(), name='verify'),
    path('<str:booking_code>/resend_mail/', views.ResendConfirmationMail.as_view(), name='resend')
]
