import json
from urllib import request

from .base import DataSource

CENINFORES_JSON_URL = 'https://maphub.net/json/map_load/176607'
CENINFORES_FILENAME = 'cen4infores.json'
# It seems maphub blocks 'python-urllib' user agent, so set an innocent one
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'  # noqa

class CenInfoResSource(DataSource):
    """
    Center for Information Resilience
    Data from https://maphub.net/Cen4infoRes/russian-ukraine-monitor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = CENINFORES_FILENAME

    @staticmethod
    def _download_data():
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        }
        req = request.Request(
            url=CENINFORES_JSON_URL,
            headers=headers,
            method='POST',
        )
        data = json.loads(
            request.urlopen(
                req,
                # data=json.dumps({}).encode('utf-8'),
                data=b'{}',
                timeout=10,
            ).read().decode('utf-8')
        )
        return data

    def get_data(self, download=True):
        if not download:
            features = self.load_data()
            return features
        features = self._download_data()
        self.dump_data(features)
        return features

    def print_data(self, download=True):
        features = self.get_data(self, download)
        print(json.dumps(features, indent=None))
