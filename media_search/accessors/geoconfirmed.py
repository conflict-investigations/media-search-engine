# https://www.google.com/maps/d/kml?mid=10YK14-QB25penu8jeS4hBVarzGKZsVgj&nl=1&forcekml=1
# From kml/kmz:
# https://www.google.com/maps/d/kml?forcekml=1&mid=10YK14-QB25penu8jeS4hBVarzGKZsVgj

# From custom map project (with author's blessing)
# JSON:
# https://geoconfirmed.azurewebsites.net/api/map/GetMap/Ukraine

import json

from .base import DataSource
from ..downloaders import GeoconfirmedDownloader

GEOCONFIRMED_FILENAME = 'geoconfirmed.json'

class GeoconfirmedSource(DataSource):
    """
    @GeoConfirmed
    Data from https://geoconfirmed.azurewebsites.net/api/map/GetMap/Ukraine
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = GEOCONFIRMED_FILENAME

    @staticmethod
    def _download_data():
        data = GeoconfirmedDownloader.download()
        return data

    def get_data(self, download=True):
        if not download:
            features = self.load_data()
            return features
        features = json.loads(self._download_data())
        self.dump_data(features)
        return features

    def print_data(self, download=True):
        features = self.get_data(self, download)
        print(json.dumps(features, indent=None))
