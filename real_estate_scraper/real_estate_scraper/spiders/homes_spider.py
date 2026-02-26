import scrapy


class HomesSpiderSpider(scrapy.Spider):
    name = "homes_spider"
    allowed_domains = ["www.homes-jordan.com"]
    start_urls = [r"https://www.homes-jordan.com/ar/property/rent/%D8%B4%D9%82%D8%A9?t=1&adt=1",
                  r"https://www.homes-jordan.com/ar/property/sale/%D8%B4%D9%82%D8%A9?t=1&adt=2"]

    def parse(self, response):
        # Extract the property links from the listing page
        cards = response.css('div.card-body')
        for card in cards:
            property_link = card.css('a[href*="HMM"]::attr(href)').get()

            if property_link:
                yield response.follow(property_link,callback=self.parse_property)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page,callback=self.parse)

    def parse_property(self,response):
            pass

        