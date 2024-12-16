from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QMenuBar,
                             QStatusBar, QHBoxLayout, QDockWidget, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from .panels.project_explorer import ProjectExplorerPanel
from .panels.properties import PropertiesPanel
from .board_view import BoardView, ElementGraphicsItem
from core.project import Project
from core.board import Board
from core.element import Element
from core.commands import CommandStack
from utils.file_ops import ProjectFileHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Önce değişkenleri tanımla
        self.project = None
        self.current_board = None
        self.board_view = None
        self.project_explorer = None
        self.properties_panel = None
        self.command_stack = CommandStack()

        # UI'ı başlat
        self.init_ui()

        # İlk projeyi oluştur
        self.create_new_project()

    def init_ui(self):
        """Ana pencere arayüzünü başlat"""
        # Pencere başlığı ve boyutu
        self.setWindowTitle('Narrative Tool')
        self.resize(1200, 800)

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Board görünümü
        self.board_view = BoardView(self)
        self.layout.addWidget(self.board_view)

        # Sol panel
        self.project_explorer = ProjectExplorerPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.project_explorer)

        # Sağ panel
        self.properties_panel = PropertiesPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_panel)

        # Menü çubuğu
        self.create_menu_bar()

        # Durum çubuğu
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Hazır')

    def create_menu_bar(self):
        """Menü çubuğunu oluştur"""
        menubar = self.menuBar()

        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')

        new_project_action = QAction('Yeni Proje', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.triggered.connect(self.create_new_project)
        file_menu.addAction(new_project_action)

        open_action = QAction('Aç', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_project)
        file_menu.addAction(open_action)

        save_action = QAction('Kaydet', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction('Farklı Kaydet', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(lambda: self.save_project(True))
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction('Çıkış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Düzenle menüsü
        edit_menu = menubar.addMenu('Düzenle')

        # Geri Al
        undo_action = QAction('Geri Al', self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)  # Ctrl+Z
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        # İleri Al
        redo_action = QAction('İleri Al', self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)  # Ctrl+Y
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Element Ekle
        add_element_action = QAction('Element Ekle', self)
        add_element_action.setShortcut('Ctrl+E')
        add_element_action.triggered.connect(self.add_element)
        edit_menu.addAction(add_element_action)

        # Görünüm menüsü
        view_menu = menubar.addMenu('Görünüm')
        view_menu.addAction('Yakınlaştır')
        view_menu.addAction('Uzaklaştır')

    def create_new_project(self):
        """Yeni proje oluştur"""
        try:
            print("Creating new project...")
            self.project = Project("Yeni Proje")
            self.current_board = Board("Ana Board", is_root=True)
            self.project.add_board(self.current_board)

            print("Creating new board view...")
            self.board_view = BoardView(self)
            old_widget = self.layout.itemAt(0).widget()
            self.layout.replaceWidget(old_widget, self.board_view)
            old_widget.deleteLater()

            print("New project created successfully")
            self.statusBar.showMessage('Yeni proje oluşturuldu')
            self.project.save_path = None

            self.project_explorer.refresh_boards(self.project)
            self.project_explorer.refresh_elements(self.current_board)
            self.project_explorer.refresh_components(self.project)

            # Komut yığınını temizle
            self.command_stack = CommandStack()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.statusBar.showMessage(f'Yeni proje oluşturma hatası: {str(e)}')

    def add_element(self):
        """Yeni element ekle"""
        if self.current_board:
            element = Element("Yeni Element", "İçerik buraya...")
            pos = self.board_view.mapToScene(self.board_view.rect().center())

            # Element ekleme komutunu oluştur ve çalıştır
            from core.commands import AddElementCommand
            command = AddElementCommand(self.board_view.scene, element, pos)
            self.command_stack.execute(command)

            self.statusBar.showMessage('Yeni element eklendi')

    def save_project(self, save_as=False):
        if not self.project:
            return

        if not self.project.save_path or save_as:
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Projeyi Kaydet",
                "",
                "Narrative Tool Projesi (*.ntp);;Tüm Dosyalar (*.*)"
            )
            if not filepath:
                return

            if not filepath.endswith('.ntp'):
                filepath += '.ntp'

            self.project.save_path = filepath

        try:
            # Tüm elementlerin pozisyonlarını kaydet
            for item in self.board_view.scene.items():
                if isinstance(item, ElementGraphicsItem):
                    item.element.position = {'x': item.pos().x(), 'y': item.pos().y()}

            ProjectFileHandler.save_project(self.project, self.project.save_path)
            self.statusBar.showMessage(f'Proje kaydedildi: {self.project.save_path}')
        except Exception as e:
            print(f"Save error: {str(e)}")
            self.statusBar.showMessage(f'Kaydetme hatası: {str(e)}')

    def load_project(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Proje Aç",
            "",
            "Narrative Tool Projesi (*.ntp);;Tüm Dosyalar (*.*)"
        )

        if not filepath:
            return

        try:
            # Projeyi yükle
            self.project = ProjectFileHandler.load_project(filepath)
            self.project.save_path = filepath

            # Yeni board view oluştur
            self.board_view = BoardView(self)
            old_widget = self.layout.itemAt(0).widget()
            self.layout.replaceWidget(old_widget, self.board_view)
            old_widget.deleteLater()

            # İlk board'u görüntüle
            if self.project.boards:
                self.current_board = next(iter(self.project.boards.values()))

                # Elementleri ve bağlantıları görsel olarak oluştur
                for element in self.current_board.elements.values():
                    item = ElementGraphicsItem(element)
                    pos_x = element.position.get('x', 0)
                    pos_y = element.position.get('y', 0)
                    item.setPos(pos_x, pos_y)
                    self.board_view.scene.addItem(item)

                # Sol paneli güncelle
                self.project_explorer.refresh_boards(self.project)
                self.project_explorer.refresh_elements(self.current_board)
                self.project_explorer.refresh_components(self.project)

                # Komut yığınını temizle
                self.command_stack = CommandStack()

            self.statusBar.showMessage(f'Proje yüklendi: {filepath}')
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.statusBar.showMessage(f'Yükleme hatası: {str(e)}')

    def switch_to_board(self, board):
        """Board'u değiştir"""
        if board == self.current_board:
            return

        print(f"Switching to board: {board.name}")

        # Mevcut board'daki elementlerin pozisyonlarını kaydet
        if self.current_board:
            for item in self.board_view.scene.items():
                if isinstance(item, ElementGraphicsItem):
                    item.element.position = {'x': item.pos().x(), 'y': item.pos().y()}
                    print(f"Saving position for element {item.element.title}: {item.element.position}")

        # Board'u değiştir
        self.current_board = board

        # Scene'i temizle
        self.board_view.scene.clear()

        # Elementleri yükle
        for element_id, element in board.elements.items():
            item = ElementGraphicsItem(element)
            pos_x = element.position.get('x', 0)
            pos_y = element.position.get('y', 0)
            print(f"Loading element {element.title} at position: {pos_x}, {pos_y}")
            item.setPos(pos_x, pos_y)
            self.board_view.scene.addItem(item)

        # Elementler listesini güncelle
        self.project_explorer.refresh_elements(board)

        # Durum çubuğunu güncelle
        self.statusBar.showMessage(f'Board değiştirildi: {board.name}')

    def undo(self):
        """Son işlemi geri al"""
        self.command_stack.undo()
        self.statusBar.showMessage('Son işlem geri alındı')

    def redo(self):
        """Son geri alınan işlemi tekrarla"""
        self.command_stack.redo()
        self.statusBar.showMessage('İşlem tekrarlandı')