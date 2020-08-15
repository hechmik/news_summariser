import unittest
import src.database_io as database_io
import os


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

    def test_get_not_sent_summaries(self):
        before_sending = [
            {
                'title': "pippo",
                'url': "https://i.com",
                'source': "TheGuardian",
                "summary": "ciao",
                "sent": False
            }, {
                'title': "abc",
                'url': "http://google.xyz",
                'source': "Khaled",
                "sent": True
            }]
        database_io.insert_items_in_db(before_sending, "test_update.json", "articles")
        articles_in_db = database_io.retrieve_items_from_db("test_update.json", "sent_articles")[0]
        self.assertEqual(before_sending[0], articles_in_db, "Correctly retrieved not sent article")

    def test_insert_data(self):
        """
        TO DO: instead of creating a local db use a stub
        :return:
        """
        database_io.insert_items_in_db(self.old_articles, "test.json", "articles")
        database_io.insert_items_in_db(self.old_articles, "test.json", "articles")
        articles_in_db = database_io.retrieve_items_from_db("test.json", "articles")
        self.assertEqual(self.old_articles, articles_in_db, "articles are not added multiple times")
        os.remove("test.json")

    def test_update_items_in_db(self):
        before_sending = [
            {
                'title': "pippo",
                'url': "https://i.com",
                'source': "TheGuardian",
                "summary": "ciao",
                "sent": False
            }, {
                'title': "abc",
                'url': "http://google.xyz",
                'source': "Khaled",
                "sent": False
            }]
        database_io.insert_items_in_db(before_sending, "test_update.json", "articles")
        database_io.insert_items_in_db([{'url': 'https://i.com'}], "test_update.json", "sent_articles")
        articles_in_db = database_io.retrieve_items_from_db("test_update.json", "articles")
        # Let's keep only the fields we are interested
        articles_in_db = [{'url': x['url'], 'sent': x['sent']} for x in articles_in_db]
        self.assertEqual([{'url': 'https://i.com', 'sent': True},
                          {'url': 'http://google.xyz', 'sent': False}],
                         articles_in_db,
                         "The sent field is correctly updated")
        os.remove("test_update.json")


if __name__ == '__main__':
    unittest.main()
