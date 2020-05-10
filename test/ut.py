import unittest
import summariser.src.scraper as scraper
import summariser.src.summariser as summariser
import commons.database_io as database_io
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


class SummariserUT(unittest.TestCase):
    summariser.download_dependencies()
    lemmatiser = summariser.initialise_lemmatiser()
    stopws = summariser.load_stop_words()
    model = summariser.load_word_embedding_model("/Users/kappa/repositories/glove.6B/glove.6B.50d.txt")

    def test_lemmatiser(self):
        w = "queen"
        lemma = "queen"
        self.assertEqual(lemma, summariser.get_word_lemma(self.lemmatiser, w),
                         "The lemma of the word \"queen\" is queen:")

        w = "champions"
        lemma = "champion"
        self.assertEqual(lemma, summariser.get_word_lemma(self.lemmatiser, w),
                         "The lemma of champions is its singular version, champion")

        w = "khaled"
        lemma = "khaled"
        self.assertEqual(lemma, summariser.get_word_lemma(self.lemmatiser, w),
                         "The lemma of an unknown word is the same word")

    def test_preprocess_text(self):
        input_text = "Hi! My name is Khaled"
        expected_output = "hi name khaled"

        self.assertEqual(expected_output, summariser.preprocess_text(input_text, self.stopws, self.lemmatiser),
                         "Stop words and special characters are removed and text is lowercased")

        input_text = "@Classes!"
        expected_output = "class"
        self.assertEqual(expected_output, summariser.preprocess_text(input_text, self.stopws, self.lemmatiser),
                         "Special characters are removed and lemmatisation is applied")

    def test_split_text_into_sentences(self):
        text = ["Hi to everyone! I am Khaled"]
        expected_output = ["Hi to everyone!", "I am Khaled"]
        self.assertEqual(expected_output, summariser.split_text_into_sentences(text),
                         "The method is able to split sentences in a single string ")
        text = ["Hi! My Name is Khaled",
                "I am 25 years old.",
                "This is another paragraph: what do you think? I hope you like it"]
        expected_output = ["Hi!",
                           "My Name is Khaled",
                           "I am 25 years old.",
                           "This is another paragraph: what do you think?",
                           "I hope you like it"]
        self.assertEqual(expected_output, summariser.split_text_into_sentences(text),
                         "The method is able to split sentences in a list")

    def test_filter_sentences_by_length(self):
        text = ["Short sentence", "This, instead, is a long sentence"]
        min_length = 0
        self.assertEqual(text, summariser.filter_sentences_by_length(text, min_length))
        min_length = 3
        self.assertEqual([text[1]], summariser.filter_sentences_by_length(text, min_length))

    def test_get_sentences_by_score(self):
        text = ["hi, my name is khaled and yours?",
                "i like watching movies",
                "my favourite tv show is made by another khaled",
                "the movie i hate the most is titanic and yours?"]
        scores = [100, 50, 110, 1]
        scored_sentences = summariser.get_sentences_by_scores(n=4, scores=scores, sentences=text, maximise_score=True)
        self.assertEqual(text, scored_sentences,
                         "If summary length is equal to the original text length they should be the same")

        scored_sentences = summariser.get_sentences_by_scores(n=2, scores=scores, sentences=text, maximise_score=True)
        expected_output = [text[0], text[2]]
        self.assertEqual(expected_output, scored_sentences,
                         "Check if the summary has the first and third sentence")

    def test_create_summary(self):
        text = ["hi, my name is khaled and yours?",
                "i like watching movies",
                "my favourite tv show is made by another khaled :) ",
                "the movie i hate the most is titanic and yours?"]

        summary = summariser.create_summary(text, self.model, 2, 1, "tf_idf")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.model, 2, 1, "pagerank")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.model, 2, 1, "invalid_method")
        self.assertTrue(summary == "")


class DatabaseIOUT(unittest.TestCase):
    old_articles = [{'title': "pippo", 'url': "https://i.com", 'source': "TheGuardian"},
                    {'title': "abc", 'url': "http://google.xyz", 'source': "Khaled"}]
    new_articles = [{'title': "pippo", 'url': "https://i.com", 'source': "TheGuardian"},
                    {'title': "abc", 'url': "http://google.xyz", 'source': "Khaled"},
                    {'title': "Praise the UT", 'url': "http://truth.abc", 'source': "Master"}]
    diff = [{'title': "Praise the UT", 'url': "http://truth.abc", 'source': "Master"}]

    def test_get_new_articles(self):
        self.assertEqual(self.diff,
                         database_io.get_delta(self.old_articles, self.new_articles),
                         "Difference in normal scenario")
        self.assertEqual([],
                         database_io.get_delta(self.old_articles, []),
                         "If there aren't new articles the delta must be empty")
        self.assertEqual(self.new_articles,
                         database_io.get_delta([], self.new_articles),
                         "If there aren't old articles the delta must be equal to the new articles")

    def test_insert_data(self):
        """
        TO DO: instead of creating a local db use a stub
        :return:
        """
        database_io.update_items_in_db(self.old_articles, "test.json")
        database_io.update_items_in_db(self.old_articles, "test.json")
        articles_in_db = database_io.retrieve_items_from_db("test.json", "articles")
        self.assertEqual(self.old_articles, articles_in_db)


if __name__ == '__main__':
    unittest.main()
