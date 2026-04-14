import os, sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox
)
#from sklearn.feature_extraction.text import TfidfVectorizer
from vectorizer import StructuralSentenceVectorizer
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import joblib
import re

class FormatterTrainerUnsupervised(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RadTrack Formatter Trainer (Unsupervised)")
        self.resize(600, 300)
        self.df = None
        self.sentences = []
        self.model = None

        self.output_dir = ''

        self.layout = QVBoxLayout(self)

        self.status_label = QLabel("Step 1: Load Excel file")
        self.layout.addWidget(self.status_label)

        self.load_btn = QPushButton("📂 Load Excel File")
        self.load_btn.clicked.connect(self.load_excel)
        self.layout.addWidget(self.load_btn)

        self.col_selector = QComboBox()
        self.layout.addWidget(QLabel("Step 2: Choose Report Column"))
        self.layout.addWidget(self.col_selector)

        self.train_btn = QPushButton("🤖 Auto-Analyze & Train Formatter Model")
        self.train_btn.clicked.connect(self.train_unsupervised)
        self.layout.addWidget(self.train_btn)

        self.save_btn = QPushButton("💾 Save Formatter Model")
        self.save_btn.clicked.connect(self.save_model)
        self.layout.addWidget(self.save_btn)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.df = pd.read_excel(path)
            self.col_selector.clear()
            self.col_selector.addItems(self.df.columns)
            self.status_label.setText(f"✅ Loaded {len(self.df)} rows from: {path}")

            print(path)
            print(os.path.dirname(path))
            self.output_dir = os.path.dirname(path)

    def extract_sentences(self, col_name):
        raw_texts = self.df[col_name].dropna().astype(str).tolist()
#        seen = set()
        all_sentences = []
        for report_idx, report in enumerate(raw_texts):
            lines = re.split(r'(?<=[:.!?])\s+', report)
            cleaned = []
            for line in lines:
                line = line.strip()
                if not line:  continue
#                if not line or line in seen or len(line) > 250:
#                    continue
#                if len(line.split()) < 2:
#                    continue
#                seen.add(line)
                cleaned.append(line)

            n = len(cleaned)
            all_sentences.extend([
                {
                    'text': line,
                    'report_index': report_idx,
                    'sentence_index': i,
                    'num_sentences_in_report': n,
                }
                for i,line in enumerate(cleaned)
            ])
           
        return all_sentences

    def train_unsupervised(self):
        if self.df is None:
            QMessageBox.warning(self, "Error", "Please load an Excel file first.")
            return
        col = self.col_selector.currentText()
        self.sentences = self.extract_sentences(col)

        if len(self.sentences) < 20:
            QMessageBox.warning(self, "Too Few Sentences", "Need at least 20 distinct sentences.")
            return

        # TF-IDF vectorization
#        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
#        X = vectorizer.fit_transform(self.sentences)
        vectorizer = StructuralSentenceVectorizer(normalize_length=True)
        X = vectorizer.fit_transform(self.sentences)

        # Clustering into 4 types (header, para start, numbered, continuation)
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(X)

        # identify cluster corresponding to headers
        cluster_centers = kmeans.cluster_centers_
        feature_percent_caps_idx = list(vectorizer.get_feature_names_out()).index('percent_capital_letters')
        header_cluster_idx = cluster_centers[:,feature_percent_caps_idx].argmax()

        # reassign header cluster to be cluster 0
        clusters_adj = clusters.copy()
        clusters_adj[clusters==0] = header_cluster_idx
        clusters_adj[clusters==header_cluster_idx] = 0

        # Train classifier to recognize new sentences
        classifier = LogisticRegression(max_iter=500)
        classifier.fit(X, clusters_adj)
        classifier_clusters = classifier.predict(X)

#        keys = ['text', 'report_index', 'sentence_index', 'num_sentences_in_report']
#        raw_output = [
#          [sentence[k] for k in keys] + list(X[i,:]) + [clusters_adj[i], classifier_clusters[i]]
#          for i, sentence in enumerate(self.sentences)
#        ]
#        raw_output_pd = pd.DataFrame(raw_output, columns = keys + list(vectorizer.get_feature_names_out()) + ['cluster_idx', 'logistic_regression_cluster_idx'], dtype=object)
#        raw_output_pd.to_csv(os.path.join(self.output_dir, 'FORMATTER_test_output.csv'))

        # Save the pipeline
        self.model = Pipeline([
            ("vectorizer", vectorizer),
            ("classifier", classifier)
        ])

        self.status_label.setText("✅ Formatter model trained from pattern discovery!")

    def save_model(self):
        if self.model is None:
            QMessageBox.warning(self, "No Model", "Please train the model first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Formatter Model", "formatter_model.pkl", "Pickle Files (*.pkl)")
        if path:
            joblib.dump(self.model, path)
            self.status_label.setText(f"✅ Saved model to {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FormatterTrainerUnsupervised()
    window.show()
    sys.exit(app.exec_())
