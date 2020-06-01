import requests

import re
import mechanicalsoup
import html
import urllib.parse
from rdflib import ConjunctiveGraph, RDF, Namespace, RDFS, XSD, Literal


class WebCrawler(object):
    def __init__(self, url=None):
        self._url = url
        self.browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
        self._g = ConjunctiveGraph()
        self.ONT_NAMESPACE = Namespace('http://www.guitarkg.com/ontology#')
        self.INST_NAMESPACE = Namespace('http://www.guitarkg.com/data/')

    def parse(self):
        pass


class ThomannListCrawler(WebCrawler):
    def parse(self):
        self._url = 'https://www.thomann.de/de/lp-modelle.html?ls=100'
        page_nums = 6
        for page in range(page_nums):
            url_tmp = self._url + '&pg=page'
            self.browser.open(url_tmp)
            page = self.browser.get_current_page()
            divs = page.find_all("a", {"class": "article-link link"})
            unique_links = set([div['href'] for div in divs])
            for link in unique_links:
                self.browser.open(link)
                product_page = self.browser.get_current_page()
                feature_list = product_page.find('ul', {'class': 'prod-features'})
                print(feature_list)
                product_name = product_page.find('h1', {'itemprop': 'name'}).text
                print(product_name)


class ThomannManufacturerCrawler(WebCrawler):
    def parse(self):
        self._url = 'https://www.thomann.de/de/cat_brands.html?catKey=gi'
        self.browser.open(self._url)
        page = self.browser.get_current_page()
        div = page.find('div', {'class': 'rs-cat-brands-manufacturers'})
        unique_manufcaturers = div.find_all('div', {'class': "item"})
        for manuf in unique_manufcaturers:
            manuf = manuf.text.strip().replace('\xad', '')  # remove soft-hyphen '\xad'
            manuf_uri = manuf.replace(' ', '_')
            manuf_uri = self.INST_NAMESPACE["manufacturer-" + manuf_uri]
            self._g.add((manuf_uri, RDF.type, self.ONT_NAMESPACE['manufacturer']))
            self._g.add((manuf_uri, self.ONT_NAMESPACE['name'], Literal(manuf, datatype=XSD.string)))
            self._g.add((manuf_uri, RDFS.label, Literal(manuf, datatype=XSD.string)))

    def save(self):
        self._g.serialize('manufacturer.rdf')


if __name__ == '__main__':
    tlc = ThomannManufacturerCrawler()
    tlc.parse()
    tlc.save()
