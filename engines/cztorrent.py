#VERSION: 1.00
# AUTHORS: Josef Kuchař (josef@josefkuchar.com)

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter
from html.parser import HTMLParser
import requests
import tempfile
import os
import io
import gzip
from urllib.parse import unquote

# YOUR LOGIN SESSION
cookies = {}


class cztorrent(object):
    url = 'https://tracker.cztorrent.net/'
    name = 'CzTorrent'
    supported_categories = {'all': '0', 'movies': '6', 'tv': '4',
                            'music': '1', 'games': '2', 'anime': '7', 'software': '3'}

    class MyHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.inside_table = False
            self.current_column = ''
            self.data_row = False
            self.current_tag = ''
            self.last_tag = ''
            self.current_attrs = {}
            self.is_img_last = False
            self.reset_info()

        def reset_info(self):
            self.info = {
                'link': '-1',
                'name': '-1',
                'size': '-1',
                'seeds': '-1',
                'leech': '-1',
                'engine_url': 'https://tracker.cztorrent.net/',
                'desc_link': '-1',
            }

        def handle_starttag(self, tag, attrs):
            if self.inside_table:
                attrs = dict(attrs)
                self.current_attrs = attrs
                self.current_tag = tag

                if tag == 'tr':
                    if 'class' in attrs and attrs['class'] == 'torr_hover':
                        self.data_row = True

                if tag == 'td' and self.data_row:
                    if attrs['class'] == 'detaily':
                        self.current_column = 'desc'
                    if attrs['class'] == 'download':
                        self.current_column = 'download'
                    if attrs['class'] == 'peers':
                        self.current_column = 'peers'

                if tag == 'a':
                    attrs = dict(attrs)
                    if self.current_column == 'desc':
                        self.info['desc_link'] = 'https://tracker.cztorrent.net' + \
                            attrs['href']
                    if self.current_column == 'download':
                        self.info['link'] = 'https://tracker.cztorrent.net' + \
                            attrs['href']

            if tag == 'table' and dict(attrs)['id'] == 'torrenty':
                self.inside_table = True

            if tag == 'img':
                self.is_img_last = True
            else:
                self.is_img_last = False

        def handle_endtag(self, tag):
            self.current_tag = ''
            self.current_attrs = {}

            if self.inside_table:
                if tag == 'tr' and self.data_row:
                    prettyPrinter(self.info)
                    self.reset_info()

            if tag == 'td':
                self.current_column = ''

            if tag == 'table':
                self.inside_table = False

        def handle_data(self, data):
            if self.inside_table:
                if self.current_column == 'desc' and self.current_tag == 'a':
                    self.info['name'] = data

                if self.current_tag == 'span' and self.current_column == 'peers':
                    if self.info['seeds'] == '-1':
                        self.info['seeds'] = data
                    else:
                        self.info['leech'] = data

                if self.current_column == 'desc' and self.is_img_last:
                    if self.info['size'] == '-1':
                        self.info['size'] = data.replace('|', '').strip()

    def __init__(self):
        self.parser = self.MyHTMLParser()

    def download_torrent(self, info):
        file, path = tempfile.mkstemp()
        file = os.fdopen(file, "wb")
        # Download url
        response = requests.get(info, cookies=cookies)
        dat = response.content
        # Check if it is gzipped
        if dat[:2] == b'\x1f\x8b':
            # Data is gzip encoded, decode it
            compressedstream = io.BytesIO(dat)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            extracted_data = gzipper.read()
            dat = extracted_data

        # Write it to a file
        file.write(dat)
        file.close()
        # return file path
        print(path + " " + info)

    def search(self, what, cat='all'):
        params = {
            's': unquote(what),
            't': 3,
        }
        response = requests.get(
            'https://tracker.cztorrent.net/torrents/', params=params, cookies=cookies)
        self.parser.feed(response.text)
