from amadeus import Client, ResponseError

import json
import pandas as pd
from flatten_json import flatten

import datetime
from time import sleep

import csv
from csv import reader

#############################
# Disbling Warning          #
def warn(*args, **kwargs):  #
    pass                    #
import warnings             #
warnings.warn = warn        #
#############################

var = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

results_file_name = 'API_Calling_scrapped_results.csv'

amadeus = Client(
    client_id='5f8r5UOWHjxmWMQzS0MAEgfbnr4w0r7n',
    client_secret='kLIN7jIQDVRCnKVN'
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

def process_json(response):
    
    dic_flattened = (flatten(d) for d in response)
    df_ret = pd.DataFrame(dic_flattened)

    # print(df_ret.head())

    df_ret = df_ret.loc[:, ~df_ret.columns.duplicated()]

    # df_ret.to_csv("API_Calling_sample_extracted.csv")
    
    duration = df_ret["itineraries_0_duration"][0]
    duration = duration_parser(duration)
    print(duration)



    

    departure_city = df_ret["itineraries_0_segments_0_departure_iataCode"][0]
    departure_time = df_ret["itineraries_0_segments_0_departure_at"][0].replace("T","_")
    
    currency = df_ret["price_currency"][0]
    price = int(float(df_ret["price_total"][0]))
    
    print("Duration:",duration)
    print("Departure City:",departure_city)
    print("Departure Time:",departure_time)
    print("Currency:",currency)
    print("Price:",price)
    
    arrival_city = ""
    arrival_time = ""
    i = 10
    while i>0:
        # print("Value of i = ",i)
        arrival_code_col = "itineraries_0_segments_{}_arrival_iataCode".format(i)
        arrival_time_col = "itineraries_0_segments_{}_arrival_at".format(i)
        try:
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
    fields=[departure_city, departure_time, arrival_city, arrival_time, duration, currency, price ]
    
    
    existence_flag=False
    with open(results_file_name, 'r', newline='') as f:
        # print(fields)
        rows = reader(f)
        for row in rows:
            
            # print(fields[4],"==",row[4])
            # if fields[3] == row[3]:
            #     print("Arrival Matched")
            # if fields[4] == row[4]:
            #     print("Date Matched")
            # if fields[6] == row[6]:
            #     print("Price Matched")

            if fields == row:
                print("[WARN] This Data Exists Already")
                existence_flag = True
                break


    if not existence_flag:
        with open(results_file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
    
    print("\n\n")


def get_cheapest_flight(
                        departure_loc, 
                        arrival_loc, 
                        departure_date
                        ):
    if departure_loc==arrival_loc:
        print("[ERROR] Arrival City cannot be same as Departure City ")
        return
    
    retry = 3
    while retry>0:
        try:
            print("[INFO] Getting Response")
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
                    fields=["Error", "Internet Connection Error", departure_loc, arrival_loc, departure_date, time_now]
                    with open('API_Calling_logs.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)
                sleep(3)
            else:
                retry = 0
                print("[ERROR] ",error)

def read_cities(file_path):
    string_input = ""
    f = open(file_path, "r")
    string_input = f.read()

    cites = []
    for line in string_input.split("\n"):
        if len(line)>1 and len(line) <= 3:
            cites.append(line)
    return cites

def check_result_file_template():
    try:
        with open(results_file_name, 'r', newline='') as f:
            pass
    except:
        print("[INFO] Template not found. Creating a New Tempalte")
        with open(results_file_name, 'w', newline='') as f:
            header_names=["departure_city", "departure_time", "arrival_city", "arrival_time", "duration", "currency", "price" ]
            writer = csv.writer(f)
            writer.writerow(header_names)

def check_record_already_fetched(dept,arrival,dept_date):
    dept_existence_flag=False
    arrival_existence_flag=False
    dept_date_existence_flag=False
    with open(results_file_name, 'r', newline='') as f:
        rows = reader(f)
        for row in rows:
            # 2021-06-10_20:20:00
            # print(fields[4],"==",row[4])
            if dept == row[0]:
                dept_existence_flag = True
            if arrival == row[2]:
                arrival_existence_flag = True
            if dept_date == row[1].split("_")[0]:
                dept_date_existence_flag = True
    
    if dept_existence_flag and arrival_existence_flag and dept_date_existence_flag:
        return True
    else:
        return False

file_path = "ArrivalCities.txt"
arrival_cites = read_cities(file_path)

departure_cites = ['CCU']
# arrival_loc = arrival_cites[0]

dept_year = 2021
dept_month = 6
dept_days = [i for i in range(10,21)]

dt = datetime.datetime.today()



check_result_file_template()


# get_cheapest_flight("CCU", "SCL", "2021-06-10")
counter = 0
for departure_loc in departure_cites:
    for arrival_loc in arrival_cites[:]:
        # for day in dept_days:
        #     New_Month = Month
        #     if int(dt.day)>1 and int(day)<15:
        #         # New_Month = str(dt.month+1)
        #         # print("Date Skipped")
        #         continue
        #     # elif int(dt.day)>15
        #     flightAPI.get_response(Country, Currency, Origin, Dest, Year, New_Month, day)
        if int(dept_month)<10:
            dept_month_str = '0'+str(dept_month)
        if int(dept_days[0])<10:
            dept_day_str = '0'+str(dept_days[0])
        else:
            dept_day_str = str(dept_days[0])
        departure_date = f'{dept_year}-{dept_month_str}-{dept_day_str}'

        if check_record_already_fetched(departure_loc, arrival_loc, departure_date ):
            print("[INFO] Record already found") 
            continue

        print(str(counter),"-",departure_loc, arrival_loc, departure_date)
        resp = get_cheapest_flight(departure_loc, arrival_loc, departure_date)
        # if resp:
        counter+=1

    sleep(0.5)

