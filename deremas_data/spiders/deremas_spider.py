# coding: utf-8
from scrapy import Request
from scrapy import Spider


class DeremasSpider(Spider):
    name = 'deremas'
    start_urls = ['http://seesaawiki.jp/imascg/l/']

    def parse(self, response):
        pages = response.xpath(
            '//*[@id="page-body-inner"]/ul/li[*]/a/@href'
        ).extract()
        for page in pages:
            yield Request(page, callback=self.parse_idol)

        # 次のページをたどる
        next_page = response.xpath(
            '//*[@id="page-body-inner"]/div[2]/ul/li[2]/a/@href'
        ).extract_first()
        if next_page:
            yield Request(next_page, callback=self.parse)

    def parse_idol(self, response):
        def is_idol_page(res):
            same_idol_box_label = res.xpath(
                '//*[@id="content_1"]/text()'
            ).extract_first()
            if isinstance(same_idol_box_label, str):
                return '同名アイドル' == same_idol_box_label.strip()
            else:
                return False

        def extract_idol_name(res):
            return res.xpath(
                '//*[@id="page-header-inner"]/div[1]/div/h2/text()'
            ).extract_first().strip()

        def extract_lines(res):
            lines = {}
            lines['before_training'] = res.xpath(
                '//*[@id="content_block_13"]/tbody/tr[*]/td[2]/text()'
            ).extract()
            lines['after_training'] = res.xpath(
                '//*[@id="content_block_24"]/tbody/tr[*]/td[2]/text()'
            ).extract()
            return lines

        if is_idol_page(response):
            yield {
                'name': extract_idol_name(response),
                'lines': extract_lines(response)
            }
