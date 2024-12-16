from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt

class BoardDialog(QDialog):
    def __init__(self, parent=None, board=None):
        super().__init__(parent)
        self.board = board  # Eğer varolan bir board düzenleniyorsa
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Board Ekle/Düzenle")
        layout = QVBoxLayout(self)
        
        # Board adı
        name_layout = QHBoxLayout()
        name_label = QLabel("Board Adı:")
        self.name_edit = QLineEdit()
        if self.board:
            self.name_edit.setText(self.board.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Root board checkbox
        self.root_checkbox = QCheckBox("Ana Board")
        if self.board:
            self.root_checkbox.setChecked(self.board.root)
        layout.addWidget(self.root_checkbox)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Tamam")
        self.cancel_button = QPushButton("İptal")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Pencere boyutu
        self.setMinimumWidth(300)

    def get_data(self):
        """Dialog verilerini döndür"""
        return {
            'name': self.name_edit.text(),
            'root': self.root_checkbox.isChecked()
        }