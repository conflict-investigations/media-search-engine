from urllib import request

GEOCONFIRMED_ENDPOINT = 'https://geoconfirmed.azurewebsites.net/api/map/GetMap/Ukraine'  # noqa
GEOCONFIRMED_JSON = 'geoconfirmed.json'

# TODO: Refactor this, save to CONFIG.DATA_FOLDER

class GeoconfirmedDownloader():

    @staticmethod
    def download():
        resp = request.urlopen(GEOCONFIRMED_ENDPOINT)
        data = resp.read().decode('utf-8')
        return data

    @staticmethod
    def load_data():
        with open(GEOCONFIRMED_JSON, 'r') as f:
            data = f.read()
        return data

    @staticmethod
    def save_data(data):
        with open(GEOCONFIRMED_JSON, 'w') as f:
            f.write(data)

    @classmethod
    def get_data(cls):
        try:
            print('Trying to load data')
            data = cls.load_data()
        except FileNotFoundError:
            print(f"{GEOCONFIRMED_JSON} not found, downloading")
            data = cls.download()
            cls.save_data(data)
        return data
