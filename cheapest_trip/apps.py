from django.apps import AppConfig


class CheapestTripConfig(AppConfig):
    name = 'cheapest_trip'

    def ready(self):
        from AmaduesAPI import schedular
        schedular.start()