
# -*- coding: utf-8 -*-
import sys
import os
import platform
import pandas as pd
import re
import joblib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QMessageBox, QCheckBox, QCompleter,
    QShortcut
)
from PyQt5.QtGui import (
    QTextCharFormat, QTextCursor, QColor, QTextDocument, QKeySequence
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QStringListModel

class MainApp(QWidget):
    def __init__(self, excel_file, identifier_columns, display_columns, editable_columns, formatter_model_path):
        super().__init__()
        self.setWindowTitle("RadTrack v1.4.3")
        self.resize(1600, 950)

        self.excel_file = excel_file
        self.df = pd.read_excel(excel_file)
        self.identifier_columns = identifier_columns
        self.display_columns = display_columns
        self.editable_columns = editable_columns
        self.formatter_model_path = formatter_model_path
        self.current_index = 0
        self.output_file = self.generate_output_filename()
        self.use_formatter = True

        self.load_formatter_model()
        self.init_ui()
        self.load_row()

#    def setup_autocomplete(self):
#        self.row_map = {}
#        self.completer_model = QStringListModel()
#        self.completer = QCompleter()
#        self.completer.setModel(self.completer_model)
#        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
#        self.completer.activated.connect(self.on_completer_selected)
#        self.search_input.setCompleter(self.completer)

    def on_completer_selected(self, text):
        key = text.lower().strip()
        if key in self.row_map:
            self.save_row()
            self.current_index = self.row_map[key]
            self.load_row()

    def generate_output_filename(self):
        base = os.path.splitext(self.excel_file)[0]
        return f"{base}_edited_output.xlsx"

    def load_formatter_model(self):
        try:
            self.formatter_model = joblib.load(self.formatter_model_path)
        except Exception as e:
            QMessageBox.critical(self, "Model Load Error", f"Failed to load formatter model: {e}")
            sys.exit(1)

    def init_ui(self):
        # Platform-specific toggles
        if platform.system() == 'Darwin': # mac
            cmd_keys = ['Ctrl+', 'Meta+']
            cmd_key_text = '⌘'
        else:
            cmd_key = ['Ctrl+']
            cmd_key_text = 'Ctrl+'

        layout = QVBoxLayout()

        self.id_label = QLabel()
        self.id_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.id_label)

#        search_row = QHBoxLayout()
#        self.search_input = QLineEdit()
#
#        self.search_input.setPlaceholderText("🔍 Search by row number or identifier...")

#        self.search_input.returnPressed.connect(self.search_row)
#        self.setup_autocomplete()

#        self.search_input.returnPressed.connect(self.search_row)

#        self.setup_autocomplete()

#        search_row.addWidget(self.search_input)
#        layout.addLayout(search_row)

        content_split = QHBoxLayout()

        display_layout = QVBoxLayout()
        self.display_texts = []
        for col in self.display_columns:
            label = QLabel(f"<b>{col}</b>")
            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setStyleSheet("font-family: Courier; font-size: 14px;")
            self.display_texts.append((label, text_area))
            display_layout.addWidget(label)
            display_layout.addWidget(text_area)
        content_split.addLayout(display_layout, stretch=2)

        tool_layout = QVBoxLayout()

        highlight_layout = QFormLayout()
        self.highlight_inputs = {}
        for color in ["yellow", "blue", "green", "red", "purple"]:
            inp = QLineEdit()
            inp.setPlaceholderText("term1|term2|term3|...")
            inp.textChanged.connect(self.refresh_highlights)
            self.highlight_inputs[color] = inp
            highlight_layout.addRow(f"{color.capitalize()}:", inp)

##        self.bold_input = QLineEdit()
##        self.bold_input.setPlaceholderText("Bold & Underline")
##        self.bold_input.textChanged.connect(self.refresh_highlights)
##        highlight_layout.addRow("Bold & Underline:", self.bold_input)

        highlight_box = QGroupBox("Highlighting Tools")
        highlight_box.setLayout(highlight_layout)
        tool_layout.addWidget(highlight_box)

        edit_layout = QFormLayout()
        self.edit_fields = {}
        for col in self.editable_columns:
            field = QLineEdit()
            self.edit_fields[col] = field
            edit_layout.addRow(col, field)
        edit_box = QGroupBox("Editable Fields")
        edit_box.setLayout(edit_layout)
        tool_layout.addWidget(edit_box)

        self.toggle_formatter = QCheckBox("Enable Smart Formatting")
        self.toggle_formatter.setChecked(True)
        self.toggle_formatter.stateChanged.connect(self.toggle_formatting)
        tool_layout.addWidget(self.toggle_formatter)

        content_split.addLayout(tool_layout, stretch=1)
        layout.addLayout(content_split)

        self.prev_btn = QPushButton(f"⬆ Previous ({cmd_key_text}[)")
        self.prev_btn.clicked.connect(self.prev_row)
        self.next_btn = QPushButton(f"Next ⬇ ({cmd_key_text}])")
        self.next_btn.clicked.connect(self.next_row)

        self.go_to_input = QLineEdit()
#        self.go_to_input.setPlaceholderText("Row #")
#        self.go_to_btn = QPushButton(f"Go to Row ({cmd_key_text}G)")
        self.go_to_input.setPlaceholderText(f"Row # ({cmd_key_text}G)")
        self.go_to_btn = QPushButton(f"Go to Row")
        self.go_to_btn.clicked.connect(lambda: self.go_to_row())

        self.exit_btn = QPushButton("Exit (Esc)")
        self.exit_btn.clicked.connect(self.exit_app)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.go_to_input)
        nav_layout.addWidget(self.go_to_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.exit_btn)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

        # Set keyboard shortcuts

        for cmd_key in cmd_keys:
            QShortcut(QKeySequence(cmd_key+'['), self, self.prev_btn.click) 
            QShortcut(QKeySequence(cmd_key+']'), self, self.next_btn.click)  
            QShortcut(QKeySequence(cmd_key+'G'), self, self.go_to_input.setFocus)
        self.prev_btn.setToolTip(f'Previous ({cmd_key_text}[)')
        self.next_btn.setToolTip(f'Next ({cmd_key_text}])')
        self.go_to_btn.setToolTip(f'Go To Row ({cmd_key_text}G)')
        self.go_to_input.returnPressed.connect(self.go_to_btn.click)
 
        QShortcut(QKeySequence('Escape'), self, self.exit_btn.click) 

    def extract_sentences(self, report):
        report_idx = 0
        lines = re.split(r'(?<=[:.!?])\s+', report)
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:  continue
            cleaned.append(line)

        n = len(cleaned)
        sentences = [
            {
                'text': line,
                'report_index': report_idx,
                'sentence_index': i,
                'num_sentences_in_report': n,
            }
            for i,line in enumerate(cleaned)
        ]
           
        return sentences

    def format_text(self, text):
        if not self.use_formatter:
            return text

#        sentences = re.split(r'(?<=[:.!?])\s+', text.strip())
        sentences = self.extract_sentences(text)
        html_lines = []

        for sentence in sentences:
            try:
                label = self.formatter_model.predict([sentence])[0]
            except Exception as e:
                print(f'WARNING: error encountered during formatting prediction: \n{e}')
                label = None

            sentence_text = sentence['text']
            if label == 0:
                html_lines.append(f"<br><br><b>{sentence_text}</b>")
#            elif label == 1:
#                html_lines.append(f"<br><br>{sentence_text}")
#            elif label == 2:
#                html_lines.append(f"<br><br>{sentence_text}")
            else:
                html_lines.append(sentence_text)

        return " ".join(html_lines)

    def apply_highlights(self, html):
        text_edit = QTextEdit()
        text_edit.setHtml(html)
        text = text_edit.toPlainText()

        color_map = {
            "yellow": QColor(255, 255, 0, 100),
            "blue": QColor(0, 0, 255, 80),
            "green": QColor(0, 255, 0, 80),
            "red": QColor(255, 0, 0, 80),
            "purple": QColor(128, 0, 128, 80)
        }

        for color, input_box in self.highlight_inputs.items():
            input_box.setStyleSheet('')
            pat = input_box.text()
            if not pat:  continue
            try:
                pat_re = re.compile(pat, re.IGNORECASE)
                fmt = QTextCharFormat()
                fmt.setBackground(color_map[color])
                for match in re.finditer(pat_re, text):
                    start, end = match.start(), match.end()
                    cursor = text_edit.textCursor()
                    cursor.setPosition(start)
                    cursor.setPosition(end, QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(fmt)
            except re.error as e:
                input_box.setStyleSheet('background-color: rgba(255,0,0,.3);')

##        # integrate this code into above
##        bold_fmt = QTextCharFormat()
##        bold_fmt.setFontWeight(QFont.Bold)
##        bold_fmt.setFontUnderline(True)
##        bold_fmt.setForeground(QColor("#C71585"))
##        pat = self.bold_input.text()
##        self.bold_input.setStyleSheet('')
##        if pat:
##            try:
##                pat_re = re.compile(pat, re.IGNORECASE)
##                for match in re.finditer(pat, text):
##                    start, end = match.start(), match.end()
##                    cursor = text_edit.textCursor()
##                    cursor.setPosition(start)
##                    cursor.setPosition(end, QTextCursor.KeepAnchor)
##                    cursor.mergeCharFormat(fmt)
##            except re.error as e:
##                self.bold_input.setStyleSheet('background-color: rgba(255,0,0,.3);')

        return text_edit.toHtml()

    def refresh_highlights(self):
        self.load_row()

    def toggle_formatting(self):
        self.use_formatter = self.toggle_formatter.isChecked()
        self.load_row()

    def load_row(self):
        row = self.df.iloc[self.current_index]
        id_parts = [f"Row {self.current_index + 1}"]
        for col in self.identifier_columns:
            id_parts.append(f"{col}: {row[col]}")
        self.id_label.setText(" | ".join(id_parts))

        for i, col in enumerate(self.display_columns):
            raw_text = str(row[col]) if pd.notna(row[col]) else ""
            formatted = self.format_text(raw_text)
            highlighted = self.apply_highlights(formatted)
            self.display_texts[i][1].setHtml(highlighted)

        for col in self.editable_columns:
            val = row[col] if pd.notna(row[col]) else ""
            self.edit_fields[col].setText(str(val))

    def save_row(self):
        for col, field in self.edit_fields.items():
            self.df.at[self.current_index, col] = field.text()
        self.df.to_excel(self.output_file, index=False)

#    def search_row(self):
#        query = self.search_input.text().strip().lower()
#
#        matches = []
#        self.row_map.clear()
#
#        for i, row in self.df.iterrows():
#            id_text = " | ".join(str(row[col]) for col in self.identifier_columns)
#            full_text = f"{i+1}: {id_text}"
#            if query in full_text.lower():
#                matches.append(full_text)
#                self.row_map[full_text.lower()] = i
#
#        self.completer_model.setStringList(matches)
#
#        # Auto-select if exactly one match
#        if len(matches) == 1:
#            self.on_completer_selected(matches[0])

    def go_to_row(self, row_number=None):
        try:
            target = row_number if row_number is not None else int(self.go_to_input.text()) - 1
            target = max(min(target, len(self.df)-1), 0)
            self.save_row()
            self.current_index = target
            self.load_row()
        except:
            QMessageBox.warning(self, "Invalid Input", "Enter a valid row number.")


    def next_row(self):
        self.save_row()
        if self.current_index < len(self.df) - 1:
            self.current_index += 1
            self.load_row()

    def prev_row(self):
        self.save_row()
        if self.current_index > 0:
            self.current_index -= 1
            self.load_row()

    def exit_app(self):
        self.save_row()
        self.close()
