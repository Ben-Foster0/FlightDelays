import csv
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import time
import pickle

AIRPORTS = {}
MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

conn = sqlite3.connect('data/weather/historical_weather.sqlite')
conn.row_factory = sqlite3.Row
cur = conn.cursor()


def get_weather_data(iata, year, month, day, hour):
    cur.execute('''
        SELECT * FROM weather
        WHERE iata = :iata AND year = :year AND month = :month AND day = :day AND hour = :hour
    ''', {'iata': iata, 'year': year, 'month': month, 'day': day, 'hour': hour})

    result = cur.fetchone()
    if result:
        return dict(result)


# loading an entire csv file as a list of dicts
# this will take ages with larger files and likely use all your memory
def load_csv(filepath):
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        return [{k: v for k, v in row.items()} for row in csv_file]  # NOQA


def random_flights(count):
    cur.execute('''
        SELECT * FROM flights ORDER BY RANDOM() LIMIT ?;
    ''', (2*count,))
    flights = []
    for _ in range(count):
        flight = dict(cur.fetchone())
        while flight['origin_airport'] not in AIRPORTS or not flight['departure_delay']:
            flight = dict(cur.fetchone())
        flights.append(flight)
    return flights


def append_weather_data(flight):
    print(f'Getting weather data for flight {flight}')
    extra = {'iata': flight['origin_airport'], 'hour': flight['scheduled_departure']//100}
    cur.execute('''
        SELECT * FROM weather
        WHERE iata = :iata AND year = :year AND month = :month AND day = :day AND hour = :hour
    ''', flight | extra)
    result = cur.fetchone()
    return dict(result) | flight


def sample_flights(count):
    t0 = time.time()
    flights = []
    for i, flight in enumerate(random_flights(count), 1):
        print(f'({(time.time()-t0)/i * (count-i)}) {i:>4} / {count:>4}: ', end='')
        flights.append(append_weather_data(flight))
    return flights


def full_sample(count):
    cur.execute('''
            SELECT * FROM flights
            JOIN weather
                ON flights.year == weather.year
               AND flights.month == weather.month
               AND flights.day == weather.day
               AND floor(flights.scheduled_departure/100) == weather.hour
               AND flights.origin_airport == weather.iata
            ORDER BY RANDOM()
            LIMIT ?;
        ''', (2 * count,))
    flights = []
    for _ in range(count):
        flight = dict(cur.fetchone())
        while flight['origin_airport'] not in AIRPORTS or not flight['departure_delay']:
            flight = dict(cur.fetchone())
        flights.append(flight)
    return flights


def to_dataframe(flights):
    fields = ['temperature_2m', 'rain', 'snowfall', 'cloud_cover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 'wind_speed_10m', 'wind_speed_100m', 'departure_delay']
    filtered_flights = [{key: d[key] for key in fields} for d in flights]

    df = pd.DataFrame(filtered_flights)
    return df


def get_model(df: pd.DataFrame, model_path):
    df_m = df.dropna()

    # X = df_m.loc[:, df_m.columns != 'departure_delay']
    # y = df_m['departure_delay']
    # X = df[['temperature_2m', 'rain', 'snowfall', 'cloud_cover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 'wind_speed_10m', 'wind_speed_100m']]
    # y = df['departure_delay']
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.5)

    # lr = LinearRegression()
    lr = GradientBoostingRegressor()
    lr.fit(x_train, y_train)

    y_pred = lr.predict(x_test)

    print(r2_score(y_test, y_pred))
    print(r2_score(y_train, y_pred))

    with open(model_path, 'wb') as f:
        pickle.dump(lr, f)


def main():
    airports = load_csv('data/flights/airports.csv')
    for airport in airports:
        AIRPORTS[airport['IATA_CODE']] = airport

    flights = sample_flights(1024)
    # flights = full_sample(64)
    df = to_dataframe(flights)
    # print(df.to_string())

    get_model(df, 'models/model1.pkl')


if __name__ == '__main__':
    main()
