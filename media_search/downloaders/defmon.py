from datetime import datetime
import json
from urllib import request

DEFMON_ENDPOINT = 'https://widgets.scribblemaps.com/api/maps/nBT8ffpeGH/smjsonLocal'  # noqa
DEFMON_JSON = 'defmon.json'
DEFMON_SHELLINGS_GEOJSON = 'defmon-shellings.geojson'
# "name": "War in Ukraine",
# "id": "f4a2b60dad",
WAR_IN_UKRAINE_ID = 'f4a2b60dad'

class DefmonDownloader():

    @staticmethod
    def download():
        print('Downloading...')
        resp = request.urlopen(DEFMON_ENDPOINT)
        data = resp.read().decode('utf-8')
        return data

    @staticmethod
    def load_data():
        with open(DEFMON_JSON, 'r') as f:
            data = f.read()
        print('Loaded data')
        return data

    @staticmethod
    def save_data(data):
        with open(DEFMON_JSON, 'w') as f:
            f.write(data)

    @classmethod
    def get_data(cls):
        try:
            print('Trying to load data')
            data = cls.load_data()
        except FileNotFoundError:
            print(f"{DEFMON_JSON} not found, downloading")
            data = cls.download()
            cls.save_data(data)
        return data

class DefmonSource():
    @staticmethod
    def extract_events(data, eventname):
        raw = json.loads(data)
        overlays = raw.get('overlays')

        filtered = list(filter(
            lambda x: x.get('id') == WAR_IN_UKRAINE_ID,
            overlays
        ))[0]

        def is_relevant_event(overlay, eventname):
            # Use 'x in y' to match partial strings
            return eventname in (overlay.get('name') or '')

        days = filtered.get('overlays')
        events = []

        def format_event(date, event):
            DATE_INPUT_FORMAT = '%Y%m%d'
            DATE_OUTPUT_FORMAT = '%Y-%m-%d'
            date_formatted = datetime.strptime(
                date, DATE_INPUT_FORMAT
            ).strftime(DATE_OUTPUT_FORMAT)
            coordinates = event.get('points')[0]
            return dict(
                id=event.get('id'),
                latitude=float(coordinates[0]),
                longitude=float(coordinates[1]),
                title=event.get('title'),
                date=date_formatted,
                description='<no description>',
            )

        for day in days:
            for o in day.get('overlays'):
                if is_relevant_event(o, eventname):
                    for s in o.get('overlays'):
                        events.append(format_event(day.get('name'), s))

        return events

    @staticmethod
    def parse_data(date_str):
        pass

    @staticmethod
    def get_data():
        pass

    @staticmethod
    def format_as_geojson(data):
        def format_feature(f):
            return dict(
                type='Feature',
                id=f['id'],
                geometry=dict(
                    type='Point',
                    # GeoJSON swaps lat/lng
                    coordinates=[f['longitude'], f['latitude']],
                ),
                properties=dict(
                    title=f['title'],
                    date=f['date'],
                    description=f['description'],
                ),
            )
        return dict(
            type='FeatureCollection',
            features=list(map(format_feature, data)),
        )

    @staticmethod
    def save_data(data):
        with open(DEFMON_SHELLINGS_GEOJSON, 'w') as f:
            json.dump(data, f, indent=None)

    @staticmethod
    def load_data():
        with open(DEFMON_SHELLINGS_GEOJSON, 'r') as f:
            return json.load(f)


downloader = DefmonDownloader()
raw_data = downloader.get_data()

source = DefmonSource()
shellings_data = source.extract_events(raw_data, 'Shellings')
# for s in source.extract_shellings(raw_data):
#     print(s)

shellings_geojson = source.format_as_geojson(shellings_data)

source.save_data(shellings_geojson)
