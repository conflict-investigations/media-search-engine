import argparse
import json
import pickle
import sys

from .defaults import CONFIG
from media_search import obtain

def main():
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
    parser.add_argument('-o', '--obain',
        action='store_true', dest='obtain',
        default=False,
        help="Obtain (download) files from online sources")
    parser.add_argument('query', nargs='?', default=None,
        type=str, help='URL query')
    args = parser.parse_args()

    processed = {}

    def dump():
        with open(CONFIG.DUMP_FILE, 'wb') as f:
            pickle.dump(processed, f)

    if args.obtain:
        obtain.download_data()
        dump()
        sys.exit(0)
    if args.load:
        with open(CONFIG.DUMP_FILE, 'rb') as f:
            processed = pickle.load(f)
    else:
        processed = obtain.load_and_generate_mapping()
    if args.dump:
        dump()
        sys.exit(0)

    if args.print:
        for key in processed.keys():
            for item in processed[key]:
                print(f"Url: {key}\nId: {item['id']}\nDescription:\n{item['desc']}\n")  # noqa
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
