import csv


AIRPORTS = {}


# this will use all your memory and take forever with larger files
def load_csv(filepath):
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        return [{k: v for k, v in row.items()} for row in csv_file]  # NOQA


def load_big_csv_file(filepath, *fields, limit=-1):
    data = []
    with open(filepath, 'r') as file:
        csv_file = csv.DictReader(file)
        for i, line in enumerate(csv_file):
            if limit != -1 and i >= limit:
                break
            if limit == -1 and i % 100000 == 0:
                print(f'Loading csv file... ({i:>7} / {5819079:>7})')

            data.append({k: line[k] for k in fields})
    return data


def main() -> None:
    airports = load_csv('data/flights/airports.csv')
    for airport in airports:
        AIRPORTS[airport['IATA_CODE']] = airport

    #for k, v in AIRPORTS.items():
    #    print(f'{k}: {v}')

    flights = load_big_csv_file('data/flights/flights.csv', 'ORIGIN_AIRPORT', 'DEPARTURE_DELAY', limit=1)

    for i, flight in enumerate(flights):
        print(flight)
        origin = AIRPORTS[flight['ORIGIN_AIRPORT']]
        print(origin['LONGITUDE'], origin['LATITUDE'])


if __name__ == '__main__':
    main()
