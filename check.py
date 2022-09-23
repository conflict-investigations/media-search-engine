import argparse
import json
import os
import pickle
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--print',
    action='store_true', dest='print',
    default=False,
    help="Print all known URLs from databases")
parser.add_argument('-j', '--json',
    action='store_true', dest='json',
    default=False,
    help="Print all known URLs as JSON")
parser.add_argument('-d', '--dump',
    action='store_true', dest='dump',
    default=False,
    help="Dump pre-processed URLs as database file")
parser.add_argument('-l', '--load',
    action='store_true', dest='load',
    default=False,
    help="Load database from pre-processed dump file")
parser.add_argument('query', nargs='?', default=None,
    type=str, help='URL query')
args = parser.parse_args()

DATA_FILES = dict(
  CEN4INFORES='cen4infores.json',
  # DefMon3 dataset is 17Mb+, leave it for now to keep repo small
  # DEFMON='defmon-gsua.json',
  BELLINGCAT='ukr-civharm-2022-09-21.json',
)
FOLDER = os.path.join(os.getcwd(), 'data')
DUMP_FILE = 'dump.pickle'

link_extract_regex = r"(https?://.+?)[ ,\n]"
entry_extract_regex = r"ENTRY: (\w+)[\n]?"

def get_file(sourcename):
    return os.path.join(FOLDER, DATA_FILES[sourcename])

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

def load_and_generate_mapping():
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


processed = {}

if args.load:
    with open(DUMP_FILE, 'rb') as f:
        processed = pickle.load(f)
else:
    processed = load_and_generate_mapping()
if args.dump:
    with open(DUMP_FILE, 'wb') as f:
        pickle.dump(processed, f)
    sys.exit(0)

if args.print:
    for key in processed.keys():
        for item in processed[key]:
            print(f"Url: {key}\nId: {item['id']}\nDescription:\n{item['desc']}\n")
    sys.exit(0)
elif args.json:
    print(json.dumps(processed))
    sys.exit(0)
else:
    if not args.query:
        print("No URL supplied")
        sys.exit(1)
    if args.query in processed:
        results = processed[args.query]
        for res in results:
            print(f"Found URL {args.query} in '{res['source']}' dataset")
            print(f"Id: {res['id']}\nDescription:\n\n{res['desc']}")
        sys.exit(0)
    else:
        print("URL not found in database")
        sys.exit(1)
