from PyQt6.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem, 
                           QVBoxLayout, QHBoxLayout, QWidget, 
                           QPushButton, QMenu, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from ..dialogs.board_dialog import BoardDialog
from core.board import Board

class ProjectExplorerPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Proje Gezgini", parent)
        self.main_window = parent
        self.init_ui()
        
    def init_ui(self):
        # Ana widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Board işlemleri için butonlar
        board_buttons = QHBoxLayout()
        self.add_board_btn = QPushButton("Board Ekle")
        self.add_board_btn.clicked.connect(self.add_board)
        board_buttons.addWidget(self.add_board_btn)
        layout.addLayout(board_buttons)
        
        # Ağaç widget'ı
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Proje İçeriği")
        self.tree.itemDoubleClicked.connect(self.item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Ana kategorileri oluştur
        self.boards_item = QTreeWidgetItem(["Board'lar"])
        self.elements_item = QTreeWidgetItem(["Elementler"])
        self.components_item = QTreeWidgetItem(["Bileşenler"])
        
        # Ana kategorileri ağaca ekle
        self.tree.addTopLevelItem(self.boards_item)
        self.tree.addTopLevelItem(self.elements_item)
        self.tree.addTopLevelItem(self.components_item)
        
        layout.addWidget(self.tree)
        self.setWidget(widget)
        
    def refresh_boards(self, project):
        """Board'ları güncelle"""
        print("Refreshing boards...")
        self.boards_item.takeChildren()  # Mevcut board'ları temizle
        if project and project.boards:
            for board_id, board in project.boards.items():
                board_item = QTreeWidgetItem([board.name])
                board_item.setData(0, Qt.ItemDataRole.UserRole, board_id)
                self.boards_item.addChild(board_item)
        self.boards_item.setExpanded(True)
        print(f"Added {len(project.boards) if project else 0} boards")

    def refresh_elements(self, current_board):
        """Elementleri güncelle"""
        self.elements_item.takeChildren()  # Mevcut elementleri temizle
        if current_board and current_board.elements:
            for element_id, element in current_board.elements.items():
                element_item = QTreeWidgetItem([element.title])
                element_item.setData(0, Qt.ItemDataRole.UserRole, element_id)
                self.elements_item.addChild(element_item)
        self.elements_item.setExpanded(True)

    def refresh_components(self, project):
        """Componentleri güncelle"""
        print("Refreshing components...")
        self.components_item.takeChildren()  # Mevcut componentleri temizle
        if project and hasattr(project, 'components'):
            for component_id, component in project.components.items():
                component_item = QTreeWidgetItem([component.name])
                component_item.setData(0, Qt.ItemDataRole.UserRole, component_id)
                self.components_item.addChild(component_item)
        self.components_item.setExpanded(True)
        print(f"Added {len(project.components) if hasattr(project, 'components') else 0} components")
        
    def add_board(self):
        """Yeni board ekle"""
        if not self.main_window.project:
            return
            
        dialog = BoardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            board = Board(data['name'], data['root'])
            self.main_window.project.add_board(board)
            self.refresh_boards(self.main_window.project)
            
    def edit_board(self, board_item):
        """Board düzenle"""
        board_id = board_item.data(0, Qt.ItemDataRole.UserRole)
        board = self.main_window.project.boards.get(board_id)
        if board:
            dialog = BoardDialog(self, board)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                board.name = data['name']
                board.root = data['root']
                self.refresh_boards(self.main_window.project)
                
    def delete_board(self, board_item):
        """Board sil"""
        board_id = board_item.data(0, Qt.ItemDataRole.UserRole)
        if board_id in self.main_window.project.boards:
            del self.main_window.project.boards[board_id]
            self.refresh_boards(self.main_window.project)
            
    def show_context_menu(self, position):
        """Sağ tık menüsü göster"""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Board işlemleri
        if item.parent() == self.boards_item:
            edit_action = menu.addAction("Düzenle")
            edit_action.triggered.connect(lambda: self.edit_board(item))
            
            switch_action = menu.addAction("Bu Board'a Geç")
            switch_action.triggered.connect(lambda: self.switch_to_board(item))
            
            menu.addSeparator()
            
            delete_action = menu.addAction("Sil")
            delete_action.triggered.connect(lambda: self.delete_board(item))
            
            menu.exec(self.tree.viewport().mapToGlobal(position))
            
    def switch_to_board(self, board_item):
        """Seçili board'a geç"""
        board_id = board_item.data(0, Qt.ItemDataRole.UserRole)
        board = self.main_window.project.boards.get(board_id)
        if board:
            self.main_window.switch_to_board(board)
            
    def item_double_clicked(self, item, column):
        """Öğeye çift tıklandığında"""
        if item.parent() == self.boards_item:
            self.switch_to_board(item)