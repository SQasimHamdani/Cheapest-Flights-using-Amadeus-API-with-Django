from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from AmaduesAPI import AmadeusApi

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(AmadeusApi.update_flights, 'interval', days=10)
    scheduler.start()