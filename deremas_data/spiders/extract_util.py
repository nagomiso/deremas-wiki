# coding: utf-8
"""情報抽出ユーティリティ."""
import typing
from functools import partial
from re import sub

import neologdn

CIRCLE_PATTERN = (
    "[\u25cf\u25ef\u20d8\u20dd\u25cc\u25cd"
    "\u25d9\u26aa\u26ab\u26ac\u274d\u2b55"
    "\u2b24\u2b58\uffee]"
)

_normalize_circle_char = partial(sub, pattern=CIRCLE_PATTERN, repl="\u25cb")


def search_block_id(response, content_name):
    """要素idを検索する.

    コンテンツの名前と一致するブロックのidを検索する.

    :param response: レスポンスオブジェクト
    :param content_name: コンテンツの名前
    :return: 要素id集合
    """
    block_ids = []
    for content_id in response.xpath('//div[@class="user-area"]//div/@id').extract():
        extracted_content_name = response.xpath(
            f'//*[@id="{content_id}"]//text()'
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
    data_block_id = data_block_id or search_block_id(response, "データ")[0]
    return response.xpath(
        f'//*[@id="{data_block_id}"]//tbody/tr[1]/td[1]/text()'
    ).extract_first()


def extract_idol_name(card_name):
    """アイドル名を抽出する.

    カード名から付属情報を除去してアイドル名にする.

    :param card_name: カードの名前
    :return: アイドルの名前
    """
    return sub(r"\s*?[\+＋]$", "", sub(r"^\s*?[\[［].+?[］\]]\s*?", "", card_name))


def extract_type(response, data_block_id=None):
    """属性を抽出する.

    :param response: レスポンスオブジェクト
    :param data_block_id: データブロックのID
    :return: アイドルの属性
    """
    # データブロックIDが指定されて居ない場合は探索をする
    data_block_id = data_block_id or search_block_id(response, "データ")[0]
    return response.xpath(
        f'//*[@id="{data_block_id}"]//tbody/tr[2]/td[2]/text()'
    ).extract_first()


def extract_memorial_episode_lines(response):
    """思い出エピソードのセリフを抽出する.

    :param response: レスポンスオブジェクト
    :return: 思い出エピソードのセリフリスト
    """
    memorial_episode_line_block_ids = search_block_id(response, "思い出エピソード")
    if memorial_episode_line_block_ids:
        return response.xpath(
            f'//div[@id="{memorial_episode_line_block_ids[0]}"]/' "/tbody/tr/td/text()"
        ).extract()
    else:
        return []


def normalize_text(text: str) -> str:
    """テキストを正規化する.

    :param text: 正規化対象テキスト
    :return: 正規化後テキスト
    """
    normalized_text = neologdn.normalize(text)
    return str(_normalize_circle_char(string=normalized_text))


def normalize_texts(texts: typing.Collection[str]) -> typing.Collection[str]:
    """テキストのリストを正規化する.

    :param texts: 正規化対象テキストコレクション.
    :return: 正規化後テキストコレクション.
    """
    return [normalize_text(text=text) for text in texts]


def extract_lines(response):
    """セリフを抽出する.

    特訓前・特訓後・思い出エピソードのセリフを抽出する.

    :return: セリフ情報を保持した辞書オブジェクト
    """
    line_block_ids = search_block_id(response, "セリフ集")

    def _extract_lines(index):
        """特訓前後のセリフを抽出する.

        セリフ集ブロックのidが1つだけしかない場合でも
        同一インタフェースで操作できるようにするための内部関数.
        """
        if len(line_block_ids) < index + 1:
            return []
        else:
            return response.xpath(
                f'//*[@id="{line_block_ids[index]}"]//tbody/tr[*]/td[2]/text()'
            ).extract()

    before_training_lines = _extract_lines(0)
    after_training_lines = _extract_lines(1)
    memorial_episode_lines = extract_memorial_episode_lines(response)

    return {
        "raw": {
            "before_training": before_training_lines,
            "after_training": after_training_lines,
            "memorial_episode": memorial_episode_lines,
        },
        "normalized": {
            "before_training": normalize_texts(before_training_lines),
            "after_training": normalize_texts(after_training_lines),
            "memorial_episode": normalize_texts(memorial_episode_lines),
        },
    }
