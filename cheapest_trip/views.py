from django.contrib import messages 
from django.shortcuts import redirect, render

from .models import FlightsData, DepartureCity, ArrivalCity
from datetime import datetime, timedelta
from AmaduesAPI.ArrivalCitiesLoader import read_cities
from AmaduesAPI.AmadeusApi import update_flights


def home(request):

    # startdate = date.today()
    # enddate = startdate + timedelta(days=6)
    # Sample.FlightsData.filter(departure_time__range=[startdate, enddate])


    today = datetime.today()
    future_dates = today + timedelta(days=0)

    query = FlightsData.objects.filter(
        departure_date__gte=future_dates,
        )
    # query = FlightsData.objects.all()
    # print(len(query))

    response = {
        "flights":query,
    }
    
    return render(request, 'cheapest_trip/home.html',response) 


def search(request):

    # startdate = date.today()
    # enddate = startdate + timedelta(days=6)
    # Sample.FlightsData.filter(departure_time__range=[startdate, enddate])
    if request.method == "POST":

        try:
            Departure = request.POST.get('Departure')
            Arrival = request.POST.get('Arrival')

            today = datetime.today()
            future_dates = today + timedelta(days=0)

            query = FlightsData.objects.filter(
                departure_date__gte=future_dates,
                departure_city=Departure,
                arrival_city=Arrival,

            )

        except:
            print("Error")
            return redirect("search")
        # query = FlightsData.objects.all()
        # print(len(query))

        response = {
            "flights":query,
        }

        return render(request, 'cheapest_trip/home.html',response) 
    
    else:
        response = {
            "home":"active",
        }
    
        return render(request, 'cheapest_trip/search.html',response) 


def update_flights_record(request):

    update_flights()
    
    flights = ""

    response = {
        "flights":flights,
    }
    return render(request, 'cheapest_trip/temp_file.html',response)

def arrival_cities_loader(request):

    file_path = r"E:\AA - Working Projects\a New\project - flight prices\web\Flights\AmaduesAPI\ArrivalCities.txt"
    arrival_cites = read_cities(file_path)
    print(arrival_cites)
    for arrival_city in arrival_cites:
        query = ArrivalCity.objects.filter(arrival_city=arrival_city)
        if len(query)==0:
            form = ArrivalCity()
            form.arrival_city = arrival_city
            form.save()
        else:
            print("arrival city already in databse",arrival_city)



    response = {
        "flights":arrival_cites,
    }
    return render(request, 'cheapest_trip/temp_file.html',response)


def departure_cities_loader(request):
    file_path = r"E:\AA - Working Projects\a New\project - flight prices\web\Flights\AmaduesAPI\DepartureCities.txt"
    departure_cites = read_cities(file_path)
    print(departure_cites)
    for departure_city in departure_cites:
        query = DepartureCity.objects.filter(departure_city=departure_city)
        if len(query)==0:
            form = DepartureCity()
            form.departure_city = departure_city
            # form.save()
        else:
            print("Departure city already in databse",departure_city)

    response = {
        "flights":departure_cites,
    }
    return render(request, 'cheapest_trip/temp_file.html',response)