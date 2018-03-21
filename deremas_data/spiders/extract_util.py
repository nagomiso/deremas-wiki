# coding: utf-8
"""情報抽出ユーティリティ."""
from re import sub


LINE_XPATH_TEMPLATE = '//*[@id="{}"]//tbody/tr[*]/td[2]/text()'


def search_block_id(response, content_name):
    """要素idを検索する.

    コンテンツの名前と一致するブロックのidを検索する.

    :param response: レスポンスオブジェクト
    :param content_name: コンテンツの名前
    :return: 要素id集合
    """
    block_ids = []
    for content_id in response.xpath(
            '//div[@class="user-area"]//div/@id').extract():
        extracted_content_name = response.xpath(
            '//*[@id="{}"]//text()'.format(content_id)
        ).extract_first()
        if isinstance(extracted_content_name, str):
            if extracted_content_name.strip() == content_name:
                block_ids.append(content_id)
    return block_ids


def extract_card_name(response, data_block_id=None):
    """カード名を抽出する.

    データブロックからカード名を取得する.

    :param response: レスポンスオブジェクト
    :param data_block_id: データブロックのID
    :return: カードの名前
    """
    # データブロックIDが指定されて居ない場合は探索をする
    data_block_id = data_block_id or search_block_id(response, 'データ')[0]
    return response.xpath(
        '//*[@id="{}"]//tbody/tr[1]/td[1]/text()'.format(
            data_block_id)).extract_first()


def extract_idol_name(card_name):
    """アイドル名を抽出する.

    カード名から付属情報を除去してアイドル名にする.

    :param card_name: カードの名前
    :return: アイドルの名前
    """
    return sub(
                r'\s*?[\+＋]$',
                '',
                sub(r'^\s*?[\[［].+?[］\]]\s*?', '', card_name)
            )


def extract_type(response, data_block_id=None):
    """属性を抽出する.

    :param response: レスポンスオブジェクト
    :param data_block_id: データブロックのID
    :return: アイドルの属性
    """
    # データブロックIDが指定されて居ない場合は探索をする
    data_block_id = data_block_id or search_block_id(response, 'データ')[0]
    return response.xpath(
        '//*[@id="{}"]//tbody/tr[2]/td[2]/text()'.format(
            data_block_id)).extract_first()


def extract_memorial_episode_lines(response):
    """思い出エピソードのセリフを抽出する.

    :param response: レスポンスオブジェクト
    :return: 思い出エピソードのセリフリスト
    """
    memorial_episode_line_block_ids = search_block_id(
            response, '思い出エピソード')
    if memorial_episode_line_block_ids:
        return response.xpath(
            '//div[@id="{}"]//tbody/tr/td/text()'.format(
                memorial_episode_line_block_ids[0])
        ).extract()
    else:
        return []


def extract_lines(response):
    """セリフを抽出する.

    特訓前・特訓後・思い出エピソードのセリフを抽出する.

    :return: セリフ情報を保持した辞書オブジェクト
    """
    line_block_ids = search_block_id(response, 'セリフ集')

    def _extract_lines(index):
        """特訓前後のセリフを抽出する.

        セリフ集ブロックのidが1つだけしかない場合でも
        同一インタフェースで操作できるようにするための内部関数.
        """
        if len(line_block_ids) < index + 1:
            return []
        else:
            return response.xpath(
                LINE_XPATH_TEMPLATE.format(line_block_ids[index])
            ).extract()

    return {
        'before_training': _extract_lines(0),
        'after_training': _extract_lines(1),
        'memorial_episode': extract_memorial_episode_lines(response)
    }
