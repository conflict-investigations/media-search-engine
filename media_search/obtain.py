import json
import os
from dataclasses import fields
from typing import Any, Dict, List

from geo_extractor.constants import RAW_DATA_FILENAMES, SOURCE_NAMES
from geo_extractor import DOWNLOADERS, EXTRACTORS

from .defaults import CONFIG
from .utils import normalize_and_sanitize

def get_file(sourcename: str) -> str:
    return os.path.join(CONFIG.DATA_FOLDER,
                        RAW_DATA_FILENAMES.__dict__[sourcename])

def load_source(sourcename: str) -> List[Any]:
    with open(get_file(sourcename), 'r') as f:
        data = json.loads(f.read())
    return EXTRACTORS[sourcename]().extract_events(data)

def save_source(sourcename: str) -> None:
    print(f"    Downloading {sourcename}...")
    data = DOWNLOADERS[sourcename]().download()
    with open(get_file(sourcename), 'w') as f:
        json.dump(data, f, ensure_ascii=False)

def build_mapping(events: Any) -> dict[str, List[dict]]:
    url_to_data_mapping = {}  # type: dict[str, List[dict]]
    for e in events:
        for link in e.links:
            # Some sources contain non-url sources
            if not link.startswith('http'):
                continue
            sanitized = normalize_and_sanitize(link)
            if sanitized not in url_to_data_mapping:
                url_to_data_mapping[sanitized] = []

            loc = dict(
                latitude=str(e.latitude),
                longitude=str(e.longitude),
                place_desc=e.place_desc,
            )
            date = e.date.strftime('%Y-%m-%d') if e.date else None
            url_to_data_mapping[sanitized].append(dict(
                unsanitized_url=link,
                source=e.source,
                id=e.id,
                desc=' - '.join(filter(None, (date, e.description))),
                location=loc,
            ))

    # TODO: Special case for reukraine data
    # If "magic" JSON file is not present the source will not be used
    try:
        reukraine = load_reukraine()
        for key in reukraine.keys():
            if key not in url_to_data_mapping:
                url_to_data_mapping[key] = []
            url_to_data_mapping[key].extend(reukraine[key])
    except FileNotFoundError:
        pass

    return url_to_data_mapping

# TODO: Handle this in geo_extractor
def load_reukraine() -> Dict[str, Any]:
    REUKRAINE_FILENAME = 'reukraine-full.json'
    filename = os.path.join(CONFIG.DATA_FOLDER, REUKRAINE_FILENAME)
    with open(filename, 'r') as f:
        data = json.loads(f.read())

    processed = {}  # type: dict[str, List[dict[str, Any]]]
    for item in data:
        link = item.get('link')
        # Some sources contain non-url sources
        if not link.startswith('http'):
            continue
        sanitized = normalize_and_sanitize(link)
        loc = dict(
            latitude=item.get('latitude'),
            longitude=item.get('longitude'),
            place_desc=" - ".join(filter(None, (item.get('address'),
                                                item.get('region')))),
        )
        date = ''
        if (d := item.get('happend')):  # 'happend', not a typo
            date = f'Date: {d}'
        description = " - ".join(filter(None,
                                        (date,
                                         item.get('type'),
                                         item.get('infotxt'))))
        if sanitized not in processed:
            processed[sanitized] = []

        processed[sanitized].append(dict(
            unsanitized_url=link,
            source='REUKRAINE',
            id=f"reukraine-{item.get('id')}",
            desc=description,
            location=loc,
        ))
    return processed

def ensure_data_dir() -> None:
    if not os.path.isdir(CONFIG.DATA_FOLDER):
        os.mkdir(CONFIG.DATA_FOLDER)

def download_data() -> None:
    ensure_data_dir()
    for _field in fields(SOURCE_NAMES):
        sourcename = _field.name
        # Skip DefMon3 shellings, see below
        if sourcename == SOURCE_NAMES.DEFMON:
            continue
        save_source(sourcename)
    print('  Download finished')

def load_and_generate_mapping() -> dict[str, List[dict[str, Any]]]:
    events = []
    for _field in fields(SOURCE_NAMES):
        sourcename = _field.name  # type: str
        # We're not interested in DefMon3 shellings etc. since they mostly
        # contain no useful links
        if sourcename == 'DEFMON':
            continue
        try:
            events.extend(load_source(sourcename))
        except FileNotFoundError:
            print(f"{sourcename} file missing")
            save_source(sourcename)
            events.extend(load_source(sourcename))
    processed = build_mapping(events)  # type: dict[str, List[dict[str, Any]]]
    return processed
