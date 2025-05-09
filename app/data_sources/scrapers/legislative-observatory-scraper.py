import scrapy
from scrapy.crawler import CrawlerProcess

class LegislativeObservatorySpider(scrapy.Spider):
    name = "legislative_observatory"
    start_urls = [
        "https://oeil.secure.europarl.europa.eu/oeil/en/search/export/XML?fullText.mode=EXACT_WORD&year=2025"
    ]


    def parse(self, response):
        items = response.xpath('//item')
        for entry in items:
            data = {
                'reference': type(entry.xpath('./reference/text()').get()),
                'link': type(entry.xpath('./link/text()').get()),
                'title': type(entry.xpath('./title/text()').get()),
                'lastpubdate': type(entry.xpath('./lastpubdate/text()').get()),
                'committee': type(entry.xpath('./committee/committee/text()').get()),
                'rapporteur': type(entry.xpath('./rapporteur/rapporteur/text()').get())
            }
            print(data)

            # supabase.table("legislative_files").upsert(data).execute()

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LegislativeObservatorySpider)
    process.start()
