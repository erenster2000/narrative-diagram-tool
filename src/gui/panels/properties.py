from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTextEdit, QSpinBox, QColorDialog,
                             QPushButton, QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from core.commands import UpdateElementCommand


class PropertiesPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Özellikler", parent)
        self.main_window = parent
        self.current_element = None
        self._updating = False

        # Ana widget ve layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # Element seçili değilken gösterilecek label
        self.no_selection_label = QLabel("Element seçili değil")
        self.no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.no_selection_label)

        # Element özellikleri widget'ı
        self.properties_widget = QWidget()
        self.properties_layout = QFormLayout(self.properties_widget)

        # Başlık alanı
        self.title_edit = QLineEdit()
        self.title_edit.textChanged.connect(self._on_title_changed)
        self.properties_layout.addRow("Başlık:", self.title_edit)

        # İçerik alanı
        self.content_edit = QTextEdit()
        self.content_edit.textChanged.connect(self._on_content_changed)
        self.content_edit.setMinimumHeight(100)
        self.properties_layout.addRow("İçerik:", self.content_edit)

        # Boyut grubu
        size_group = QGroupBox("Boyut")
        size_layout = QHBoxLayout()

        # Genişlik
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 500)
        self.width_spin.setSingleStep(10)
        self.width_spin.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(QLabel("Genişlik:"))
        size_layout.addWidget(self.width_spin)

        # Yükseklik
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 500)
        self.height_spin.setSingleStep(10)
        self.height_spin.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(QLabel("Yükseklik:"))
        size_layout.addWidget(self.height_spin)

        size_group.setLayout(size_layout)
        self.properties_layout.addRow(size_group)

        # Renk seçici
        color_group = QGroupBox("Renk")
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setMinimumHeight(30)
        self.color_button.setStyleSheet("background-color: #F0F0F0;")
        self.color_button.clicked.connect(self._on_color_button_clicked)
        color_layout.addWidget(self.color_button)
        color_group.setLayout(color_layout)
        self.properties_layout.addRow(color_group)

        # Properties widget'ı layout'a ekle
        self.layout.addWidget(self.properties_widget)
        self.layout.addStretch()

        # Başlangıçta properties widget'ı gizle
        self.properties_widget.hide()

        # Ana widget'ı ayarla
        self.setWidget(self.main_widget)

    def set_element(self, element_item):
        """Seçili elementi güvenli bir şekilde ayarla"""
        try:
            self._updating = True

            # Element kontrolü
            if element_item is None:
                self.current_element = None
                self.properties_widget.hide()
                self.no_selection_label.show()
                return

            # Scene kontrolü
            if not element_item.scene():
                self.current_element = None
                self.properties_widget.hide()
                self.no_selection_label.show()
                return

            print(f"Setting element: {element_item.element.title}")
            self.current_element = element_item
            self.no_selection_label.hide()
            self.properties_widget.show()

            # Form alanlarını güncelle
            if hasattr(element_item.element, 'title'):
                self.title_edit.setText(element_item.element.title)
            if hasattr(element_item.element, 'content'):
                self.content_edit.setText(element_item.element.content)

            # Boyut değerlerini güncelle
            rect = element_item.rect()
            self.width_spin.setValue(int(rect.width()))
            self.height_spin.setValue(int(rect.height()))

            # Renk butonunu güncelle
            color = element_item.brush().color()
            self.color_button.setStyleSheet(f"background-color: {color.name()};")

        except Exception as e:
            print(f"Error in set_element: {str(e)}")
            self.current_element = None
            self.properties_widget.hide()
            self.no_selection_label.show()
        finally:
            self._updating = False

    def _on_title_changed(self):
        if not self._updating and self.current_element:
            try:
                old_title = self.current_element.element.title
                new_title = self.title_edit.text()
                if old_title != new_title:
                    command = UpdateElementCommand(
                        self.current_element,
                        "title",
                        old_title,
                        new_title
                    )
                    self.main_window.command_stack.execute(command)
            except Exception as e:
                print(f"Error updating title: {str(e)}")

    def _on_content_changed(self):
        if not self._updating and self.current_element:
            try:
                old_content = self.current_element.element.content
                new_content = self.content_edit.toPlainText()
                if old_content != new_content:
                    command = UpdateElementCommand(
                        self.current_element,
                        "content",
                        old_content,
                        new_content
                    )
                    self.main_window.command_stack.execute(command)
            except Exception as e:
                print(f"Error updating content: {str(e)}")

    def _on_size_changed(self):
        if not self._updating and self.current_element:
            try:
                old_size = {
                    'width': self.current_element.rect().width(),
                    'height': self.current_element.rect().height()
                }
                new_size = {
                    'width': self.width_spin.value(),
                    'height': self.height_spin.value()
                }
                if old_size != new_size:
                    command = UpdateElementCommand(
                        self.current_element,
                        "size",
                        old_size,
                        new_size
                    )
                    self.main_window.command_stack.execute(command)
            except Exception as e:
                print(f"Error updating size: {str(e)}")

    def _on_color_button_clicked(self):
        if self.current_element:
            try:
                old_brush = self.current_element.brush()
                color = QColorDialog.getColor(old_brush.color(), self)
                if color.isValid():
                    new_brush = QBrush(color)
                    command = UpdateElementCommand(
                        self.current_element,
                        "color",
                        old_brush,
                        new_brush
                    )
                    self.main_window.command_stack.execute(command)
            except Exception as e:
                print(f"Error updating color: {str(e)}")