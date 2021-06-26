import datetime
from datetime import timedelta

def add_months(sourcedate, months):
    import calendar
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

today_dt = datetime.datetime.today()

dept_day = 10
return_day = 20
departure_dates = []

for x in range(1,10):
    last_month_to_fetch = add_months(today_dt,x)
    departure_dates.append(last_month_to_fetch)
    # print(last_month_to_fetch)

# print(departure_dates)


for date in departure_dates:
    if int(date.month)<10:
        dept_month_str = '0'+str(date.month)

    departure_date = f'{date.year}-{dept_month_str}-{dept_day}'
    return_date = f'{date.year}-{dept_month_str}-{return_day}'
    print(departure_date,return_date)