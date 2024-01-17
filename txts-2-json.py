import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QCheckBox, QListWidget, QFrame
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from docx import Document
from PyPDF2 import PdfReader
import textract

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip() != '']

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        return [page.extract_text() for page in reader.pages]

def extract_text_from_doc(doc_path):
    return textract.process(doc_path).decode('utf-8')

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r') as file:
        return file.read()

def convert_to_json(text_list):
    json_data = {"content": []}
    for text in text_list:
        json_data["content"].append({"paragraph": text})
    return json_data

class FileFormatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Format Automation")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Dark Mode Checkbox
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.toggled.connect(self.toggle_dark_mode)
        self.layout.addWidget(self.dark_mode_checkbox)

        # File Selection
        self.input_label = QLabel("Select input files:")
        self.layout.addWidget(self.input_label)

        self.input_files_button = QPushButton("Browse")
        self.input_files_button.clicked.connect(self.get_input_files)
        self.layout.addWidget(self.input_files_button)

        self.file_list_frame = QFrame()
        self.file_list_frame.setLayout(QVBoxLayout())

        self.file_list = QListWidget()
        self.file_list_frame.layout().addWidget(self.file_list)
                # ... [Previous code for UI setup]

        self.output_label = QLabel("Output files will be saved in the same directory as input files.")
        self.layout.addWidget(self.output_label)

        # Editable Text Areas for DOCX and JSON
        self.docx_text_edit = QTextEdit()
        self.layout.addWidget(self.docx_text_edit)

        self.json_text_edit = QTextEdit()
        self.layout.addWidget(self.json_text_edit)

        # Save Buttons for Edits
        self.save_docx_button = QPushButton("Save DOCX Edits")
        self.save_docx_button.clicked.connect(self.save_docx_edits)
        self.layout.addWidget(self.save_docx_button)

        self.save_json_button = QPushButton("Save JSON Edits")
        self.save_json_button.clicked.connect(self.save_json_edits)
        self.layout.addWidget(self.save_json_button)

        self.format_button = QPushButton("Format Files")
        self.format_button.clicked.connect(self.format_files)
        self.layout.addWidget(self.format_button)

        self.input_files = []

    def toggle_dark_mode(self):
        palette = QPalette()
        if self.dark_mode_checkbox.isChecked():
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            QApplication.setPalette(palette)
        else:
            QApplication.setPalette(QApplication.style().standardPalette())

    def get_input_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("Documents (*.docx *.pdf *.doc *.txt)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            self.input_files = file_dialog.selectedFiles()
            self.update_file_list()

    def update_file_list(self):
        self.file_list.clear()
        for file in self.input_files:
            self.file_list.addItem(file)

    def format_files(self):
        for input_file in self.input_files:
            if input_file.endswith('.pdf'):
                text_list = extract_text_from_pdf(input_file)
            elif input_file.endswith('.docx'):
                text_list = extract_text_from_docx(input_file)
            elif input_file.endswith('.doc'):
                text_list = [extract_text_from_doc(input_file)]
            elif input_file.endswith('.txt'):
                text_list = [extract_text_from_txt(input_file)]
            else:
                continue  # Skip unsupported files

            json_data = convert_to_json(text_list)
            output_file = input_file.rsplit('.', 1)[0] + ".json"

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4)

            self.update_text_editors(text_list, json_data)

    def update_text_editors(self, text_list, json_data):
        self.docx_text_edit.setPlainText("\n\n".join(text_list))
        self.json_text_edit.setPlainText(json.dumps(json_data, indent=4))

    def save_docx_edits(self):
        # Logic to save edits back to DOCX (if applicable)
        # This can be complex as it involves writing back to a DOCX format.
        # You might need a library like python-docx for creating DOCX files.
        pass

    def save_json_edits(self):
        # Logic to save edits back to the JSON file
        current_file = self.file_list.currentItem().text() if self.file_list.currentItem() else None
        if current_file:
            output_file = current_file.rsplit('.', 1)[0] + ".json"
            try:
                with open(output_file, 'w', encoding='utf-8') as json_file:
                    json_data = json.loads(self.json_text_edit.toPlainText())
                    json.dump(json_data, json_file, indent=4)
            except json.JSONDecodeError:
                # Handle JSON format errors
                pass  # You may want to show an error message to the user

def main():
    app = QApplication(sys.argv)
    ex = FileFormatApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

