import numpy as np
import re
from sklearn.base import BaseEstimator, TransformerMixin

class StructuralSentenceVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, normalize_length=True):
        self.normalize_length = normalize_length
        self.length_mean_ = 0.0
        self.length_std_ = 1.0

    def fit(self, X, y=None):
        lengths = [self._word_count(self._get_text(item)) for item in X]
        if self.normalize_length and len(lengths) > 0:
            self.length_mean_ = float(np.mean(lengths))
            self.length_std_ = float(np.std(lengths))
            if self.length_std_ == 0:
                self.length_std_ = 1.0
        return self

    def transform(self, X):
        features = []
        for item in X:
            text = self._get_text(item)

            word_count = self._word_count(text)
            if self.normalize_length:
                word_count_feature = (word_count - self.length_mean_) / self.length_std_
            else:
                word_count_feature = float(word_count)

            starts_with_number = float(bool(re.match(r'^\s*\d', text)))
            all_caps = float(self._is_all_caps(text))
            percent_caps = self._percent_capital_letters(text)
            ends_with_colon = float(text.rstrip().endswith(':'))
            rel_position = float(self._relative_position(item))
            percent_alpha = self._percent_alpha_characters(text)
            percent_numeric = self._percent_numeric_characters(text)

            features.append([
                word_count_feature,
                starts_with_number,
                all_caps,
                percent_caps,
                ends_with_colon,
                rel_position,
                percent_alpha,
                percent_numeric,
            ])

        return np.array(features, dtype=float)

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def get_feature_names_out(self, input_features=None):
        return np.array([
            "word_count",
            "starts_with_number",
            "all_caps",
            "percent_capital_letters",
            "ends_with_colon",
            "relative_position",
            "percent_alpha_characters",
            "percent_numeric_characters",
        ], dtype=object)

    def _get_text(self, item):
#        if isinstance(item, str):
#            return item
        return item["text"]

    def _relative_position(self, item):
        if isinstance(item, str):
            raise ValueError
#            return 0.0
        n = item["num_sentences_in_report"]
        i = item["sentence_index"]
        if n <= 1:
            return 0.0
        return i / (n - 1)

    def _word_count(self, text):
        return len(re.findall(r'\b\w+\b', text))

    def _is_all_caps(self, text):
        letters = [ch for ch in text if ch.isalpha()]
        #letters = re.findall(r'[A-Za-z]', text)
        if len(letters) < 2:
            return False
        return all(ch.isupper() for ch in letters)

    def _percent_capital_letters(self, text):
        letters = [ch for ch in text if ch.isalpha()]
        if not letters:
            return 0.0
        caps = sum(ch.isupper() for ch in letters)
        return caps / len(letters)

    def _percent_alpha_characters(self, text):
        if not text:
            return 0.0
        nums = sum(ch.isalpha() for ch in text)
        return nums / len(text)

    def _percent_numeric_characters(self, text):
        if not text:
            return 0.0
        nums = sum(ch.isdigit() for ch in text)
        return nums / len(text)
