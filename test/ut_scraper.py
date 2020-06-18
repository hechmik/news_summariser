import unittest
import src.scraper as scraper
import json


class ScraperUT(unittest.TestCase):
    wired_url = "https://www.wired.co.uk/article/big-tech-geopolitics"
    politico_url = "https://www.politico.eu/article/this-guy-hasnt-changed-one-iota-coronavirus-or-not-its-the-same" \
                   "-old-trump/?utm_source=RSS_Feed&utm_medium=RSS&utm_campaign=RSS_Syndication "
    with open("../src/config/websites.json", "r") as f:
        config_websites = json.load(f)
    wired_div_class = config_websites['Wired UK']['main_class']
    politico_class = config_websites['Politico']['main_class']
    link_with_html_extension = "https://www.foreignaffairs.com/articles/middle-east/2020-04-13/next-iranian" \
                               "-revolution.html"
    link_with_mp4_extension = "https://www.theverge.com/2020/4/14/21221078/stephanie-sinclair-mashable-instagram" \
                              "-embed-copyright-lawsuit-dismissed.mp4"
    link_with_avi_extension = "https://www.theverge.com/2020/4/14/21221078/stephanie-sinclair-mashable-instagram" \
                              "-embed-copyright-lawsuit-dismissed.avi"

    def test_is_article_a_multimedia_page(self):
        self.assertFalse(scraper.is_article_a_multimedia_page(self.wired_url))
        self.assertFalse(scraper.is_article_a_multimedia_page(self.link_with_html_extension))
        self.assertTrue(scraper.is_article_a_multimedia_page(self.link_with_mp4_extension))
        self.assertTrue(scraper.is_article_a_multimedia_page(self.link_with_avi_extension))

    def test_download_wired_page(self):
        page = scraper.scrape_page(self.wired_url, self.wired_div_class, 0, 0)
        self.assertTrue(len(page) > 0)

    def test_download_page_skipping_paragraphs(self):
        page = scraper.scrape_page(self.wired_url, self.wired_div_class, 0, 0)
        n_last_paragraphs_to_skip = 2
        reduced_page = scraper.scrape_page(self.wired_url, self.wired_div_class, 0, n_last_paragraphs_to_skip)
        self.assertTrue(len(page) == len(reduced_page) + n_last_paragraphs_to_skip,
                        "The downloaded page is missing 2 paragraphs")
        self.assertTrue(page[:-n_last_paragraphs_to_skip] == reduced_page,
                        "The content is the same, excluding the last 2 paragraphs")

        n_first_paragraphs_to_skip = 3
        reduced_page = scraper.scrape_page(self.wired_url, self.wired_div_class, n_first_paragraphs_to_skip, 0)
        self.assertTrue(len(page) == len(reduced_page) + n_first_paragraphs_to_skip,
                        "The downloaded page is missing 3 paragraphs")
        self.assertTrue(page[n_first_paragraphs_to_skip:] == reduced_page,
                        "The content is the same, excluding the first 3 paragraphs")

        reduced_page = scraper.scrape_page(self.wired_url, self.wired_div_class, n_first_paragraphs_to_skip,
                                           n_last_paragraphs_to_skip)
        self.assertTrue(len(page) == len(reduced_page) + n_first_paragraphs_to_skip + n_last_paragraphs_to_skip,
                        "The downloaded page is missing 5 paragraphs")
        self.assertTrue(page[n_first_paragraphs_to_skip:- n_last_paragraphs_to_skip] == reduced_page,
                        "The content is the same, excluding the first 3 and last 2 paragraphs")

    def test_download_politico_page(self):
        page = scraper.scrape_page(self.politico_url, self.politico_class, 5, 0)
        self.assertTrue(len(page) > 0)


if __name__ == '__main__':
    unittest.main()
