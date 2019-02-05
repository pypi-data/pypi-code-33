# -*- coding: utf-8 -*-

import scrapy


class BotItem(scrapy.Item):
    unique_control = scrapy.Field()
    organization = scrapy.Field()
    document = scrapy.Field()
    departament = scrapy.Field()
    process_number = scrapy.Field()
    ticket_id = scrapy.Field()
    ticket_number = scrapy.Field()
    ticket_creation_date = scrapy.Field()
    ticket_type_code = scrapy.Field()
    vehicle_plate = scrapy.Field()
    ticket_status = scrapy.Field()
    ticket_pdf_url = scrapy.Field()
    imported = scrapy.Field()
    s3_directory = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()