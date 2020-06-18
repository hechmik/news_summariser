import unittest
import src.summariser as summariser
import src.transformers_summaries as transformers_summaries
import numpy as np
import word_mover_distance.model as model


class SummariserUT(unittest.TestCase):
    summariser.download_dependencies()
    lemmatiser = summariser.initialise_lemmatiser()
    stopws = summariser.load_stop_words()
    we = model.WordEmbedding(model_fn="/Users/kappa/repositories/glove.6B/glove.6B.50d.txt")
    cosine_model = {"distance_metric": "cosine", "model_object": we}
    wmd_model = {"distance_metric": "wmd", "model_object": we}
    bart_model = transformers_summaries.load_transformer_model("bart")
    t5_model = transformers_summaries.load_transformer_model("t5")

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
        expected_output = ["hi", "name", "khaled"]

        self.assertEqual(expected_output, summariser.preprocess_text(input_text, self.stopws, self.lemmatiser),
                         "Stop words and special characters are removed and text is lowercased")

        input_text = "@Classes!"
        expected_output = ['class']
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
        scored_sentences = summariser.get_sentences_by_scores(n_sentences=4,
                                                              scores=scores,
                                                              sentences=text,
                                                              maximise_score=True)
        self.assertEqual(text, scored_sentences,
                         "If summary length is equal to the original text length they should be the same")

        scored_sentences = summariser.get_sentences_by_scores(n_sentences=2,
                                                              scores=scores,
                                                              sentences=text,
                                                              maximise_score=True)
        expected_output = [text[0], text[2]]
        self.assertEqual(expected_output, scored_sentences,
                         "Check if the summary has the first and third sentence")

    def test_create_summary(self):
        text = ["hi, my name is khaled and yours?",
                "i like watching movies",
                "my favourite tv show is made by another khaled :) ",
                "the movie i hate the most is titanic and yours?",
                "I really enjoy coding, I find that its a sort of magic activity where you are able to generate new values from scratch.",
                "Apart from that, I love spending my spare time reading, watching motorsport and traveling around the world."]

        summary = summariser.create_summary(text, None, 2, 1, "tf_idf")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.cosine_model, 2, 1, "pagerank")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.wmd_model, 2, 1, "pagerank")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.bart_model, 2, 1, "bart")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.t5_model, 2, 1, "t5")
        self.assertTrue(len(summary) > 0)
        self.assertTrue(len(summary) < len(" ".join(text)), "The summary is shorter than the original text")

        summary = summariser.create_summary(text, self.cosine_model, 2, 1, "invalid_method")
        self.assertTrue(summary == "")

    def test_vectorize_sentence(self):
        sentence = "This is a normal sentence, what do you think?"
        we_model = self.cosine_model['model_object'].model
        vectorized_sentence = summariser.vectorize_sentence(sentence.split(),
                                                            we_model)
        self.assertEqual(50, len(vectorized_sentence))

        sentence = "r1jd dsjsn einwjh"
        vectorized_sentence = summariser.vectorize_sentence(sentence.split(),
                                                            we_model)
        self.assertEqual(50, len(vectorized_sentence))
        self.assertTrue(np.all(np.zeros(50) == vectorized_sentence),
                        "If no word is in the embedding model, a vector of zeros should be returned")

        s1 = "My name is what is yours?"
        s2 = "My name is Khaled what is yours?"
        vect_s1 = summariser.vectorize_sentence(s1.split(), we_model, empty_strategy="skip")
        vect_s2 = summariser.vectorize_sentence(s2.split(), we_model, empty_strategy="skip")
        self.assertTrue(np.array_equal(vect_s1, vect_s2),
                        "With skip strategy Khaled is not replaced with zeros")

        vect_s1 = summariser.vectorize_sentence(s1.split(), we_model, empty_strategy="fill")
        vect_s2 = summariser.vectorize_sentence(s2.split(), we_model, empty_strategy="fill")
        self.assertFalse(np.array_equal(vect_s1, vect_s2),
                         "With fill strategy Khaled is replaced with zeros before computing sentence average")

        vect_s2 = summariser.vectorize_sentence(s1.split(), we_model, empty_strategy="fill")
        self.assertTrue(np.array_equal(vect_s1, vect_s2),
                        "With fill strategy only equal sentences have the same vector representation")

    def test_compute_sentence_similarity(self):
        s1 = summariser.preprocess_text("Hi, my name is khaled and I love coding!",
                                        self.stopws,
                                        self.lemmatiser)
        s2 = summariser.preprocess_text("Hy, my name is khaled and I love coding!",
                                        self.stopws,
                                        self.lemmatiser)
        s3 = summariser.preprocess_text("This is an unrelated sentence, what do you think?",
                                        self.stopws,
                                        self.lemmatiser)

        score_s1_s2_cos = summariser.compute_sentence_similarity(s1, s2, self.cosine_model)
        score_s2_s3_cos = summariser.compute_sentence_similarity(s2, s3, self.cosine_model)
        self.assertTrue(score_s1_s2_cos < score_s2_s3_cos,
                        "Similar sentences should have a lower \"cosine\" score")

        score_s1_s2_wmd = summariser.compute_sentence_similarity(s1, s2, self.wmd_model)
        score_s2_s3_wmd = summariser.compute_sentence_similarity(s2, s3, self.wmd_model)
        self.assertTrue(score_s1_s2_wmd < score_s2_s3_wmd,
                        "Similar sentences should have a lower \"wmd\" score")

        self.assertTrue(score_s1_s2_wmd != score_s1_s2_cos,
                        "Changing distance metric lead to different scores")


if __name__ == "__main__":
    unittest.main()
