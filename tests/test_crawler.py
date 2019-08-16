import unittest
from source.grabber import Crawler, LogStorageOS


class TestCrawlerMethods(unittest.TestCase):
    STORAGE_PATH = "./tests/test-data/"

    def _ctor_crawler(self):
        """
        construct Crawler class
        """

        storage = LogStorageOS(self.STORAGE_PATH)
        return Crawler(storage)

    def test_get_shirt_html(self):
        with open('./tests/test-data/shirt.html', 'r') as my_file:  # dev server
            result = my_file.read().replace('\n', '')
        self.assertIsNotNone(result)
        return result

    def test_parse_price(self):
        web = self._ctor_crawler()
        price = web.parse_price('CHF 90.00')
        self.assertEqual(price, '90.00')

    def test_parse_price_failing(self):
        web = self._ctor_crawler()
        with self.assertRaises(Exception):
            web.parse_price('abcdef')

    def test_parse_html_way1(self):
        web = self._ctor_crawler()
        page = self.test_get_shirt_html()
        data = web.parse_html(page, "//div[@class='h-text h-color-black title-typo h-p-top-m']/text()")
        self.assertEqual(data, u'CHF\xa0105.00')

    def test_parse_html_way2(self):
        web = self._ctor_crawler()
        page = self.test_get_shirt_html()
        data = web.parse_html(page, "//div[contains(@class, 'h-product-price')]/div/text()")
        self.assertEqual(data, u'CHF\xa0105.00')

    def test_parse_html_failing(self):
        web = self._ctor_crawler()
        page = self.test_get_shirt_html()
        with self.assertRaises(Exception):
            web.parse_html(page, "//div[@class='h-text h-color-black title-typo']/text()")


if __name__ == '__main__':
    unittest.main()
