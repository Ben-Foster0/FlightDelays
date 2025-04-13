import csv
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import time
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

AIRPORTS = {}

conn = sqlite3.connect('data/weather/historical_weather.sqlite')
conn.row_factory = sqlite3.Row
cur = conn.cursor()


# loading an entire csv file as a list of dicts
# this will take ages with larger files and likely use all your memory
def load_csv(filepath):
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        return [{k: v for k, v in row.items()} for row in csv_file]  # NOQA


def combine_data(count):
    query = '''
        INSERT INTO combined (iata, year, month, day, hour, temperature_2m, rain, snowfall, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, wind_speed_10m, wind_speed_100m, departure_delay)
        SELECT flights.origin_airport, flights.year, flights.month, flights.day, weather.hour, weather.temperature_2m, weather.rain, weather.snowfall, weather.cloud_cover, weather.cloud_cover_low, weather.cloud_cover_mid, weather.cloud_cover_high, weather.wind_speed_10m, weather.wind_speed_100m, flights.weather_delay
        FROM flights
        JOIN weather
            ON flights.year == weather.year
           AND flights.month == weather.month
           AND flights.day == weather.day
           AND floor(flights.scheduled_departure/100) == weather.hour
           AND flights.origin_airport == weather.iata
        WHERE flights.weather_delay != '' AND flights.weather_delay > 0
        ORDER BY RANDOM()
        LIMIT ?;
    '''
    cur.execute(query, (count,))
    conn.commit()


def full_sample(count):
    cur.execute('''
            SELECT temperature_2m, rain, snowfall, cloud_cover, cloud_cover_low, cloud_cover_mid, cloud_cover_high, wind_speed_10m, wind_speed_100m, departure_delay
            FROM combined
            ORDER BY random()
            LIMIT ?;
        ''', (2 * count,))
    return [dict(r) for r in cur.fetchall()]


def to_dataframe(flights):
    fields = ['temperature_2m', 'rain', 'snowfall', 'cloud_cover', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 'wind_speed_10m', 'wind_speed_100m', 'departure_delay']
    # fields = ['rain', 'cloud_cover', 'wind_speed_10m', 'wind_speed_100m', 'departure_delay']
    filtered_flights = [{key: d[key] for key in fields} for d in flights]

    df = pd.DataFrame(filtered_flights)
    return df


def get_model(df: pd.DataFrame, model_path):
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    x_train, x_test, y_train, y_test = train_test_split(X, y)

    # lr = LinearRegression()
    # lr = GradientBoostingRegressor()
    # lr = HistGradientBoostingRegressor()
    lr = RandomForestRegressor()
    lr.fit(x_train, y_train)

    y_pred = lr.predict(x_test)

    print(f'r2_score: {r2_score(y_test, y_pred)}')
    print(f'mean_squared_error: {mean_squared_error(y_test, y_pred)}')

    with open(model_path, 'wb') as f:
        pickle.dump(lr, f)


def test_single_data(model_path, data):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        prediction = model.predict(data)
        print(f'Predicted: {prediction[0]}')


def main():
    airports = load_csv('data/flights/airports.csv')
    for airport in airports:
        AIRPORTS[airport['IATA_CODE']] = airport

    flights = full_sample(65536)
    df = to_dataframe(flights)

    corr_matrix = df.corr()
    plt.figure(figsize=(10, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Correlations')
    plt.savefig('heatmap.svg', format='svg', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    main()
