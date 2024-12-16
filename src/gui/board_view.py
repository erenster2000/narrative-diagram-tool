from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                           QGraphicsRectItem, QMenu, QGraphicsTextItem,
                           QGraphicsProxyWidget, QTextEdit, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QRectF, QPointF, QMetaObject, Q_ARG, QLineF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QPolygonF
import math

class ElementEditor(QWidget):
    def __init__(self, element_item):
        super().__init__()
        self.element_item = element_item
        self.original_size = element_item.rect().size()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Başlık düzenleme
        self.title_edit = QTextEdit()
        self.title_edit.setMaximumHeight(50)
        self.title_edit.setPlainText(self.element_item.element.title)
        # Enter tuşunu yakala
        self.title_edit.installEventFilter(self)
        layout.addWidget(self.title_edit)

        # İçerik düzenleme
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(self.element_item.element.content)
        layout.addWidget(self.content_edit)

    def eventFilter(self, obj, event):
        """Enter tuşunu yakala"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        if (obj == self.title_edit and event.type() == QEvent.Type.KeyPress and
            isinstance(event, QKeyEvent) and event.key() == Qt.Key.Key_Return):
            # Alt satıra geçmek yerine düzenlemeyi bitir
            self.element_item.close_editor()
            return True
        return super().eventFilter(obj, event)

    def save_changes(self):
        """Değişiklikleri kaydet"""
        old_title = self.element_item.element.title
        new_title = self.title_edit.toPlainText().strip()
        new_content = self.content_edit.toPlainText()

        # Değişiklikleri kaydet
        self.element_item.element.title = new_title
        self.element_item.element.content = new_content

        # Element boyutunu orijinal haline döndür
        self.element_item.setRect(0, 0, self.original_size.width(), self.original_size.height())

        # Başlık değiştiyse sol paneli güncelle
        if old_title != new_title:
            if self.element_item.scene():
                view = self.element_item.scene().views()[0]
                if view and hasattr(view, 'main_window'):
                    view.main_window.project_explorer.refresh_elements(
                        view.main_window.current_board)

        self.element_item.update()

class ConnectionGraphicsItem(QGraphicsItem):
    def __init__(self, source_item, target_item):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self._pen = QPen(QColor(100, 100, 100))
        self._pen.setWidth(2)
        self.arrow_size = 15

    def _find_intersection_point(self, source_rect, target_point):
        """Elementlerin kenarları ile kesişim noktasını bul"""
        center = source_rect.center()

        # Rectangle'ın kenarlarını kontrol et
        if target_point.x() > center.x():  # Sağ taraf
            line_start = QPointF(source_rect.right(), source_rect.center().y())
        else:  # Sol taraf
            line_start = QPointF(source_rect.left(), source_rect.center().y())

        if abs(target_point.y() - center.y()) > abs(target_point.x() - center.x()):
            if target_point.y() > center.y():  # Alt taraf
                line_start = QPointF(source_rect.center().x(), source_rect.bottom())
            else:  # Üst taraf
                line_start = QPointF(source_rect.center().x(), source_rect.top())

        return line_start

    def boundingRect(self):
        # Kaynak ve hedef elementleri içine alan rectangle'ı döndür
        return self.shape().boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Element rectangle'larını al
        source_rect = self.source_item.sceneBoundingRect()
        target_rect = self.target_item.sceneBoundingRect()

        # Başlangıç ve bitiş noktalarını hesapla
        # Başlangıç noktası
        target_center = target_rect.center()
        start_point = self._find_intersection_point(source_rect, target_center)

        # Bitiş noktası
        source_center = source_rect.center()
        end_point = self._find_intersection_point(target_rect, source_center)

        # Ana çizgiyi çiz
        painter.setPen(self._pen)
        painter.drawLine(start_point, end_point)

        # Ok başını çiz
        angle = math.atan2(end_point.y() - start_point.y(),
                          end_point.x() - start_point.x())

        # Ok başı noktaları
        arrowhead_p1 = QPointF(
            end_point.x() - self.arrow_size * math.cos(angle - math.pi/6),
            end_point.y() - self.arrow_size * math.sin(angle - math.pi/6)
        )

        arrowhead_p2 = QPointF(
            end_point.x() - self.arrow_size * math.cos(angle + math.pi/6),
            end_point.y() - self.arrow_size * math.sin(angle + math.pi/6)
        )

        # Ok başını çiz
        painter.setBrush(QBrush(self._pen.color()))
        arrow_head = QPolygonF([end_point, arrowhead_p1, arrowhead_p2])
        painter.drawPolygon(arrow_head)

    def shape(self):
        path = QPainterPath()

        # Element rectangle'larını al
        source_rect = self.source_item.sceneBoundingRect()
        target_rect = self.target_item.sceneBoundingRect()

        # Başlangıç ve bitiş noktalarını hesapla
        target_center = target_rect.center()
        start_point = self._find_intersection_point(source_rect, target_center)

        source_center = source_rect.center()
        end_point = self._find_intersection_point(target_rect, source_center)

        # Ana çizgi
        path.moveTo(start_point)
        path.lineTo(end_point)

        # Ok başı için alan
        angle = math.atan2(end_point.y() - start_point.y(),
                          end_point.x() - start_point.x())

        arrowhead_p1 = QPointF(
            end_point.x() - self.arrow_size * math.cos(angle - math.pi/6),
            end_point.y() - self.arrow_size * math.sin(angle - math.pi/6)
        )

        arrowhead_p2 = QPointF(
            end_point.x() - self.arrow_size * math.cos(angle + math.pi/6),
            end_point.y() - self.arrow_size * math.sin(angle + math.pi/6)
        )

        path.addPolygon(QPolygonF([end_point, arrowhead_p1, arrowhead_p2]))
        return path

    def setPen(self, pen):
        self._pen = pen
        self.update()

    def __init__(self, source_item, target_item):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.arrow_size = 10.0
        self.setPen(QPen(QColor(100, 100, 100), 1.5))

    def _calculate_intersection_point(self, item, line):
        """Element ile çizginin kesişim noktasını hesapla"""
        rect = item.sceneBoundingRect()
        center = rect.center()

        # Element'in kenarlarını kontrol et
        intersections = []

        # Üst kenar
        top_line = QLineF(rect.topLeft(), rect.topRight())
        top_intersection = QPointF()
        if top_line.intersect(line, top_intersection) == QLineF.IntersectType.BoundedIntersection:
            intersections.append(top_intersection)

        # Alt kenar
        bottom_line = QLineF(rect.bottomLeft(), rect.bottomRight())
        bottom_intersection = QPointF()
        if bottom_line.intersect(line, bottom_intersection) == QLineF.IntersectType.BoundedIntersection:
            intersections.append(bottom_intersection)

        # Sol kenar
        left_line = QLineF(rect.topLeft(), rect.bottomLeft())
        left_intersection = QPointF()
        if left_line.intersect(line, left_intersection) == QLineF.IntersectType.BoundedIntersection:
            intersections.append(left_intersection)

        # Sağ kenar
        right_line = QLineF(rect.topRight(), rect.bottomRight())
        right_intersection = QPointF()
        if right_line.intersect(line, right_intersection) == QLineF.IntersectType.BoundedIntersection:
            intersections.append(right_intersection)

        # En yakın kesişim noktasını bul
        if intersections:
            return min(intersections, key=lambda p: QLineF(p, center).length())
        return center

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

    def mousePressEvent(self, event):
        """Mouse basılı tutma olayında başlangıç pozisyonunu kaydet"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = self.pos()
            # Element seçildiğinde properties paneli güncelle
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                if hasattr(view, 'main_window') and view.main_window:
                    if hasattr(view.main_window, 'properties_panel'):
                        view.main_window.properties_panel.set_element(self)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse bırakıldığında hareket komutu oluştur"""
        if event.button() == Qt.MouseButton.LeftButton and self.old_pos is not None:
            new_pos = self.pos()
            # Pozisyon değiştiyse komut oluştur
            if self.old_pos != new_pos:
                from core.commands import MoveElementCommand
                view = self.scene().views()[0]
                if view.main_window:
                    command = MoveElementCommand(self, self.old_pos, new_pos)
                    view.main_window.command_stack.execute(command)
            self.old_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Çift tıklama olayı - düzenleme modunu aç"""
        if not self.editor:
            self.editor = ElementEditor(self)
            self.editor_proxy = self.scene().addWidget(self.editor)
            self.editor_proxy.setPos(self.pos())
            self.editor_proxy.setMinimumSize(300, 200)

    def paint(self, painter, option, widget=None):
        """Element'in görsel çizimi"""
        # Arkaplan
        painter.setBrush(self.brush())
        painter.setPen(self.selected_pen if self.isSelected() else self.default_pen)
        painter.drawRect(self.rect())

        # Başlık
        painter.setPen(Qt.PenStyle.SolidLine)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(10, 5, -10, -10),
                         Qt.AlignmentFlag.AlignTop, self.element.title)

        # İçerik
        font.setBold(False)
        painter.setFont(font)
        content_rect = self.rect().adjusted(10, 30, -10, -10)
        painter.drawText(content_rect, Qt.TextFlag.TextWordWrap, self.element.content)

    def keyPressEvent(self, event):
        """Delete tuşu ile silme"""
        if event.key() == Qt.Key.Key_Delete:
            from core.commands import DeleteElementCommand
            view = self.scene().views()[0]
            if view.main_window:
                command = DeleteElementCommand(self.scene(), self)
                view.main_window.command_stack.execute(command)
        else:
            super().keyPressEvent(event)

class BoardGraphicsScene(QGraphicsScene):
    """Board için özel scene sınıfı"""

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -5000, 10000, 10000)  # Geniş bir çalışma alanı
        self._draw_grid()

    def _draw_grid(self, size: int = 20):
        """Arka plan ızgarasını çiz"""
        pen = QPen(QColor(50, 50, 50, 100))
        pen.setStyle(Qt.PenStyle.DotLine)

        # Dikey çizgiler
        for x in range(-5000, 5000, size):
            self.addLine(x, -5000, x, 5000, pen)

        # Yatay çizgiler
        for y in range(-5000, 5000, size):
            self.addLine(-5000, y, 5000, y, pen)

class BoardView(QGraphicsView):
    """Board görünümü için ana sınıf"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = BoardGraphicsScene()
        self.setScene(self.scene)
        self.main_window = parent  # MainWindow referansını sakla


        # Görünüm ayarları
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        # Yakınlaştırma seviyesi
        self.zoom = 1.0
        self.zoom_factor = 1.1

        # Mouse takibi için değişkenler
        self.last_mouse_pos = QPointF()
        self.panning = False


    # BoardView sınıfına yeni method ekleyelim
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            # Seçili elementleri sil
            for item in self.scene.selectedItems():
                if isinstance(item, ElementGraphicsItem):
                    item._delete_element()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """View'da çift tıklama olayını scene'e ilet"""
        scene_pos = self.mapToScene(event.pos())
        items = self.scene.items(scene_pos)

        if not any(isinstance(item, ElementGraphicsItem) for item in items):
            # Yeni element oluştur
            from core.element import Element
            from core.commands import AddElementCommand

            element = Element("Yeni Element", "İçerik buraya...")
            command = AddElementCommand(self.scene, element, scene_pos)
            self.main_window.command_stack.execute(command)
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        """Mouse tekerleği ile zoom kontrolü"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom in/out
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
        """Mouse basılı tutma olayı"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Mouse bırakma olayı"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Mouse hareket olayı"""
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