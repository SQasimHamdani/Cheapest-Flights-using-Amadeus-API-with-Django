from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(FlightsData)
admin.site.register(DepartureCity)
admin.site.register(ArrivalCity)
admin.site.register(Setting)