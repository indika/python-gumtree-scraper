#!/usr/bin/env python

"""GumtreeScraper

Gumtree scraper written in Python

Derived from
Copyright 2013 Oli Allen <oli@oliallen.com>


Usage:
   gumtree_scraper.py
   gumtree_scraper.py --load-from-cache
   gumtree_scraper.py --debug-ad

Options:
    -h --help     Show this screen.
    --version     Show version.


"""
from entities.GTItem import GTListingItem

__author__ = "Indika Piyasena"

USER_AGENT = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"

REQUEST_HEADERS = {'User-agent': USER_AGENT, }

import os, sys
import logging
import requests
import re
import pytz
import datetime

from tzlocal import get_localzone
from bs4 import BeautifulSoup
from docopt import docopt

logger = logging.getLogger(__name__)


class GumtreeScraper:
    def __init__(self, category, query="", location=""):
        self.configure_logging()
        self.arguments = docopt(__doc__, version='GumtreeScraper 0.1')

        self.category = category
        self.query = query
        self.location = location

        self.data = []
        self.cache_file = 'cache/request.cache'

        self.base_url = 'http://www.gumtree.com.au'


    def process(self):
        if self.arguments['--debug-ad']:
            logger.debug('Debugging an ad')
            with open('cache/item_one.cache', 'r') as f:
                self.parse_ad(f.read())
            exit(0)


        self.listing_results = self.doSearch()
        print self.listing_results
        pass

    def doSearch(self):
        """
        Performs the search against gumtree
        """

        if self.arguments['--load-from-cache']:
            with open(self.cache_file, 'r') as f:
                content = f.read()

        else:
            #request = requests.get("http://www.gumtree.com.au/search?q=%s&search_location=%s&category=%s" % (self.query, self.location, self.category), headers=REQUEST_HEADERS)
            url = "{0}/s-flatshare-houseshare/west-end-brisbane/page-1/c18294l3005921?ad=offering&price=0.00__200.00".format(
                self.base_url)
            logger.debug('Query URL: {0}'.format(url))
            request = requests.get(url, headers=REQUEST_HEADERS)

            with open(self.cache_file, 'w') as f:
                f.write(request.content)
                content = request.content

        listings = self.parse(content)
        self.process_listing_item(listings[0])


    def parse(self, content):
        logger.debug('Souping')
        souped = BeautifulSoup(content, "html5lib")
        logger.debug('Souping complete')

        listing_query = souped.find_all("div", {"class": "rs-ad-field",
                                                "class": "rs-ad-detail"})

        logger.debug('Number of listings: {0}'.format(len(listing_query)))

        items = []

        for listing in listing_query:
            title = listing.find("a", class_="rs-ad-title").contents
            item_instance = GTListingItem(title=title)
            item_instance.url = self.base_url + listing. \
                find("a", class_="rs-ad-title").get("href")
            item_instance.summary = listing.find("p",
                                                 class_="word-wrap").contents

            items.append(item_instance)

            #print listing
            #print '<a href="{0}">Link</a>'.format(item_instance.url)

        return items

    def process_listing_item(self, listing_item):
        print listing_item.url
        request = requests.get(listing_item.url, headers=REQUEST_HEADERS)

        with open('cache/item_one.cache', 'w') as f:
            f.write(request.content)

        content = request.content

        pass

    def parse_ad(self, ad_content):
        logger.debug('Souping ad')
        souped = BeautifulSoup(ad_content, "html5lib")
        main_box = souped.find("div", {"class": "white-box"})
        main_content = main_box.find("p", {"id":"vip-description"})
        print main_content

    def configure_logging(self):
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        pass


if __name__ == "__main__":
    print "Running GumtreeScraper in stand-alone-mode"

    #server_tz = pytz.timezone("UTC")
    server_tz = get_localzone()
    local_tz = pytz.timezone("Australia/Brisbane")

    typical_datetime_object = datetime.datetime.now()
    now_server = server_tz.localize(typical_datetime_object)
    now_local = now_server.astimezone(server_tz)
    print now_local

    gumtree_scraper = GumtreeScraper('s-flatshare-houseshare')
    gumtree_scraper.process()
