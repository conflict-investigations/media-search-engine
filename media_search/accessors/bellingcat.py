import json

from dataclasses import asdict, dataclass
from urllib import request
from typing import List

from .base import DataSource

BELLINGCAT_BASE = 'https://ukraine.bellingcat.com/ukraine-server/api/ukraine'
EVENTS_ENDPOINT = BELLINGCAT_BASE + '/export_events/deeprows'
SOURCES_ENDPOINT = BELLINGCAT_BASE + '/export_sources/deepids'
ASSOCIATIONS_ENDPOINT = BELLINGCAT_BASE + '/export_associations/deeprows'

BELLINGCAT_FILENAME = 'bellingcat.json'

@dataclass
class Event():
    id: str
    date: str
    latitude: float
    longitude: float
    location: str
    description: str
    sources: List['Source']
    filters: List['Association']

    # https://www.delftstack.com/howto/python/dataclass-to-json-in-python/
    @property
    def __dict__(self):
        return asdict(self)

@dataclass
class Source():
    id: str
    path: str
    description: str

@dataclass
class Association():
    key: str
    value: str

class BellingcatSource(DataSource):
    """
    Bellingcat
    Data from https://ukraine.bellingcat.com
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = BELLINGCAT_FILENAME

    @staticmethod
    def _download_data():
        data = {}
        data['events'] = json.loads(
            request.urlopen(EVENTS_ENDPOINT).read().decode('utf-8'))
        data['sources'] = json.loads(
            request.urlopen(SOURCES_ENDPOINT).read().decode('utf-8'))
        data['associations'] = json.loads(
            request.urlopen(ASSOCIATIONS_ENDPOINT).read().decode('utf-8'))
        return data

    # This is only for testing
    @staticmethod
    def _load_streams():
        data = {}

        def _load(item):
            with open(f"{item}.json", 'r') as f:
                data[item] = json.load(f)
        _load('events')
        _load('sources')
        _load('associations')
        return data

    def _get_source(self, source_id, event_id):
        src = self.data['sources'].get(source_id)
        return Source(id=event_id, path=src.get('paths')[0],
                    description=src.get('description'))

    def _get_association(self, association):
        assoc = list(filter(None,
            (a for a in self.data['associations']
                if a.get('id') == association)
        ))[0]
        return Association(
            key=assoc['filter_paths'][0],
            value=assoc['filter_paths'][1]
        )

    def _mangle(self, e):
        eventid = e.get('id')
        return Event(
            id=eventid,
            date=e.get('date'),
            latitude=e.get('latitude'),
            longitude=e.get('longitude'),
            location=e.get('location'),
            description=e.get('description'),
            sources=[self._get_source(s, eventid) for s in e.get('sources')],
            filters=[self._get_association(a) for a in e.get('associations')],
        )

    def get_data(self, download=True):
        if not download:
            events = self.load_data()
            return events
        self.data = self._download_data()
        events = [self._mangle(e).__dict__ for e in self.data['events']]
        self.dump_data(events)
        return events

    def print_data(self, download=True):
        events = self.get_data(download)
        print(json.dumps(events, indent=None))


"""
Reference:
https://github.com/bellingcat/ukraine-timemap/blob/590cb66a2b069fc3041662404bb0e34c896501a7/src/components/controls/DownloadButton.js#L37-L63

const exportEvents = events.map((e) => {
  return {
    id: e.civId,
    date: e.date,
    latitude: e.latitude,
    longitude: e.longitude,
    location: e.location,
    description: e.description,
    sources: e.sources.map((id) => {
      const s = sources[id];
      return {
        id,
        path: s.paths[0],
        description: s.description,
      };
    }),
    filters: e.associations.map((a) => {
      return {
        key: a.filter_paths[0],
        value: a.filter_paths[1],
      };
    }),
  };
});
return JSON.stringify(exportEvents);
"""
