import csv
import requests
from flight import Flight

AIRPORTS = {}
MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# requesting hourly weather data for an entire month to avoid spamming api calls
def get_weather_data(lat, lon, month):
    r = requests.get(
        url='https://archive-api.open-meteo.com/v1/archive',
        params={
            'latitude': f'{lat}',
            'longitude': f'{lon}',
            'start_date': f'2015-{month:>02}-01',
            'end_date': f'2015-{month:>02}-{MONTH_LENGTHS[month-1]}',
            'hourly': 'temperature_2m,rain,snowfall,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_speed_100m',
            'timezone': 'auto'
        }
    )
    data = r.json()

    # converting to a more usable format of {'iso8601 time': {data..}, ..}
    timestamped_data = {}
    timestamps = []
    for timestamp in data['hourly']['time']:
        timestamps.append(timestamp)
        timestamped_data[timestamp] = {}

    for name, vals in data['hourly'].items():
        if name == 'time':
            continue
        for time, val in zip(timestamps, vals):
            timestamped_data[time][name] = val

    return timestamped_data


# tries parsing a string as an integer or float, returns the original string if it couldn't be parsed
# i'm assuming predictive models need numbers to work? or at least work better with numbers
def try_str_to_num(s):
    try:
        i = int(s)
        return i
    except ValueError:
        try:
            f = float(s)
            return f
        except ValueError:
            return s


# loading an entire csv file as a list of dicts
# this will take ages with larger files and likely use all your memory
def load_csv(filepath):
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        return [{k: v for k, v in row.items()} for row in csv_file]  # NOQA


# loads only specific columns from a csv file, with a limited number of rows
def load_big_csv_file(filepath, *fields, limit=-1):
    data = []
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        for i, line in enumerate(csv_file):
            if limit != -1 and i >= limit:
                break
            #if limit == -1 and i % 100000 == 0:
            #    print(f'Loading csv file... ({i:>7} / {5819079:>7})')

            data.append({k: try_str_to_num(line[k]) for k in fields})
    return data


def main() -> None:
    airports = load_csv('data/flights/airports.csv')
    for airport in airports:
        AIRPORTS[airport['IATA_CODE']] = airport

    flights = load_big_csv_file('data/flights/flights.csv', 'SCHEDULED_DEPARTURE', 'DEPARTURE_TIME', 'DEPARTURE_DELAY',
                                'YEAR', 'MONTH', 'DAY', 'ORIGIN_AIRPORT', 'DEPARTURE_DELAY', limit=80)

    # PLEASE figure out a way to cache weather data, so you aren't blowing past the api call limit
    cached_weather = {}
    for i, f in enumerate(flights):
        if i < 65:
            continue
        flight = Flight(f, AIRPORTS)
        airport = flight.ORIGIN_AIRPORT
        month = flight.MONTH
        if airport not in cached_weather or month not in cached_weather[airport]:
            weather_data = get_weather_data(flight.latitude, flight.longitude, flight.MONTH)
            if airport not in cached_weather:
                cached_weather[airport] = {}
            cached_weather[airport][month] = weather_data
        else:
            weather_data = cached_weather[airport][month]
        print(f'{i:>2} -> {flight.DEPARTURE_DELAY:>5}: {weather_data[flight.get_time()]}')


if __name__ == '__main__':
    main()
