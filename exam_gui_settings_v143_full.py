# Full-featured RadTrack Settings v1.4.3 with formatter model selection
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout
)
from exam_gui_main_v143_full import MainApp

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RadTrack Settings v1.4.3")
        self.resize(700, 500)
        self.df = None
        self.formatter_model_path = None  # default

        layout = QVBoxLayout(self)

        self.status_label = QLabel("Step 1: Load your Excel file")
        layout.addWidget(self.status_label)

        load_btn = QPushButton("📂 Load Excel File")
        load_btn.clicked.connect(self.load_excel)
        layout.addWidget(load_btn)

        self.col_list = QListWidget()
        self.col_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(QLabel("Step 2: Select Identifier Columns"))
        layout.addWidget(self.col_list)

        self.display_list = QListWidget()
        self.display_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(QLabel("Step 3: Select Columns to Display (One or Two)"))
        layout.addWidget(self.display_list)

        self.editable_list = QListWidget()
        self.editable_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(QLabel("Step 4: Select Editable Columns (up to 10)"))
        layout.addWidget(self.editable_list)

        formatter_row = QHBoxLayout()
        self.formatter_label = QLabel("Model: none")
        formatter_btn = QPushButton("🧠 Select Formatter Model (.pkl)")
        formatter_btn.clicked.connect(self.select_model)
        formatter_row.addWidget(self.formatter_label)
        formatter_row.addWidget(formatter_btn)
        layout.addLayout(formatter_row)

        start_btn = QPushButton("🚀 Launch RadTrack")
        start_btn.clicked.connect(self.launch_main_gui)
        layout.addWidget(start_btn)

    def load_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            try:
                self.df = pd.read_excel(path)
                self.file_path = path
                self.status_label.setText(f"✅ Loaded: {os.path.basename(path)}")
                self.populate_lists()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file:\n{e}")

    def populate_lists(self):
        self.col_list.clear()
        self.display_list.clear()
        self.editable_list.clear()
        for col in self.df.columns:
            for widget in [self.col_list, self.display_list, self.editable_list]:
                item = QListWidgetItem(col)
                widget.addItem(item)

    def select_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Formatter Model", "", "Pickle Files (*.pkl)")
        if path:
            self.formatter_model_path = path
            self.formatter_label.setText(f"Model: {os.path.basename(path)}")

    def launch_main_gui(self):
        if self.df is None:
            QMessageBox.warning(self, "Missing File", "Please load an Excel file.")
            return

        identifiers = [item.text() for item in self.col_list.selectedItems()]
        display = [item.text() for item in self.display_list.selectedItems()]
        editable = [item.text() for item in self.editable_list.selectedItems()]

        if len(display) not in [1, 2]:
            QMessageBox.warning(self, "Display Columns", "Please select 1 or 2 columns to display.")
            return
        if len(editable) > 10:
            QMessageBox.warning(self, "Editable Limit", "Please select up to 10 editable columns.")
            return

        self.main_window = MainApp(
            self.file_path,
            identifiers,
            display,
            editable,
            self.formatter_model_path
        )
        self.main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = SettingsApp()
    settings.show()
    sys.exit(app.exec_())
