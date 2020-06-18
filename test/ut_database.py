import unittest
import src.database_io as database_io


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
        database_io.update_items_in_db(self.old_articles, "test.json", "articles")
        database_io.update_items_in_db(self.old_articles, "test.json", "articles")
        articles_in_db = database_io.retrieve_items_from_db("test.json", "articles")
        self.assertEqual(self.old_articles, articles_in_db)


if __name__ == '__main__':
    unittest.main()
