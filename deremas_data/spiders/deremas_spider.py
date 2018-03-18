# coding: utf-8
"""デレマス情報抽出用Spider."""
from scrapy import Request
from scrapy import Spider

import deremas_data.spiders.extract_util as util


exclude_card_names = {'（アイドル名）'}


class DeremasSpider(Spider):
    """デレマス情報抽出用Spiderクラス."""
    name = 'deremas'
    start_urls = ['http://seesaawiki.jp/imascg/l/']

    def parse(self, response):
        pages = response.xpath(
            '//*[@id="page-body-inner"]/ul/li[*]/a/@href'
        ).extract()
        for page in pages:
            yield Request(page, callback=self.parse_idol)

        next_page = response.xpath(
            '//*[@id="page-body-inner"]/div[2]/ul/li[2]/a/@href'
        ).extract_first()
        if next_page:
            yield Request(next_page, callback=self.parse)

    def parse_idol(self, response):
        profile_block_ids = util.search_block_id(response, 'プロフィール')
        line_block_ids = util.search_block_id(response, 'セリフ集')
        if profile_block_ids and line_block_ids:
            card_name = util.extract_card_name(response)
            if card_name not in exclude_card_names:
                idol_name = util.extract_idol_name(card_name)
                type_name = util.extract_type(response)
                yield {
                    'idol_name': idol_name,
                    'card_name': card_name,
                    'type': type_name,
                    'lines': util.extract_lines(response)
                }
