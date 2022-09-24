import json
import os
import re

from .defaults import CONFIG
from .accessors import BellingcatSource, CenInfoResSource

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
            processed[source.get('path')] = dict(
                source='BELLINGCAT',
                id=item.get('id'),
                desc=item.get('description'),
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
            found.append(url)

        # We may get the same URL multiple times for a single item (e.g. once
        # as `GEOLOCATION` and once as `LINK`). But that's not too worrisome
        # since we link the whole item anyway
        if not props.get('description'):
            props['description'] = ''
        matches = re.findall(link_extract_regex,
                             props['description'])
        if matches:
            found.extend(matches)
        entryid = None
        if (candidate := re.findall(entry_extract_regex,
                                    props['description'])):
            entryid = candidate[0]
        for url in found:
            processed[url] = dict(
                source='CEN4INFORES',
                id=entryid,
                desc=props.get('description'),
            )
    return processed

def download_data():
    ensure_data_dir()
    print('  downloading Bellingcat...')
    BellingcatSource(datapath=CONFIG.DATA_FOLDER).get_data()
    print('  downloading Cen4infoRes...')
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
    for key in bellingcat.keys():
        processed[key] = [bellingcat[key], ]
    for key in ceninfores.keys():
        if not processed.get(key):
            processed[key] = []
        processed[key].append(ceninfores[key])
    return processed
