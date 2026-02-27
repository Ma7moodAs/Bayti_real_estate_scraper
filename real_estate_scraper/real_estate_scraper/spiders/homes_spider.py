import scrapy
import re

class HomesSpiderSpider(scrapy.Spider):
    name = "homes_spider"
    allowed_domains = ["www.homes-jordan.com"]
    start_urls = [r"https://www.homes-jordan.com/ar/property/rent/%D8%B4%D9%82%D8%A9?t=1&adt=1",
                  r"https://www.homes-jordan.com/ar/property/sale/%D8%B4%D9%82%D8%A9?t=1&adt=2"]

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'CLOSESPIDER_ITEMCOUNT': 1000,
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY':2,
        'AUTOTHROTTLE_MAX_DELAY': 10   
            }

    def parse(self, response):

        listing_type = 'rent' if 'rent' in response.url else 'sale'

        # Extract the property links from the listing page
        cards = response.css('div.card-body')
        for card in cards:
            property_link = card.css('a[href*="HMM"]::attr(href)').get()

            if property_link:
                yield response.follow(property_link,
                                      callback = self.parse_property,
                                      meta = {'listing_type': listing_type} )

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page,
                                  callback = self.parse,
                                  meta = {'listing_type':listing_type})
            

    def parse_property(self,response):
        
        # Extract the listing type from the meta data
        listing_type = response.meta.get('listing_type')

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
        #section_text = ' '.join(response.xpath('//*[@id="profile-description"]//text()')).getall()
        section_text = ' '.join(response.xpath('//*[@id="profile-description"]//text()').getall())
        
        price_monthly = None
        price_annualy = None
        sale_price = None
        
        price_lines = response.xpath('//*[@id=profile-description]//p[contains(text(),"السعر")]/text()').getall()
        
        for line in price_lines:

            line = line.replace('\xa0',' ').strip()
            number_match  = re.search(r'([\d,]+)',line)
            if not number_match:
                continue
            price_value = int(number_match.group(1).replace(',',''))
            #line_clean = line.replace('(','').replace(')','')
            if 'شهري' in line:
                price_monthly = price_value
            elif 'سنوي' in line:
                price_annualy = price_value
            else:
                sale_price = price_value
             
        # Monthly Price rental extraction
        #price_monthly = re.search(r'السعر\s*\(شهري\).*?([\d,]+)',section_text)
        #price_monthly = int(price_monthly.group(1).replace(',','')) if price_monthly else None
        # Yearly Price rental extraction
        #price_annualy = re.search(r'السعر\s*\(سنوي\).*?([\d,]+)',section_text)
        #price_annualy = int(price_annualy.group(1).replace(',','')) if price_annualy else None
        # Sale Price extraction
        #sale_price_match = re.search(r'السعر\s*:\s*([\d,]+)\s*دينار', section_text)
        #sale_price = int(sale_price_match.group(1).replace(',','')) if sale_price_match else None  
        
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

        # Location Extraction
        location_raw = response.css('p.mb-1::text').get()
        location = location_raw.strip() if location_raw else None

        # Property Description
        description =  response.xpath(
            '//div[@id="profile-description"]//strong[contains(text(),"تفاصيل الشقة")]'
            '/parent::p/following-sibling::p[1]//text()').getall()
        description = ' '.join(description).strip() if description else None

        # Property Specialities
        specialities = response.xpath(
            '//div[@id="profile-description"]//strong[contains(text(),"مميزات الشقة")]'
            '/parent::p/following-sibling::p[1]//text()').getall()
        specialities = ' '.join(specialities).strip() if specialities else None

        yield {
            'Listing_type': listing_type,
            'URL': response.url,
            'Bedrooms': Bedrooms,
            'Bathrooms': Bathrooms,
            'Area_sqm': Area_sqm,
            'Price_monthly': price_monthly if listing_type == 'rent' else None,
            'Price_annualy': price_annualy if listing_type == 'rent' else None,
            'Sale_price': sale_price if listing_type == 'sale' else None,
            'Furnished': furnished,
            'Pool': pool,
            'Floor': floor,
            'Floor_type': floor_type,
            'Location': location,
            'Description': description,
            'Specialities': specialities
        }
        
        
        
            


        