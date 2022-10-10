import json
import os
import re

from .defaults import CONFIG
from .accessors import BellingcatSource, CenInfoResSource, GeoconfirmedSource
from .utils import normalize_and_sanitize

DATA_FILES = dict(
  BELLINGCAT='bellingcat.json',
  CEN4INFORES='cen4infores.json',
  # DefMon3 dataset is 17Mb+, leave it for now to keep repo small
  # DEFMON='defmon-gsua.json',
  GEOCONFIRMED='geoconfirmed.json',
)

link_extract_regex = r"(https?://.+?)([ ,\n\\<>]|$)"
entry_extract_regex = r"ENTRY: (\w+)[\n]?"
geoconfirmed_regex = r"https://twitter\.com/GeoConfirmed/status/(\d+)([ ,\n]|$)"  # noqa

def get_file(sourcename):
    return os.path.join(CONFIG.DATA_FOLDER, DATA_FILES[sourcename])

def load_files():
    data = {}
    for key in DATA_FILES.keys():
        with open(get_file(key), 'r') as f:
            data[key] = json.loads(f.read())
    return data

def process_bellingcat(data):
    processed = {}
    for item in data['BELLINGCAT']:
        for source in item.get('sources'):
            if not source.get('path'):
                continue  # Skip items without links
            url = source['path']
            loc = dict(
                latitude=item.get('latitude'),
                longitude=item.get('longitude'),
                place_desc=item.get('location')
            )
            date = ''
            if (d := item.get('date')):
                date = f'Date: {d}\n'
            processed[normalize_and_sanitize(url)] = dict(
                unsanitized_url=url,
                source='BELLINGCAT',
                id=item.get('id'),
                desc=date + item.get('description'),
                location=loc,
            )
    return processed

def process_ceninfores(data):
    processed = {}
    for item in data['CEN4INFORES']['geojson']['features']:
        props = item.get('properties')
        if not props:
            continue
        found = []
        # Not every 'type: Feature' has a 'media_url' property
        if (url := props.get('media_url')):
            found.append((url, normalize_and_sanitize(url)))

        # We may get the same URL multiple times for a single item (e.g. once
        # as `GEOLOCATION` and once as `LINK`). But that's not too worrisome
        # since we link the whole item anyway
        if not props.get('description'):
            props['description'] = ''
        if props.get('title'):
            props['description'] = props['title'] + '\n' + props['description']
        matches = re.findall(link_extract_regex,
                             props['description'])
        if matches:
            pairs = ((u, normalize_and_sanitize(u)) for u, _unused in matches)
            found.extend(pairs)
        entryid = None
        if (candidate := re.findall(entry_extract_regex,
                                    props['description'])):
            entryid = candidate[0]
        geometry = item.get('geometry')
        coordinates = [None, None]
        if geometry['type'] == 'Point':
            coordinates = geometry.get('coordinates')
        elif geometry['type'] == 'LineString':
            # Be lazy and use first vector of LineString
            coordinates = geometry.get('coordinates')[0]
        # Swap lat/lng since we're parsing GeoJSOn
        loc = dict(latitude=coordinates[1], longitude=coordinates[0])
        for url, sanitized in found:
            processed[sanitized] = dict(
                unsanitized_url=url,
                source='CEN4INFORES',
                id=entryid,
                desc=props.get('description'),
                location=loc,
            )
    return processed

def process_geoconfirmed(data):
    def is_relevant(folder):
        # Filter out metadata folders
        _name = folder.get('name')
        if _name.startswith('A.') or _name.startswith('B.'):
            return False
        return True

    processed = {}
    folders = filter(is_relevant, data['GEOCONFIRMED'].get('mapDataFolders'))
    for folder in folders:
        placemarks = folder.get('mapDataPlacemarks')
        if not placemarks:
            continue
        for item in placemarks:
            matches = re.findall(link_extract_regex,
                                 item.get('description'))
            if not matches:
                continue
            found = []
            if matches:
                pairs = ((u, normalize_and_sanitize(u))
                    for u, _unused in matches)
                found.extend(pairs)

            def get_id(desc):
                status = re.findall(geoconfirmed_regex, desc)
                if status:
                    return status[0][0]
                return '(no id)'
            loc = dict(
                # Coordinates swapped?
                latitude=item.get('coordinates')[1],
                longitude=item.get('coordinates')[0],
            )
            for url, sanitized in found:
                processed[sanitized] = dict(
                    unsanitized_url=url,
                    source='GEOCONFIRMED',
                    id=get_id(item.get('description')),
                    desc=item.get('description'),
                    location=loc,
                )
    return processed

def ensure_data_dir():
    if not os.path.isdir(CONFIG.DATA_FOLDER):
        os.mkdir(CONFIG.DATA_FOLDER)

def download_data():
    ensure_data_dir()
    print('  Downloading Bellingcat...')
    BellingcatSource(datapath=CONFIG.DATA_FOLDER).get_data(download=True)
    print('  Downloading Cen4infoRes...')
    CenInfoResSource(datapath=CONFIG.DATA_FOLDER).get_data(download=True)
    print('  Downloading GeoConfirmed...')
    GeoconfirmedSource(datapath=CONFIG.DATA_FOLDER).get_data(download=True)
    print('  Download finished')

def load_and_generate_mapping():
    try:
        data = load_files()
    except FileNotFoundError:
        print('Files not yet downloaded, downloading')
        download_data()
        data = load_files()
    processed = {}
    bellingcat = process_bellingcat(data)
    ceninfores = process_ceninfores(data)
    geoconfirmed = process_geoconfirmed(data)

    def add_src(src):
        for key in src.keys():
            if not processed.get(key):
                processed[key] = []
            processed[key].append(src[key])
    add_src(bellingcat)
    add_src(ceninfores)
    add_src(geoconfirmed)

    return processed
