"""
1) Тут я решил использовать парсер selectolax, написанный на cython т.к. он быстрее в несколько раз beautifulsoup4
2) Нет смысла использовать асинхронный aiohttp или httpx, т.к. парсинг все равно будет блокировать event loop
"""

from __future__ import annotations

import csv
import logging
from collections import defaultdict
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import requests
from selectolax.parser import HTMLParser

if TYPE_CHECKING:
    from typing import Final

    from requests import Response
LOG_DEFAULT_FORMAT: Final[str] = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
RUSSIAN_ALPHABET: Final[str] = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def configure_logging(
    level: int = logging.INFO,
    format_: str = LOG_DEFAULT_FORMAT,
    datefmt: str = LOG_DATE_FORMAT,
) -> None:
    logging.basicConfig(
        level=level,
        format=format_,
        datefmt=datefmt,
    )


log = logging.getLogger(__name__)


def save_animal_counts_to_csv(counts: defaultdict[str, int], filename: str = "beasts.csv") -> None:
    log.info("Сохранение результатов в файл %s", filename)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for letter in sorted(counts.keys(), key=lambda x: RUSSIAN_ALPHABET.index(x[0])):
            writer.writerow([letter, counts[letter]])
    log.info("Успешно сохранено %d записей", len(counts))


def get_animal_counts() -> None:
    base_url: Final[str] = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"
    next_page_url = base_url
    counts = defaultdict(int)

    log.info("Начало сбора данных о животных")

    page_num = 1
    while next_page_url:
        log.info("Обработка страницы #%d (%s)", page_num, next_page_url)

        try:
            response: Response = requests.get(next_page_url, timeout=10)
            response.raise_for_status()
            parser: HTMLParser = HTMLParser(response.text)

            category_div = parser.css_first("div.mw-category.mw-category-columns")
            if not category_div:
                log.warning("Не найдена категория животных на странице")
                break

            for group in category_div.css("div.mw-category-group"):
                letter = group.css_first("h3").text()
                if letter in RUSSIAN_ALPHABET:
                    items = group.css("li")
                    counts[letter] += len(items)
                    log.debug("Буква %s: найдено %d животных", letter, len(items))

            next_link = None
            for link in parser.css("a"):
                if link.text().strip() == "Следующая страница":
                    next_link = link
                    break

            if next_link:
                next_page_url = urljoin(base_url, next_link.attributes["href"])
                page_num += 1
            else:
                next_page_url = None
                log.info("Достигнута последняя страница")

        except Exception as e:
            log.error("Ошибка при обработке страницы: %s", str(e))
            break

    log.info("Всего обработано %d страниц", page_num - 1)
    save_animal_counts_to_csv(counts=counts)


if __name__ == "__main__":
    configure_logging()
    get_animal_counts()
    log.info("Программа успешно завершена")
