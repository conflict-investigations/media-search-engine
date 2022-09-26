import csv
import re

from .base import BadFormatError, Processor

# TODO: Does not catch everything as of now! Might be better to be a negative
# lookup for illegal chars like "<", "(", "[" or a space
link_extract_regex = r"(https?://[a-zA-z0-9/.?=_-]+)"

BELLINGCAT_FIELD_NAMES = [
    'case_number',
    'listed_location',
    'date_posted',
    'link',
    'source_repost',
    'geolocation',
    'status',
    'comments',
    'discord_link',
    'checked_by_giancarlo',
]
BELLINGCAT_FIELD_COUNT = len(BELLINGCAT_FIELD_NAMES)

ENCODING = 'utf-8'  # Probably not always correct

class FileProcessor(Processor):
    """
    A "dumb" processor that reads plaintext files and extracts URLs.
    """
    def __init__(self, fileobj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fileobj = fileobj

    @staticmethod
    def read_file(fileobj):
        return fileobj.read().decode(ENCODING)

    @classmethod
    def get_data(cls):
        raise NotImplementedError

    def get_links(self):
        data = self.read_file(self.fileobj)
        matches = re.findall(link_extract_regex, data)
        return matches


class CSVFileProcessor(FileProcessor):
    @staticmethod
    def read_file(fileobj):
        header = fileobj.readline().decode(ENCODING)
        if header.count(',') != BELLINGCAT_FIELD_COUNT - 1:
            raise BadFormatError

        lines = [line.decode(ENCODING) for line in fileobj.readlines()]

        reader = csv.DictReader(
            lines,
            fieldnames=BELLINGCAT_FIELD_NAMES,
            delimiter=',',
            quotechar='"',
            restkey='extra',
            restval='',
        )
        return reader

    @staticmethod
    def extract_links(data):
        links = []
        for entry in data:
            for v in entry.values():
                matches = re.findall(link_extract_regex, v)
                for link in matches:
                    # Skip internal Bellingcat discord links
                    if 'https://discord' not in link:
                        links.append(link)
        return links

    @classmethod
    def get_data(cls, fileobj):
        entries = []

        reader = cls.read_file(fileobj)

        for row in reader:
            entries.append(row)
        return entries

    def get_links(self):
        data = self.get_data(self.fileobj)
        links = self.extract_links(data)
        return links
