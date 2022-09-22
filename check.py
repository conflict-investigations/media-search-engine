import argparse
import json
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--print',
    action='store_true', dest='print',
    default=False,
    help="Print all known URLs from databases")
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

data = {}

def get_file(sourcename):
    return os.path.join(FOLDER, DATA_FILES[sourcename])


for key in DATA_FILES.keys():
    with open(get_file(key), 'r') as f:
        data[key] = json.loads(f.read())

processed = {}

for item in data['BELLINGCAT']:
    for source in item.get('sources'):
        processed[source.get('path')] = dict(
            source='BELLINGCAT',
            id=item.get('id'),
            desc=item.get('description'),
        )

link_extract_regex = r"(https?://.+?)\n"

for item in data['CEN4INFORES']['geojson']['features']:
    props = item.get('properties')
    if not props:
        continue
    found = []
    # Not every 'type: Feature' has a 'media_url' property
    if (url := props.get('media_url')):
        found.append(url)

    # We may get the same URL multiple times for a single item (e.g. once as
    # `GEOLOCATION` and once as `LINK`). But that's not too worrisome since we
    # link the whole item anyway
    matches = re.findall(link_extract_regex, props.get('description') or '')
    if matches:
        found.extend(matches)
    for url in found:
        processed[url] = dict(
            source='CEN4INFORES',
            id=props.get('id'),
            desc=props.get('description'),
        )

if args.print:
    for key in processed.keys():
        print(f"{key}: {processed[key]}")
else:
    if not args.query:
        print("No URL supplied")
        sys.exit(1)
    if args.query in processed:
        res = processed[args.query]
        print(f"Found URL {args.query} in '{res['source']}' dataset")
        print(f"Id: {res['id']}\nDescription:\n\n{res['desc']}")
    else:
        print("URL not found in database")
