import unittest
import src.scraper as scraper
import src.summariser as summariser


class ScraperUT(unittest.TestCase):

    url = "https://www.wired.co.uk/article/big-tech-geopolitics"
    url_class = "a-body__content has-bbcode"
    link_with_html_extension = "https://www.foreignaffairs.com/articles/middle-east/2020-04-13/next-iranian-revolution.html"
    link_with_mp4_extension = "https://www.theverge.com/2020/4/14/21221078/stephanie-sinclair-mashable-instagram-embed-copyright-lawsuit-dismissed.mp4"
    link_with_avi_extension = "https://www.theverge.com/2020/4/14/21221078/stephanie-sinclair-mashable-instagram-embed-copyright-lawsuit-dismissed.avi"

    def test_is_article_a_multimedia_page(self):

        self.assertFalse(scraper.is_article_a_multimedia_page(self.url))
        self.assertFalse(scraper.is_article_a_multimedia_page(self.link_with_html_extension))
        self.assertTrue(scraper.is_article_a_multimedia_page(self.link_with_mp4_extension))
        self.assertTrue(scraper.is_article_a_multimedia_page(self.link_with_avi_extension))

    def test_download_page(self):

        page = scraper.scrape_page(self.url, self.url_class, 0)
        self.assertTrue(len(page) > 0)
        number_of_paragraphs_to_skip = 2
        reduced_page = scraper.scrape_page(self.url, self.url_class, number_of_paragraphs_to_skip)
        self.assertTrue(len(page) == len(reduced_page) + 2)
        self.assertTrue(page[:-number_of_paragraphs_to_skip] == reduced_page)


class SummariserUT(unittest.TestCase):

    def test_lemmatiser(self):
        
        summariser.download_dependencies()
        lemmatiser = summariser.initialise_lemmatiser()
        w = "queen"
        lemma = "queen"
        self.assertEqual(lemma, summariser.get_word_lemma(lemmatiser, w), "The lemma of the word \"queen\" is queen:")

        w = "champions"
        lemma = "champion"
        self.assertEqual(lemma, summariser.get_word_lemma(lemmatiser, w), "The lemma of champions is its singular version, champion")

        w = "khaled"
        lemma = "khaled"
        self.assertEqual(lemma, summariser.get_word_lemma(lemmatiser, w), "The lemma of an unknown word is the same word")


if __name__ == '__main__':
    unittest.main()
