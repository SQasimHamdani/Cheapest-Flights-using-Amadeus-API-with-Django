from django.db import models

# import os
# from django.conf import settings

class FlightsData(models.Model):
    # departure_city = models.ForeignKey(DepartureCity, on_delete=models.CASCADE)
    # arrival_city = models.ForeignKey(ArrivalCity, on_delete=models.CASCADE)

    departure_city = models.CharField(max_length=200, null=True, blank=True)
    arrival_city = models.CharField(max_length=200, null=True, blank=True)

    departure_date = models.DateField(null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True)

    departure_time = models.TimeField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)

    duration = models.CharField(max_length=200, null=True, blank=True)
    currency = models.CharField(max_length=200, null=True, blank=True)
    price = models.FloatField(max_length=200, null=True, blank=True)

    def __str__(self):
        string = "Flight from {} to {} on day {} costs {}".format(
            self.departure_city,
            self.arrival_city,
            self.departure_date,
            self.price
            )
        return string

class DepartureCity(models.Model):
    departure_city = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.departure_city

class ArrivalCity(models.Model):
    arrival_city = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):
        return self.arrival_city

class Setting(models.Model):
    status_choices = [
        ('Played', 'Played'),
        ('Paused', 'Paused'),
    ]
    Status = models.CharField(max_length=200, null=True, blank=True, choices=status_choices)

    def __str__(self):
        return "Status = "+self.Status