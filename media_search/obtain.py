import json
import os
import re

from .defaults import CONFIG
from .accessors import BellingcatSource, CenInfoResSource
from .utils import normalize_and_sanitize

DATA_FILES = dict(
  BELLINGCAT='bellingcat.json',
  CEN4INFORES='cen4infores.json',
  # DefMon3 dataset is 17Mb+, leave it for now to keep repo small
  # DEFMON='defmon-gsua.json',
)

link_extract_regex = r"(https?://.+?)[ ,\n]"
entry_extract_regex = r"ENTRY: (\w+)[\n]?"

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
            processed[normalize_and_sanitize(url)] = dict(
                unsanitized_url=url,
                source='BELLINGCAT',
                id=item.get('id'),
                desc=item.get('description'),
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
        matches = re.findall(link_extract_regex,
                             props['description'])
        if matches:
            pairs = ((u, normalize_and_sanitize(u)) for u in matches)
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
        loc = dict(latitude=coordinates[0], longitude=coordinates[1])
        for url, sanitized in found:
            processed[sanitized] = dict(
                unsanitized_url=url,
                source='CEN4INFORES',
                id=entryid,
                desc=props.get('description'),
                location=loc,
            )
    return processed

def download_data():
    ensure_data_dir()
    print('  Downloading Bellingcat...')
    BellingcatSource(datapath=CONFIG.DATA_FOLDER).get_data()
    print('  Downloading Cen4infoRes...')
    CenInfoResSource(datapath=CONFIG.DATA_FOLDER).get_data()
    print('  Download finished')

def ensure_data_dir():
    if not os.path.isdir(CONFIG.DATA_FOLDER):
        os.mkdir(CONFIG.DATA_FOLDER)

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

    def add_src(src):
        for key in src.keys():
            if not processed.get(key):
                processed[key] = []
            processed[key].append(src[key])
    add_src(bellingcat)
    add_src(ceninfores)

    return processed
