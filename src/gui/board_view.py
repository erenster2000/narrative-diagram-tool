from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                           QGraphicsRectItem, QGraphicsLineItem, QMenu, 
                           QGraphicsTextItem, QGraphicsProxyWidget, 
                           QTextEdit, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (QPen, QBrush, QColor, QPainter, QPainterPath,
                        QTransform)  # QTransform burada olmalı


class BoardGraphicsScene(QGraphicsScene):
    """Board için özel scene sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.grid_lines = []  # Grid çizgilerini takip etmek için
        self.grid_visible = True  # Grid görünürlüğünü takip etmek için
        self._draw_grid()

    def set_grid_visible(self, visible):
        """Grid görünürlüğünü ayarla"""
        print(f"Setting grid visibility to: {visible}")  # Debug için
        self.grid_visible = visible
        
        # Tüm grid çizgilerini kaldır
        for line in self.grid_lines:
            self.removeItem(line)
        self.grid_lines.clear()
        
        # Eğer grid görünür olacaksa yeniden çiz
        if visible:
            self._draw_grid()
        self.update()
        """Grid görünürlüğünü ayarla"""
        self.grid_visible = visible
        if visible:
            self._draw_grid()
        else:
            # Grid çizgilerini temizle
            for line in self.grid_lines:
                self.removeItem(line)
            self.grid_lines.clear()
        self.update()

    def _draw_grid(self, size: int = 20):
        """Arka plan ızgarasını çiz"""
        # Önceki grid çizgilerini temizle
        for line in self.grid_lines:
            self.removeItem(line)
        self.grid_lines.clear()
        
        if not self.grid_visible:
            return
            
        pen = QPen(QColor(50, 50, 50, 100))
        pen.setStyle(Qt.PenStyle.DotLine)
        
        # Dikey çizgiler
        for x in range(-5000, 5000, size):
            line = QGraphicsLineItem(x, -5000, x, 5000)
            line.setPen(pen)
            self.addItem(line)
            self.grid_lines.append(line)
            
        # Yatay çizgiler
        for y in range(-5000, 5000, size):
            line = QGraphicsLineItem(-5000, y, 5000, y)
            line.setPen(pen)
            self.addItem(line)
            self.grid_lines.append(line)

class ConnectionGraphicsItem(QGraphicsItem):
    """Elementler arası bağlantı çizgisi"""
    def __init__(self, source_item, target_item):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.arrow_size = 10
        self._pen = QPen(QColor(0, 0, 0), 2)
        
    def boundingRect(self):
        return self.shape().boundingRect()
        
    def shape(self):
        path = QPainterPath()
        
        if self.source_item and self.target_item:
            source_pos = self.source_item.sceneBoundingRect().center()
            target_pos = self.target_item.sceneBoundingRect().center()
            
            # Ana çizgi
            path.moveTo(source_pos)
            path.lineTo(target_pos)
            
        return path
        
    def paint(self, painter, option, widget=None):
        if self.source_item and self.target_item:
            source_pos = self.source_item.sceneBoundingRect().center()
            target_pos = self.target_item.sceneBoundingRect().center()
            
            # Çizgiyi çiz
            painter.setPen(self._pen)
            painter.drawLine(source_pos, target_pos)
            
    def setPen(self, pen):
        self._pen = pen
        self.update()
        
    def pen(self):
        return self._pen

class ElementGraphicsItem(QGraphicsRectItem):
    def __init__(self, element, x=0, y=0, width=200, height=150):
        super().__init__(0, 0, width, height)
        self.element = element
        self.setPos(x, y)
        self.default_width = width
        self.default_height = height
        self.old_pos = None
        
        # Görsel özellikler
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Görünüm ayarları
        self.default_pen = QPen(QColor(100, 100, 100))
        self.default_brush = QBrush(QColor(240, 240, 240))
        self.selected_pen = QPen(QColor(0, 120, 210), 2)
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)
        
        # Editor
        self.editor = None
        self.editor_proxy = None
        
        # Bağlantı oluşturma için değişkenler
        self.is_drawing_connection = False
        self.temp_connection = None
        super().__init__(0, 0, width, height)
        self.element = element
        self.setPos(x, y)
        self.default_width = width
        self.default_height = height
        self.old_pos = None
        
        # Görsel özellikler
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Görünüm ayarları
        self.default_pen = QPen(QColor(100, 100, 100))
        self.default_brush = QBrush(QColor(240, 240, 240))
        self.selected_pen = QPen(QColor(0, 120, 210), 2)
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)
        
        # Editor
        self.editor = None
        self.editor_proxy = None
        
        # Bağlantı oluşturma için değişkenler
        self.is_drawing_connection = False
        self.temp_connection = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = self.pos()
            # Element seçildiğinde properties paneli güncelle
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                if hasattr(view, 'main_window') and view.main_window:
                    if hasattr(view.main_window, 'properties_panel'):
                        view.main_window.properties_panel.set_element(self)
        elif event.button() == Qt.MouseButton.RightButton:
            # Bağlantı çizmeye başla
            self.is_drawing_connection = True
            pos = self.sceneBoundingRect().center()
            scene = self.scene()
            
            # Geçici çizgi oluştur
            self.temp_connection = scene.addLine(
                pos.x(), pos.y(), pos.x(), pos.y(), 
                QPen(QColor(0, 0, 0), 2, Qt.PenStyle.DashLine))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing_connection and self.temp_connection:
            # Geçici bağlantı çizgisini güncelle
            start_pos = self.sceneBoundingRect().center()
            end_pos = self.mapToScene(event.pos())
            self.temp_connection.setLine(
                start_pos.x(), start_pos.y(),
                end_pos.x(), end_pos.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.old_pos is not None:
            new_pos = self.pos()
            if self.old_pos != new_pos:
                from src.core.commands import MoveElementCommand
                view = self.scene().views()[0]
                if view.main_window:
                    command = MoveElementCommand(self, self.old_pos, new_pos)
                    view.main_window.command_stack.execute(command)
            self.old_pos = None
        elif event.button() == Qt.MouseButton.RightButton and self.is_drawing_connection:
            # Hedef elementi bul
            end_pos = self.mapToScene(event.pos())
            items = self.scene().items(end_pos)
            
            target_item = None
            for item in items:
                if isinstance(item, ElementGraphicsItem) and item != self:
                    target_item = item
                    break
            
            # Bağlantıyı oluştur
            if target_item:
                connection = ConnectionGraphicsItem(self, target_item)
                self.scene().addItem(connection)
            
            # Geçici çizgiyi kaldır
            if self.temp_connection:
                self.scene().removeItem(self.temp_connection)
                self.temp_connection = None
            
            self.is_drawing_connection = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.editor:
            self.editor = ElementEditor(self)
            self.editor_proxy = self.scene().addWidget(self.editor)
            self.editor_proxy.setPos(self.pos())
            self.editor_proxy.setMinimumSize(300, 200)
            self.setRect(0, 0, 300, 200)
        super().mouseDoubleClickEvent(event)

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush())
        painter.setPen(self.selected_pen if self.isSelected() else self.default_pen)
        painter.drawRect(self.rect())
        
        painter.setPen(Qt.PenStyle.SolidLine)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 5, -10, -10), 
                        Qt.AlignmentFlag.AlignTop, self.element.title)
        
        font.setBold(False)
        painter.setFont(font)
        content_rect = self.rect().adjusted(10, 30, -10, -10)
        painter.drawText(content_rect, Qt.TextFlag.TextWordWrap, self.element.content)

    def keyPressEvent(self, event):
        """Delete tuşu ile silme"""
        if event.key() == Qt.Key.Key_Delete:
            # DeleteElementCommand kullan
            if self.scene():
                from src.core.commands import DeleteElementCommand
                view = self.scene().views()[0]
                if view.main_window:
                    if self.editor:  # Eğer düzenleme penceresi açıksa kapat
                        self.close_editor()
                    command = DeleteElementCommand(self.scene(), self)
                    view.main_window.command_stack.execute(command)
                    print("Element deleted")  # Debug için
        else:
            super().keyPressEvent(event)
    
    def close_editor(self):
        """Editörü kapat"""
        if self.editor:
            if hasattr(self.editor, 'save_changes'):
                self.editor.save_changes()
            if self.editor_proxy:
                self.scene().removeItem(self.editor_proxy)
            self.editor = None
            self.editor_proxy = None
            self.setRect(0, 0, self.default_width, self.default_height)

class BoardView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
        # Scene oluştur
        self.scene = BoardGraphicsScene()
        self.setScene(self.scene)
        
        # Görünüm ayarları
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        # Zoom ayarları
        self.zoom = 1.0
        self.zoom_factor = 1.1
        
        # Grid ayarları
        self.show_grid = True
        
        # Pan ayarları
        self.last_mouse_pos = QPointF()
        self.panning = False
    
    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            if zoom_in:
                self.zoom *= self.zoom_factor
                self.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.zoom /= self.zoom_factor
                self.scale(1/self.zoom_factor, 1/self.zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x()))
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y()))
            self.last_mouse_pos = event.position()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        items = self.scene.items(scene_pos)
        
        if not any(isinstance(item, ElementGraphicsItem) for item in items):
            from core.element import Element
            from core.commands import AddElementCommand
            element = Element("Yeni Element", "İçerik buraya...")
            command = AddElementCommand(self.scene, element, scene_pos)
            self.main_window.command_stack.execute(command)
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        """Tuş olaylarını yakala"""
        if event.key() == Qt.Key.Key_Delete:
            # Seçili elementleri sil
            selected_items = [item for item in self.scene.selectedItems() 
                            if isinstance(item, ElementGraphicsItem)]
            
            from src.core.commands import DeleteElementCommand
            for item in selected_items:
                command = DeleteElementCommand(self.scene, item)
                self.main_window.command_stack.execute(command)
        else:
            super().keyPressEvent(event)

        """Tuş olaylarını yakala"""
        if event.key() == Qt.Key.Key_Delete:
            # Seçili elementleri sil
            selected_items = [item for item in self.scene.selectedItems() 
                            if isinstance(item, ElementGraphicsItem)]
            
            for item in selected_items:
                # Önce bağlantıları sil
                connections_to_remove = []
                for scene_item in self.scene.items():
                    if isinstance(scene_item, ConnectionGraphicsItem):
                        if scene_item.source_item == item or scene_item.target_item == item:
                            connections_to_remove.append(scene_item)
                
                for conn in connections_to_remove:
                    self.scene.removeItem(conn)
                
                # Elementi sahneden sil
                self.scene.removeItem(item)
                
                # Board verilerinden sil
                if self.main_window and self.main_window.current_board:
                    if item.element.id in self.main_window.current_board.elements:
                        del self.main_window.current_board.elements[item.element.id]
                        # Sol paneli güncelle
                        self.main_window.project_explorer.refresh_elements(self.main_window.current_board)
            
        super().keyPressEvent(event)

    def set_zoom(self, factor):
        """Zoom seviyesini ayarla"""
        print(f"Setting zoom to: {factor}")  # Debug için
        # Zoom faktörünü sınırla
        factor = max(0.25, min(4.0, factor))
        
        # Mevcut transformu sıfırla
        self.resetTransform()
        
        # Yeni zoom uygula
        self.scale(factor, factor)
        self.zoom = factor
        print(f"Zoom applied: {factor}")  # Debug için
        """Zoom seviyesini ayarla"""
        # Yeni zoom seviyesini 0.25 ile 4.0 arasında sınırla
        factor = max(0.25, min(4.0, factor))
        
        # Transform matrisini sıfırla ve yeni zoom uygula
        transform = QTransform()
        transform.scale(factor, factor)
        self.setTransform(transform)
        
        # Zoom seviyesini güncelle
        self.zoom = factor
        """Zoom seviyesini ayarla"""
        # Geçerli zoom seviyesini al
        current_factor = self.transform().m11()
        # Yeni zoom seviyesine göre ölçeklendirme faktörünü hesapla
        scale_factor = factor / current_factor
        # Ölçeklendirmeyi uygula
        self.scale(scale_factor, scale_factor)
        self.zoom = factor
        """Zoom seviyesini ayarla"""
        current_factor = self.transform().m11()  # Mevcut zoom seviyesi
        scale_factor = factor / current_factor
        self.scale(scale_factor, scale_factor)
        self.zoom = factor
    
    def fit_to_view(self):
        """Tüm içeriği görünür pencereye sığdır"""
        rect = self.scene.itemsBoundingRect()
        if not rect.isEmpty():
            # Kenarlardan biraz boşluk bırak
            rect.adjust(-50, -50, 50, 50)
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            # Zoom seviyesini güncelle
            self.zoom = self.transform().m11()
            # Toolbar'daki göstergeyi güncelle
            if self.main_window and hasattr(self.main_window, 'toolbar'):
                self.main_window.toolbar.set_zoom_level(self.zoom)

    def set_grid_visible(self, visible):
        """Grid görünürlüğünü ayarla"""
        print(f"Board view setting grid to: {visible}")  # Debug için
        if isinstance(self.scene, BoardGraphicsScene):
            self.scene.set_grid_visible(visible)


     
    def wheelEvent(self, event):
        """Mouse tekerleği ile zoom (Ctrl tuşuyla)"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            
            if zoom_in:
                self.zoom *= self.zoom_factor
            else:
                self.zoom /= self.zoom_factor
                
            # Zoom sınırlarını kontrol et
            self.zoom = max(0.25, min(4.0, self.zoom))
            
            # Zoom uygula
            self.setTransform(QTransform().scale(self.zoom, self.zoom))
            
            # Toolbar'daki göstergeyi güncelle
            if self.main_window and hasattr(self.main_window, 'toolbar'):
                self.main_window.toolbar.set_zoom_level(self.zoom)
                
            event.accept()
        else:
            super().wheelEvent(event)

class ElementEditor(QWidget):
    def __init__(self, element_item):
        super().__init__()
        self.element_item = element_item
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Başlık düzenleme
        self.title_edit = QTextEdit()
        self.title_edit.setMaximumHeight(50)
        self.title_edit.setPlainText(self.element_item.element.title)
        layout.addWidget(self.title_edit)
        
        # İçerik düzenleme
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(self.element_item.element.content)
        layout.addWidget(self.content_edit)
        
    def save_changes(self):
        self.element_item.element.title = self.title_edit.toPlainText()
        self.element_item.element.content = self.content_edit.toPlainText()
        self.element_item.update()