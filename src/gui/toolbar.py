from PyQt6.QtWidgets import (QToolBar, QLabel, QPushButton, QSpinBox, 
                           QDoubleSpinBox, QWidget, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

class EditorToolBar(QToolBar):
    """Editör için toolbar"""
    # Özel sinyaller
    zoomChanged = pyqtSignal(float)  # Zoom değiştiğinde sinyal gönder
    gridToggled = pyqtSignal(bool)   # Grid göster/gizle değiştiğinde sinyal gönder
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)  # Toolbar'ın yerini sabitle
        self.init_ui()
        
    def init_ui(self):
        # Zoom kontrolleri
        self.addAction(QIcon(), "Zoom Out", self.zoom_out).setShortcut("Ctrl+-")
        
        # Zoom seviyesi göstergesi (%)
        self.zoom_level = QSpinBox()
        self.zoom_level.setRange(25, 400)  # 25% ile 400% arası zoom
        self.zoom_level.setSuffix("%")
        self.zoom_level.setValue(100)
        self.zoom_level.setFixedWidth(70)
        self.zoom_level.valueChanged.connect(self.on_zoom_value_changed)
        self.addWidget(self.zoom_level)
        
        self.addAction(QIcon(), "Zoom In", self.zoom_in).setShortcut("Ctrl+=")
        
        self.addSeparator()
        
        # Tümünü göster butonu
        self.addAction(QIcon(), "Tümünü Göster", self.fit_to_view).setShortcut("Ctrl+0")
        
        self.addSeparator()
        
        # Grid kontrolü
        self.grid_action = self.addAction(QIcon(), "Grid")
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.on_grid_toggled)
        
        # Sağa boşluk ekle
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(spacer)
        
    def zoom_in(self):
        current = self.zoom_level.value()
        new_zoom = min(current + 25, 400)
        self.zoom_level.setValue(new_zoom)
        self.zoomChanged.emit(new_zoom / 100.0)  # Yüzdeyi decimal'e çevirip sinyal gönder
        print(f"Zoom in: {new_zoom}%")  # Debug için
        current = self.zoom_level.value()
        new_zoom = min(current + 25, 400)  # 25% artır, max 400%
        self.zoom_level.setValue(new_zoom)
        # Zoom sinyali gönder
        self.zoomChanged.emit(new_zoom / 100.0)  # Yüzdeyi ondalık sayıya çevir
        current = self.zoom_level.value()
        new_zoom = min(current + 25, 400)  # 25% artır, max 400%
        self.zoom_level.setValue(new_zoom)
        
    def zoom_out(self):
        current = self.zoom_level.value()
        new_zoom = max(current - 25, 25)
        self.zoom_level.setValue(new_zoom)
        self.zoomChanged.emit(new_zoom / 100.0)  # Yüzdeyi decimal'e çevirip sinyal gönder
        print(f"Zoom out: {new_zoom}%")  # Debug için

        current = self.zoom_level.value()
        new_zoom = max(current - 25, 25)  # 25% azalt, min 25%
        self.zoom_level.setValue(new_zoom)
        # Zoom sinyali gönder
        self.zoomChanged.emit(new_zoom / 100.0)  # Yüzdeyi ondalık sayıya çevir
        current = self.zoom_level.value()
        new_zoom = max(current - 25, 25)  # 25% azalt, min 25%
        self.zoom_level.setValue(new_zoom)
        
    def on_zoom_value_changed(self, value):
        zoom_factor = value / 100.0
        self.zoomChanged.emit(zoom_factor)
        print(f"Zoom value changed: {value}%")  # Debug için
        zoom_factor = value / 100.0
        self.zoomChanged.emit(zoom_factor)
        
    def on_grid_toggled(self, checked):
        self.gridToggled.emit(checked)
        print(f"Grid toggled: {checked}")  # Debug için
        self.gridToggled.emit(checked)
        
    def fit_to_view(self):
        if self.parent():
            self.parent().board_view.fit_to_view()
         
    def set_zoom_level(self, zoom_factor):
        """Dışarıdan zoom seviyesi güncellemesi"""
        self.zoom_level.setValue(int(zoom_factor * 100))