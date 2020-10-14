import requests
from sqlalchemy import create_engine, Table, Column, String, Float, MetaData
from sqlalchemy.sql import select
from datetime import datetime
import matplotlib.pyplot as plt


class WeatherProvider:
    def __init__(self, key):
        self.key = key

    def get_data(self, location, start_date, end_date):
        url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history'
        params = {
            'aggregateHours': 24,
            'startDateTime': f'{start_date}T00:0:00',
            'endDateTime': f'{end_date}T23:59:59',
            'unitGroup': 'metric',
            'location': location,
            'key': self.key,
            'contentType': 'json',
        }
        data = requests.get(url, params).json()
        return [
            {
                'date': row['datetimeStr'][:10],
                'mint': row['mint'],
                'maxt': row['maxt'],
                'location': 'Volgograd,Russia',
                'humidity': row['humidity'],
            }
            for row in data['locations'][location]['values']
        ]


engine = create_engine('sqlite:///weather.sqlite3')
metadata = MetaData()
weather = Table(
    'weather',
    metadata,
    Column('date', String),
    Column('mint', Float),
    Column('maxt', Float),
    Column('location', String),
    Column('humidity', Float),
)
metadata.create_all(engine)

c = engine.connect()

provider = WeatherProvider('I3D60I88UB6KPSDAVGK38HNP5')
c.execute(weather.insert(), provider.get_data('Volgograd,Russia', '2020-09-20', '2020-09-29'))

entries = list(c.execute(select([weather])))

for entry in entries:
    print(entry)

dates = [datetime.strptime(entry[0], '%Y-%m-%d') for entry in entries]

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

ax1.set_ylabel('Temperature')
min_temperatures = [entry[1] for entry in entries]
max_temperatures = [entry[2] for entry in entries]
average_temperatures = [(v_min + v_max) / 2 for v_min, v_max in zip(min_temperatures, max_temperatures)]
ax1.plot(dates, min_temperatures, color='c')
ax1.plot(dates, average_temperatures, color='gray', linestyle='--')
ax1.plot(dates, max_temperatures, color='r')

ax2.set_ylabel('Humidity')
humidities = [entry[4] for entry in entries]
ax2.plot(dates, humidities, color='b')

ax2.set_xlabel('Date')
plt.xticks(rotation=90)
plt.show()
