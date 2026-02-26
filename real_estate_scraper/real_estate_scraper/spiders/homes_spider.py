import scrapy
import re

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
        
        # Bedrooms number extraction
        Bedrooms = response.css('i[title="Bedroom"] + p span.font-wt-600::text').get()
        Bedrooms = int(Bedrooms.strip()) if Bedrooms else None
        # Bathrooms number extraction
        Bathrooms = response.css('i[title="Bathroom"] + p span.font-wt-600::text').get()
        Bathrooms = int(Bathrooms.strip()) if Bathrooms else None
        # Built up area extraction
        Area_sqm = response.css('i[title="Built Up Area"] + p span.font-wt-600::text').get()
        Area_sqm = float(Area_sqm.strip()) if Area_sqm else None
        # Annual and monthly rent price extraction
        section_text = ' '.join(response.xpath('//[@id="profile-description"]//text()')).getall()
        # Monthly Price rental extraction
        price_monthly = re.search(r'السعر\s*\(شهري\).*?([\d,]+)',section_text)
        price_monthly = int(price_monthly.group(1).replace(',','')) if price_monthly else None
        # Yearly Price rental extraction
        price_annualy = re.search(r'السعر\s*\(سنوي\).*?([\d,]+)',section_text)
        price_annualy = int(price_annualy.group(1).replace(',','')) if price_annualy else None

        # Property special features extraction section
        features = {}
        rows = response.css('div.row')
        for row in rows:
            label = row.css('p.font-wt-600::text').get()
            value = row.css('p.font-wt-500::text').get()
            if label and value:
                label = label.strip().replace(':','')
                value = value.strip()
                features[label] = value
        
        # Features extraction
        area_raw = features.get('مساحة بناء')
        area = float(area_raw.split()[0]) if area_raw else None
        furnished_raw = features.get('مفروش')
        furnished = 1 if furnished_raw == 'مفروشة' else 0
        pool_raw = features.get('مسبح')
        pool = 1 if pool_raw == 'نعم' else 0
        floor = features.get('الطابق')
        floor_type = features.get('نوع الطابق ')
        
        
        
            


        