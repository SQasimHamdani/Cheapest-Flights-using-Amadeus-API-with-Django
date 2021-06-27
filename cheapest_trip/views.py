from django.contrib import messages
from django.shortcuts import redirect, render

from .models import FlightsData, DepartureCity, ArrivalCity, Setting
from datetime import datetime, timedelta
from AmaduesAPI.ArrivalCitiesLoader import read_cities
from AmaduesAPI.AmadeusApi import update_flights

from django.http import HttpResponse, JsonResponse

import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# from django.conf import settings as django_settings


def home(request):

    # startdate = date.today()
    # enddate = startdate + timedelta(days=6)
    # Sample.FlightsData.filter(departure_time__range=[startdate, enddate])

    today = datetime.today()
    future_dates = today + timedelta(days=0)

    query = FlightsData.objects.filter(
        departure_date__gte=future_dates,
    )
    query_total = query
    # query = FlightsData.objects.all()
    # print(len(query))
    settings = Setting.objects.all()[0]
    message = settings.Status
    print("Get", message)

    page = request.GET.get("page", 1)

    paginator = Paginator(query, 20)

    try:
        query = paginator.page(page)
    except PageNotAnInteger:
        query = paginator.page(1)
    except EmptyPage:
        query = paginator.page(paginator.num_pages)

    response = {
        "flights": query,
        "total_flights": query_total,
        "settings": settings,
    }

    return render(request, "cheapest_trip/home.html", response)


def change_status(request):
    message = ""
    if request.method == "POST":
        print(request.POST.get("Status"))

        settings = Setting.objects.all()[0]

        if settings.Status == "Paused":
            settings.Status = "Played"
            settings.save()

        elif settings.Status == "Played":
            settings.Status = "Paused"
            settings.save()

        message = "Success"

    if request.method == "GET":
        settings = Setting.objects.all()[0]
        message = settings.Status
        print("Get", message)

    data = {"message": message}
    # return JsonResponse(data)
    return HttpResponse(json.dumps(message), content_type="application/json")


def search(request):

    # startdate = date.today()
    # enddate = startdate + timedelta(days=6)
    # Sample.FlightsData.filter(departure_time__range=[startdate, enddate])
    settings = Setting.objects.all()[0]
    if request.method == "POST":

        try:
            Departure = request.POST.get("Departure").upper()
            Arrival = request.POST.get("Arrival").upper()
            DepartureDate = request.POST.get("DepartureDate")
            # print(DepartureDate)

            today = datetime.today()
            future_dates = today + timedelta(days=0)

            if int(DepartureDate.split("-")[2]) > 10:
                future_dates = future_dates.replace(
                    day=1,
                    month=int(DepartureDate.split("-")[1]) + 1,
                    year=int(DepartureDate.split("-")[0]),
                )

            else:
                future_dates = future_dates.replace(
                    day=1,
                    month=int(DepartureDate.split("-")[1]),
                    year=int(DepartureDate.split("-")[0]),
                )
            # print("Future Dates",future_dates)

            if len(Arrival) > 0:
                query = FlightsData.objects.filter(
                    departure_date__gte=future_dates,
                    departure_city=Departure,
                    arrival_city=Arrival,
                ).order_by("departure_date")
            else:
                query = FlightsData.objects.filter(
                    departure_date__gte=future_dates,
                    departure_city=Departure,
                ).order_by("departure_date")

        except EOFError:
            print("Error", EOFError)
            return redirect("search")
        # query = FlightsData.objects.all()
        # print(len(query))

        response = {
            "flights": query,
            "total_flights": query,
            "settings": settings,
        }

        return render(request, "cheapest_trip/home.html", response)

    else:
        response = {
            "home": "active",
            "settings": settings,
        }

        return render(request, "cheapest_trip/search.html", response)


def update_flights_record(request):

    update_flights()

    flights = ""

    response = {
        "flights": flights,
    }
    return render(request, "cheapest_trip/temp_file.html", response)


def arrival_cities_loader(request):

    file_path = r"AmaduesAPI\ArrivalCities.txt"
    arrival_cites = read_cities(file_path)
    # print(arrival_cites)
    new_added_arrivals = []
    for arrival_city in arrival_cites:
        query = ArrivalCity.objects.filter(arrival_city=arrival_city)
        if len(query) == 0:
            form = ArrivalCity()
            form.arrival_city = arrival_city
            form.save()
            new_added_arrivals.append(arrival_city)
        else:
            print("arrival city already in databse", arrival_city)

    settings = Setting.objects.all()[0]
    message = settings.Status
    print("Get", message)

    response = {
        "flights": new_added_arrivals,
        "settings": settings,
    }
    return render(request, "cheapest_trip/arrivals_loader.html", response)


def departure_cities_loader(request):
    file_path = r"AmaduesAPI\DepartureCities.txt"
    departure_cites = read_cities(file_path)
    # print(departure_cites)
    new_added_departures = []
    for departure_city in departure_cites:
        query = DepartureCity.objects.filter(departure_city=departure_city)
        if len(query) == 0:
            form = DepartureCity()
            form.departure_city = departure_city
            form.save()
            new_added_departures.append(departure_city)
        else:
            print("Departure city already in databse", departure_city)
    settings = Setting.objects.all()[0]
    message = settings.Status
    print("Get", message)

    response = {
        "flights": new_added_departures,
        "settings": settings,
    }

    return render(request, "cheapest_trip/destinations_loader.html", response)
