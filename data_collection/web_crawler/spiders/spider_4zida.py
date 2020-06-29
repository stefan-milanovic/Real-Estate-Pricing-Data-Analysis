import scrapy
import re
import sys
import requests
from lxml.html import fromstring

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            if (len(proxies) == 20):
                break
    return proxies

# Run in console using:
# scrapy crawl 4zida -o 4zida.json
class Spider_4zida(scrapy.Spider):
    name = "4zida"
    start_urls = [
        'https://www.4zida.rs/prodaja-kuca?strana=1',
        'https://www.4zida.rs/izdavanje-kuca?strana=1',
        'https://www.4zida.rs/prodaja-stanova?strana=1',
        'https://www.4zida.rs/izdavanje-stanova?strana=1'   
    ]

    searchKeys = ['Cena po m', 'Površina', 'Sprat', 'Uknjiženost', 'Grejanje', 'Broj soba', 'Godina izgradnje:', 'Unutrašnje prostorije:']
    parsedData = {}
    floorsCountPresent = False

    def processResponse(self, response):

        leftColumns = [response.css('span.item-left::text'), response.css('div.font-weight-bold::text')]
        rightColumns = [response.css('span.item-right::text'), response.css('div.col-lg-9 > span::text')]

        for k in range(0, len(leftColumns)):
            for i in range (0, len(leftColumns[k].getall())):
                item = leftColumns[k][i].get()
                if (item in self.searchKeys and i < len(rightColumns[k])):
                    self.parsedData[item] = rightColumns[k][i].get()
                    if (item == self.searchKeys[2]):
                        self.floorsCountPresent = True

    def parseCssElement(self, response, cssElement, index):
        try:
            result = response.css(cssElement)[index].get()
            return result
        except IndexError:
            return ''
    
    def getFloorsInBuilding(self, response, floorIndex):
        if self.floorsCountPresent:
            arr = response.css('span.ng-star-inserted::text').getall()
            for item in arr:
                if (item.find('/') != -1):
                    return item[3]
        return ''

    def parsePage(self, response):
        self.processResponse(response)
        yield {
            'link': response.request.url,
            'offer_type' : self.parseCssElement(response, 'li.breadcrumb-item > small > a::text', 1),
            'price_per_m2' : self.parsedData[self.searchKeys[0]] if self.searchKeys[0] in self.parsedData else '',
            'city': self.parseCssElement(response, 'li.breadcrumb-item > small > a::text', 2),
            'city_area' : self.parseCssElement(response, 'li.breadcrumb-item > small > a::text', 3),
            'living_area' : self.parsedData[self.searchKeys[1]] if self.searchKeys[1] in self.parsedData else '',
            'construction_year' : self.parsedData[self.searchKeys[6]] if self.searchKeys[6] in self.parsedData else '',
            'land_size' : '',
            'floor' : self.parsedData[self.searchKeys[2]] if self.searchKeys[2] in self.parsedData else '',
            'floors_in_building' : self.getFloorsInBuilding(response, self.floorsCountPresent),
            'registered' : self.parsedData[self.searchKeys[3]] if self.searchKeys[3] in self.parsedData else '',
            'heating' : self.parsedData[self.searchKeys[4]] if self.searchKeys[4] in self.parsedData else '',
            'rooms' : self.parsedData[self.searchKeys[5]] if self.searchKeys[5] in self.parsedData else '',
            'additional_info' : self.parsedData[self.searchKeys[7]] if self.searchKeys[7] in self.parsedData else ''
        }
        self.parsedData = {}
        self.floorsCountPresent = False

    def parse(self, response):
        
        realEstatePageLinks = response.css('div.card a::attr(href)').getall()

        rentRegex = re.compile('/izdavanje/*')
        purchaseRegex = re.compile('/prodaja/*')

        rentLinksNoDuplicates = list(filter(rentRegex.match, list(set(realEstatePageLinks))))
        purchaseLinksNoDuplicates = list(filter(purchaseRegex.match, list(set(realEstatePageLinks))))

        if (len(rentLinksNoDuplicates) != 0):
            yield from response.follow_all(rentLinksNoDuplicates, self.parsePage)
        else:
            yield from response.follow_all(purchaseLinksNoDuplicates, self.parsePage)

        pageNumberRegex = re.compile('(.*\?strana=)([0-9]+)')
        linkPrefix = pageNumberRegex.match(response.request.url).group(1)
        currentPage = pageNumberRegex.match(response.request.url).group(2)

        nextPageNumber = int(currentPage) + 1
        maxPageNumber = int(response.css('li.page-item a::text')[len(response.css('li.page-item a::text').getall()) - 2].get())

        # If the next page number is larger than the maximum, end the search.
        if (nextPageNumber < maxPageNumber):
            nextPage = linkPrefix + str(nextPageNumber)
            yield response.follow(nextPage, self.parse)

    if __name__ == '__main__':
        orig_stdout = sys.stdout
        with open('proxies.txt', 'w') as output:
            sys.stdout = output
            proxies = get_proxies()
            for proxy in proxies:
                print(proxy)
        sys.stdout = orig_stdout