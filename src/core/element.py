from uuid import uuid4
from datetime import datetime


class Element:
    """Element sınıfı - hikayedeki her bir düğümü temsil eder"""

    def __init__(self, title: str = "", content: str = ""):
        self.id: str = str(uuid4())
        self.title: str = title
        self.content: str = content
        self.theme: str = "default"  # Görsel tema
        self.components: list = []  # Bağlı component ID'leri
        self.position: dict = {'x': 0, 'y': 0}  # Board üzerindeki konumu
        self.size: dict = {'width': 200, 'height': 150}  # Element boyutu
        self.created_at: datetime = datetime.now()
        self.modified_at: datetime = datetime.now()

    def set_position(self, x: float, y: float) -> None:
        """Element'in konumunu ayarla"""
        self.position['x'] = x
        self.position['y'] = y
        self.modified_at = datetime.now()

    def set_size(self, width: float, height: float) -> None:
        """Element'in boyutunu ayarla"""
        self.size['width'] = width
        self.size['height'] = height
        self.modified_at = datetime.now()

    def add_component(self, component_id: str) -> None:
        """Element'e component bağla"""
        if component_id not in self.components:
            self.components.append(component_id)
            self.modified_at = datetime.now()

    def remove_component(self, component_id: str) -> None:
        """Element'ten component bağlantısını kaldır"""
        if component_id in self.components:
            self.components.remove(component_id)
            self.modified_at = datetime.now()

    def to_dict(self) -> dict:
        """Element'i JSON serileştirme için dict'e çevir"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'theme': self.theme,
            'components': self.components,
            'position': self.position,
            'size': self.size,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Element':
        """Dict'ten element oluştur"""
        element = cls(data['title'], data['content'])
        element.id = data['id']
        element.theme = data['theme']
        element.components = data['components']
        element.position = data['position']
        element.size = data['size']
        element.created_at = datetime.fromisoformat(data['created_at'])
        element.modified_at = datetime.fromisoformat(data['modified_at'])
        return element

    def move_to(self, x: float, y: float) -> None:
        """Element'i belirtilen konuma taşı"""
        self.set_position(x, y)
        print(f"Element {self.title} moved to ({x}, {y})")

    def resize_to(self, width: float, height: float) -> None:
        """Element'i belirtilen boyuta getir"""
        self.set_size(width, height)
        print(f"Element {self.title} resized to {width}x{height}")

    def update_content(self, title: str = None, content: str = None) -> None:
        """Element içeriğini güncelle"""
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        self.modified_at = datetime.now()
        print(f"Element {self.id} content updated")

    def duplicate(self) -> 'Element':
        """Element'in bir kopyasını oluştur"""
        new_element = Element(f"{self.title} (Copy)", self.content)
        new_element.theme = self.theme
        new_element.components = self.components.copy()
        new_element.position = {'x': self.position['x'] + 20, 'y': self.position['y'] + 20}
        new_element.size = self.size.copy()
        return new_element

    def __str__(self) -> str:
        """Element'in string gösterimi"""
        return f"Element(id={self.id}, title='{self.title}')"

    def __repr__(self) -> str:
        """Element'in detaylı string gösterimi"""
        return (f"Element(id={self.id}, title='{self.title}', "
                f"pos=({self.position['x']}, {self.position['y']}))")