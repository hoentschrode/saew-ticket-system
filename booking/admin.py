from django.contrib import admin

from .models import Performance, Booking

admin.site.register([Performance, Booking])
