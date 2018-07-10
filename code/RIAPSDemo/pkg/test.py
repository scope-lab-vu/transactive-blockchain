from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from libs.Grafana.config import Config
from libs.Grafana.dbase import Database

from time import time, sleep
import datetime

print(time())

dbase = Database()

tag_dict={ "name" : "test" }
now = int(time())
print(now)

dbase.post(now=now, tag_dict=tag_dict, seriesName='testSeries', value=25)

now = datetime.datetime.now()
print(now)

dbase.post(now=now, tag_dict=tag_dict, seriesName='testSeries', value=30)