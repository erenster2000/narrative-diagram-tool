from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.core.element import Element
from PyQt6.QtCore import QPointF


from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.core.element import Element
from PyQt6.QtCore import QPointF

from src.gui.board_view import ConnectionGraphicsItem, ElementGraphicsItem

class Command(ABC):
    """Temel komut sınıfı"""
    
    @abstractmethod
    def execute(self):
        """Komutu uygula"""
        pass
        
    @abstractmethod
    def undo(self):
        """Komutu geri al"""
        pass

class AddElementCommand(Command):
    """Element ekleme komutu"""
    def __init__(self, board_scene, element, pos):
        self.scene = board_scene
        self.element = element
        self.pos = pos
        self.element_item = None
        
    def execute(self):
        from src.gui.board_view import ElementGraphicsItem
        self.element_item = ElementGraphicsItem(self.element)
        self.element_item.setPos(self.pos)
        self.scene.addItem(self.element_item)
        
        # Board'a elementi ekle
        view = self.scene.views()[0]
        if view.main_window and view.main_window.current_board:
            view.main_window.current_board.elements[self.element.id] = self.element
            view.main_window.project_explorer.refresh_elements(view.main_window.current_board)
        
    def undo(self):
        if self.element_item:
            # Board'dan elementi kaldır
            view = self.scene.views()[0]
            if view.main_window and view.main_window.current_board:
                if self.element.id in view.main_window.current_board.elements:
                    del view.main_window.current_board.elements[self.element.id]
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)
            # Sahneden elementi kaldır
            self.scene.removeItem(self.element_item)

class DeleteElementCommand(Command):
    """Element silme komutu"""
    def __init__(self, board_scene, element_item):
        self.scene = board_scene
        self.element_item = element_item
        self.element = element_item.element
        self.pos = element_item.pos()
        self.connections = []
        self.was_executed = False
        print(f"Created delete command for element {self.element.title}")

    def execute(self):
        """Elementi ve bağlantılarını sil"""
        try:
            print(f"Executing delete for element {self.element.title}")
            # Bağlantıları kaydet ve sil
            if self.scene and not self.was_executed:  # Sadece ilk kez yürütülüyorsa bağlantıları kaydet
                for item in self.scene.items():
                    if isinstance(item, ConnectionGraphicsItem):
                        if item.source_item == self.element_item or item.target_item == self.element_item:
                            self.connections.append({
                                'source_id': item.source_item.element.id,
                                'target_id': item.target_item.element.id,
                                'item': item
                            })
                            self.scene.removeItem(item)

            # Board'dan elementi sil
            view = self.scene.views()[0]
            if view.main_window and view.main_window.current_board:
                if self.element.id in view.main_window.current_board.elements:
                    del view.main_window.current_board.elements[self.element.id]
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)

            # Sahneden elementi sil
            if self.scene:
                self.scene.removeItem(self.element_item)
            
            self.was_executed = True
            print(f"Successfully deleted element {self.element.title}")
        except Exception as e:
            print(f"Error in DeleteElementCommand execute: {str(e)}")
            import traceback
            traceback.print_exc()

    def undo(self):
        """Elementi ve bağlantılarını geri yükle"""
        try:
            print(f"Undoing delete for element {self.element.title}")
            # Elementi geri ekle
            if self.scene:
                self.scene.addItem(self.element_item)
                self.element_item.setPos(self.pos)

            # Board'a elementi geri ekle
            view = self.scene.views()[0]
            if view.main_window and view.main_window.current_board:
                view.main_window.current_board.elements[self.element.id] = self.element
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)

            # Bağlantıları geri oluştur
            for conn_data in self.connections:
                source_item = None
                target_item = None
                for item in self.scene.items():
                    if isinstance(item, ElementGraphicsItem):
                        if item.element.id == conn_data['source_id']:
                            source_item = item
                        elif item.element.id == conn_data['target_id']:
                            target_item = item
                
                if source_item and target_item:
                    conn = ConnectionGraphicsItem(source_item, target_item)
                    self.scene.addItem(conn)
            
            self.was_executed = False
            print(f"Successfully restored element {self.element.title}")
        except Exception as e:
            print(f"Error in DeleteElementCommand undo: {str(e)}")
            import traceback
            traceback.print_exc()
        """Elementi ve bağlantılarını geri yükle"""
        try:
            print(f"Undoing delete for element: {self.element.title}")  # Debug için
            
            # Elementi geri ekle
            if self.scene:
                self.scene.addItem(self.element_item)
                self.element_item.setPos(self.pos)
                print("Restored element to scene")  # Debug için

            # Bağlantıları geri ekle
            for conn in self.connections:
                if self.scene:
                    self.scene.addItem(conn['connection'])
                    print("Restored connection")  # Debug için

            # Board'a elementi geri ekle
            view = self.scene.views()[0]
            if view.main_window and view.main_window.current_board:
                view.main_window.current_board.elements[self.element.id] = self.element
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)
                print("Restored to board data")  # Debug için

        except Exception as e:
            print(f"Error in DeleteElementCommand undo: {str(e)}")
            import traceback
            traceback.print_exc()

class MoveElementCommand(Command):
    """Element taşıma komutu"""
    def __init__(self, element_item, old_pos, new_pos):
        self.element_item = element_item
        self.old_pos = old_pos
        self.new_pos = new_pos
        print(f"Created move command from {old_pos} to {new_pos}")
        
    def execute(self):
        try:
            self.element_item.setPos(self.new_pos)
            print(f"Moved element to {self.new_pos}")
        except Exception as e:
            print(f"Error in MoveElementCommand execute: {str(e)}")
        
    def undo(self):
        try:
            self.element_item.setPos(self.old_pos)
            print(f"Moved element back to {self.old_pos}")
        except Exception as e:
            print(f"Error in MoveElementCommand undo: {str(e)}")

class UpdateElementCommand(Command):
    """Element özelliklerini güncelleme komutu"""
    def __init__(self, element_item, property_name: str, old_value: Any, new_value: Any):
        self.element_item = element_item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        
    def execute(self):
        self._set_property(self.new_value)
        
    def undo(self):
        self._set_property(self.old_value)
        
    def _set_property(self, value):
        if self.property_name == "title":
            self.element_item.element.title = value
            self.element_item.update()
            # Sol paneli güncelle
            view = self.element_item.scene().views()[0]
            if view.main_window and view.main_window.current_board:
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)
        elif self.property_name == "content":
            self.element_item.element.content = value
            self.element_item.update()
        elif self.property_name == "size":
            self.element_item.setRect(0, 0, value['width'], value['height'])
            self.element_item.element.size = value
        elif self.property_name == "color":
            self.element_item.setBrush(value)
    """Element taşıma komutu"""
    def __init__(self, element_item, old_pos, new_pos):
        self.element_item = element_item
        self.old_pos = old_pos
        self.new_pos = new_pos
        print(f"Created move command from {old_pos} to {new_pos}")
        
    def execute(self):
        try:
            self.element_item.setPos(self.new_pos)
            print(f"Moved element to {self.new_pos}")
        except Exception as e:
            print(f"Error in MoveElementCommand execute: {str(e)}")
        
    def undo(self):
        try:
            self.element_item.setPos(self.old_pos)
            print(f"Moved element back to {self.old_pos}")
        except Exception as e:
            print(f"Error in MoveElementCommand undo: {str(e)}")
    """Element özelliklerini güncelleme komutu"""

    def __init__(self, element_item, property_name: str, old_value: Any, new_value: Any):
        self.element_item = element_item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value

    def execute(self):
        self._set_property(self.new_value)

    def undo(self):
        self._set_property(self.old_value)

    def _set_property(self, value):
        if self.property_name == "title":
            self.element_item.element.title = value
            self.element_item.update()
            # Sol paneli güncelle
            view = self.element_item.scene().views()[0]
            if view.main_window and view.main_window.current_board:
                view.main_window.project_explorer.refresh_elements(view.main_window.current_board)
        elif self.property_name == "content":
            self.element_item.element.content = value
            self.element_item.update()
        elif self.property_name == "size":
            self.element_item.setRect(0, 0, value['width'], value['height'])
            self.element_item.element.size = value
        elif self.property_name == "color":
            self.element_item.setBrush(value)

class CommandStack:
    """Komut yığını - Geri alma/ileri alma işlemlerini yönetir"""

    def __init__(self):
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []

    def execute(self, command: Command):
        """Komutu uygula ve undo stack'e ekle"""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Yeni komut eklenince redo stack'i temizle

    def undo(self):
        """Son komutu geri al"""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        """Son geri alınan komutu tekrar uygula"""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)

    def can_undo(self) -> bool:
        """Geri alınabilecek komut var mı?"""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """İleri alınabilecek komut var mı?"""
        return len(self.redo_stack) > 0