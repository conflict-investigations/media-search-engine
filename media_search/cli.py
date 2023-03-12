import click
import json
import os
import pickle
import sys

from .defaults import CONFIG
from .utils import normalize_and_sanitize
from media_search import obtain

@click.command()
@click.option('-j', '--json', 'json_', is_flag=True, default=False,
              help='Print all known URLs as JSON')
@click.option('-d', '--dump', 'dump_', is_flag=True, default=False,
              help='Dump pre-processed URLs as database file')
@click.option('-o', '--obtain', 'obtain_', is_flag=True, default=False,
              help='Obtain (download) files from online sources')
@click.argument('query', type=click.STRING, required=False)
def main(json_, dump_, obtain_, query) -> None:

    processed = {}

    def dump(p) -> None:
        with open(CONFIG.DUMP_FILE, 'wb') as f:
            pickle.dump(p, f)

    def ensure_dump_dir() -> None:
        if not os.path.isdir(CONFIG.DUMP_FOLDER):
            os.mkdir(CONFIG.DUMP_FOLDER)

    if obtain_:
        obtain.download_data()
        processed = obtain.load_and_generate_mapping()
        ensure_dump_dir()
        dump(processed)
        sys.exit(0)
    if dump_:
        processed = obtain.load_and_generate_mapping()
        ensure_dump_dir()
        dump(processed)
        sys.exit(0)
    try:
        with open(CONFIG.DUMP_FILE, 'rb') as f:
            processed = pickle.load(f)
    except FileNotFoundError:
        ensure_dump_dir()
        processed = obtain.load_and_generate_mapping()

    if json_:
        click.echo(json.dumps(processed, ensure_ascii=False))
        sys.exit(0)
    else:
        if not query:
            click.echo("No URL supplied")
            sys.exit(1)
        query_sanitized = normalize_and_sanitize(query)
        if query_sanitized in processed:
            results = processed[query_sanitized]
            for res in results:
                click.echo(f"Found URL {query} in '{res['source']}' dataset")
                click.echo(f"Id: {res['id']}, "
                      + f"Location: {res['location']['latitude']}, "
                      + f"{res['location']['longitude']}"
                      + f"\nDescription:\n\n{res['desc']}")
            sys.exit(0)
        else:
            click.echo("URL not found in database")
            sys.exit(1)
