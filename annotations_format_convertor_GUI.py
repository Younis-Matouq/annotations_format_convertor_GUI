import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
                             QComboBox, QLineEdit, QSpinBox, QFileDialog)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QTimer

from src import seg_convert_json_to_txt, seg_convert_txt_to_json, rect_convert_json_to_txt, rect_convert_txt_to_json

class ScriptRunnerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.setWindowTitle("Annotation Format Converter")  # Set window title
        self.resize(600, 400)  # Resize window to 400x400 pixels

    def init_ui(self):
        layout = QVBoxLayout()

        # Title for the dropdown menu
        layout.addWidget(QLabel("Choose Format to Convert to"))

        # Script selector
        self.script_selector = QComboBox()
        self.script_selector.addItems(["seg_convert_json_to_txt", "seg_convert_txt_to_json","rect_convert_json_to_txt","rect_convert_txt_to_json"])
        self.script_selector.currentIndexChanged.connect(self.on_script_change)
        layout.addWidget(self.script_selector)
        
        # Smoothness selector
        self.smoothness_selector = QComboBox()
        self.smoothness_selector.addItems(["No Smoothness", "Fully Smoothed", "Simple Smoothness"])
        layout.addWidget(self.smoothness_selector)

        # Common inputs for all scripts
        self.input_dir = QLineEdit(self)
        self.input_dir.setPlaceholderText("Input Directory")
        self.input_dir_btn = QPushButton("Browse", self)
        self.input_dir_btn.clicked.connect(self.browse_directory)
        layout.addWidget(QLabel("Input Directory:"))
        layout.addWidget(self.input_dir)
        layout.addWidget(self.input_dir_btn)

        self.output_dir = QLineEdit(self)
        self.output_dir.setPlaceholderText("Output Directory")
        self.output_dir_btn = QPushButton("Browse", self)
        self.output_dir_btn.clicked.connect(self.browse_directory)
        layout.addWidget(QLabel("Output Directory:"))
        layout.addWidget(self.output_dir)
        layout.addWidget(self.output_dir_btn)

        self.class_dict_path = QLineEdit(self)
        self.class_dict_path.setPlaceholderText("Class Dict File Path")
        self.class_dict_btn = QPushButton("Browse", self)
        self.class_dict_btn.clicked.connect(self.browse_file)
        layout.addWidget(QLabel("Class Dict File Path:"))
        layout.addWidget(self.class_dict_path)
        layout.addWidget(self.class_dict_btn)

        # Additional inputs for img dimensions
        self.img_width_spin = QSpinBox(self)
        self.img_width_spin.setRange(0, 10000)
        layout.addWidget(QLabel("Image Width:"))
        layout.addWidget(self.img_width_spin)

        self.img_height_spin = QSpinBox(self)
        self.img_height_spin.setRange(0, 10000)
        layout.addWidget(QLabel("Image Height:"))
        layout.addWidget(self.img_height_spin)

        # Run button
        self.run_button = QPushButton('Run', self)
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button)

        self.result_label = QLabel("Status: Awaiting Input")
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        self.on_script_change(0)  # Initialize UI state

    def on_script_change(self, index):
        if index == 0 or index == 2:
            self.img_width_spin.setVisible(False)
            self.img_height_spin.setVisible(False)
            self.smoothness_selector.setVisible(False)
        else:
            self.img_width_spin.setVisible(True)
            self.img_height_spin.setVisible(True)
            self.smoothness_selector.setVisible(False)
            if index == 1:  # seg_convert_txt_to_json
                self.smoothness_selector.setVisible(True)
            # else:
            #     self.smoothness_selector.setVisible(False)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.class_dict_path.setText(file_path)

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            # Determine which button triggered this function
            sender = self.sender()
            if sender == self.input_dir_btn:
                self.input_dir.setText(dir_path)
            else:
                self.output_dir.setText(dir_path)

    def run_script(self):
        input_dir_path = self.input_dir.text()
        output_dir_path = self.output_dir.text()
        class_dict_path = self.class_dict_path.text()

        # Validation checks
        if not (input_dir_path and output_dir_path and class_dict_path):
            self.result_label.setText("Please fill all the required fields!")
            return

        choice = self.script_selector.currentIndex()
        if choice == 0:  # seg_convert_json_to_txt
            seg_convert_json_to_txt.json_seg_to_txt_annotations(input_dir_path, output_dir_path, class_dict_path)

        elif choice == 1:  # seg_convert_txt_to_json
            img_width = self.img_width_spin.value()
            img_height = self.img_height_spin.value()
            smoothness_degree = self.smoothness_selector.currentText()
            seg_convert_txt_to_json.yolo_to_json_polygon_writer(input_dir_path, output_dir_path, class_dict_path,img_width, img_height,smoothness_degree)
        elif choice == 2: #rect_convert_json_to_txt
             rect_convert_json_to_txt.json_to_yolo_rect(input_dir_path, output_dir_path, class_dict_path)  # Using the same args as script1
        else: #rect_convert_txt_to_json
            img_width = self.img_width_spin.value()
            img_height = self.img_height_spin.value()
            rect_convert_txt_to_json.convert_txt_to_labelme(input_dir_path, output_dir_path, class_dict_path, img_width, img_height)

        self.result_label.setText("Script executed successfully!")
        QTimer.singleShot(15000, lambda: self.result_label.setText("Status: Awaiting Input"))

    def closeEvent(self, event):
        # Any cleanup or shutdown operations you want can be added here
        QCoreApplication.quit()  # Ensure the event loop is closed properly 
        event.accept()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Increase the size of all text in the application, Set font color of all QLabel widgets to red  
    app.setStyleSheet("""
    QWidget { font-size: 16px; }
    QLabel { color: red; }
""")
    
    window = ScriptRunnerApp()
    window.show()
    sys.exit(app.exec_())
