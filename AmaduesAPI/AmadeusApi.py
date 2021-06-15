from amadeus import Client, ResponseError

import json
import pandas as pd
from flatten_json import flatten

import datetime
from time import sleep


#############################
# Disbling Warning          #
def warn(*args, **kwargs):  #
    pass                    #
import warnings             #
warnings.warn = warn        #
#############################

from cheapest_trip.models import FlightsData, DepartureCity, ArrivalCity

var = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# results_file_name = 'API_Calling_scrapped_results.csv'


amadeus = Client(
    client_id = '5f8r5UOWHjxmWMQzS0MAEgfbnr4w0r7n',
    client_secret = 'kLIN7jIQDVRCnKVN'
)

def duration_parser(duration):
    if "PT" in duration:
        duration = duration.replace("PT","")

    if "H" in duration:
        duration = duration.replace("H",":")

    if "M" in duration:
        duration = duration.replace("M",":00")
    else:
        duration += "00:00"

    # print(duration)

    duration = duration.split(":")

    new_duration =""
    for i in range(len(duration)):
        if len(duration[i]) == 1:
            old_val = duration[i]
            new_val = "0"+str(old_val)
            new_duration += str(new_val)
        else:
            new_duration+=str(duration[i])
        
        if not i == len(duration)-1:
            new_duration+=":"
    return new_duration

def verify_dataexistence_in_db(departure_loc,arrival_loc,departure_date):
    get_query = FlightsData.objects.filter(
        departure_city  = departure_loc ,
        arrival_city    = arrival_loc ,
        departure_date  = departure_date ,
    )
    if len(get_query)>0:
        return True
    else:
        return False

def process_json(response):
    try:

        print("1st")
        dic_flattened = (flatten(d) for d in response)
        df_ret = pd.DataFrame(dic_flattened)
        # df_ret.to_csv("Good_Name_CSV.csv")
        # print(df_ret.head())

        df_ret = df_ret.loc[:, ~df_ret.columns.duplicated()]
        
        print("2nd")
        # duration = df_ret["itineraries_0_duration"][0]
        # print("3rd")
        # duration = duration_parser(duration)
        # print(duration)

        print("4th")

        departure_city = df_ret["itineraries_0_segments_0_departure_iataCode"][0]
        departure_time = df_ret["itineraries_0_segments_0_departure_at"][0].replace("T","_")
        
        currency = df_ret["price_currency"][0]
        price = int(float(df_ret["price_total"][0]))

        
    except:
        print("[ERROR] while fetching")
        print(response)
        return

        
    # print("Duration:",duration)
    print("Departure City:",departure_city)
    print("Departure Time:",departure_time)
    print("Currency:",currency)
    print("Price:",price)
    
    arrival_city = ""
    arrival_time = ""
    i = 10
    while i>=0:
        # print("Value of i = ",i)
        arrival_code_col = "itineraries_0_segments_{}_arrival_iataCode".format(i)
        arrival_time_col = "itineraries_0_segments_{}_arrival_at".format(i)
        # print("asdas", df_ret, arrival_time_col)
        try:
            # print("In try comment", df_ret[arrival_code_col][0])
            if len(df_ret[arrival_code_col][0])>0:
                arrival_city = df_ret[arrival_code_col][0]
                arrival_time = df_ret[arrival_time_col][0].replace("T","_")

                print("Arrival City:",arrival_city)
                print("Arrival Time:",arrival_time)
                break
        except:
            i-=1
            # print("[ERROR] value not found for ",i)
            # pass
    print("[INFO] Adding Results to CSV -> API_Calling_scrapped_results.csv")

    # fields=[departure_city, departure_time, arrival_city, arrival_time, duration, currency, price ]
    
    departure_date = departure_time.split("_")[0]
    print("Depature Date", departure_date)

    arrival_date = arrival_time.split("_")[0]
    print("Arrival Date", arrival_date)

    # print("Depature Time")
    departure_time = departure_time.split("_")[1]

    print("Arrival Time",arrival_time)
    arrival_time = arrival_time.split("_")[1]

    
    try:
        if verify_dataexistence_in_db(departure_city,arrival_city,departure_date):
            print("Skipping Data Already Exists - Cross Checked")
            return False
            
        form = FlightsData()
        
        form.departure_city     = departure_city
        form.arrival_city       = arrival_city

        form.departure_date     = departure_date
        form.arrival_date       = arrival_date

        form.departure_time     = departure_time
        form.arrival_time       = arrival_time

        # form.duration           = duration
        form.currency           = currency
        form.price              = price

        form.save()
    except:
        print("Form Didn't saved")
            

def get_cheapest_flight(
                        departure_loc, 
                        arrival_loc, 
                        departure_date
                        ):

    retry = 1
    while retry>0:
        try:
            print("[INFO] Getting Response",departure_loc,arrival_loc,departure_date)
            # print("[INFO] Getting Response")
            # print(departure_loc, arrival_loc, departure_date)
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode = departure_loc,
                destinationLocationCode = arrival_loc,
                departureDate = departure_date,
                adults=1,
                currencyCode='USD',
                max = 1
            )
            
            # print(response.data[0])

            jdata = json.dumps(response.data[:3])
            SYM = jdata[:1]
            if SYM != '[':
                rdata = '[' + jdata + ']'
            else:
                rdata = jdata

            ResJson = json.loads(rdata)

            # print(ResJson)
            print("[INFO] Response Getting Done")
            print("[INFO] Cleaning the Response")
            
            process_json(ResJson)
            retry=0
            return
        except ResponseError as error:
            if str(error) == "[---]":
                print("[ERROR] Please Check for connection")
                retry -= 1
                if retry==0:
                    time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    print("[ERROR] Due to Connection Error Response not got, Saving Logs to -> API_Calling_logs.csv\n\n")
                    # fields=["Error", "Internet Connection Error", departure_loc, arrival_loc, departure_date, time_now]
                sleep(3)
            else:
                retry = 0
                print("[ERROR] ",error)

def update_flights():
    
    dt = datetime.datetime.today()

    departures = DepartureCity.objects.all()
    arrivals = ArrivalCity.objects.all()

    dept_year = dt.year
    dept_month = dt.month
    dept_days = [10]

    if int(dept_month)<10:
        dept_month_str = '0'+str(dept_month)
    if int(dept_days[0])<10:
        dept_day_str = '0'+str(dept_days[0])
    else:
        dept_day_str = str(dept_days[0])

    departure_date = f'{dept_year}-{dept_month_str}-{dept_day_str}'
    print(departure_date)
    

    counter = 0
    for departure_loc in departures:
        for arrival_loc in arrivals:

            if departure_loc==arrival_loc:
                print("[ERROR] Arrival City cannot be same as Departure City ")
                continue
                
            

            # print(get_query)
            if verify_dataexistence_in_db(departure_loc,arrival_loc,departure_date):
                print("Skipping - Data already Exists")
                # continue
            else:

                get_cheapest_flight(departure_loc, arrival_loc, departure_date)

                counter+=1
        sleep(0.5)