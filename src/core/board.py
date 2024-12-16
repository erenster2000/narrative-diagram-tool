from sqlite3 import Connection
from uuid import uuid4
from typing import List, Dict, Optional
from datetime import datetime

from src.core.element import Element

class Board:
    """Board sınıfı - projedeki her bir çalışma alanını temsil eder"""
    
    def __init__(self, name: str, is_root: bool = False):
        self.id: str = str(uuid4())
        self.name: str = name
        self.root: bool = is_root
        self.elements: Dict[str, 'Element'] = {}  # element_id -> Element
        self.branches: Dict[str, 'Branch'] = {}  # branch_id -> Branch
        self.connections: Dict[str, 'Connection'] = {}  # connection_id -> Connection
        self.children: List[str] = []  # Alt board ID'leri
        self.created_at: datetime = datetime.now()
        self.modified_at: datetime = datetime.now()
        
    def add_element(self, element: 'Element') -> None:
        """Board'a yeni bir element ekle"""
        self.elements[element.id] = element
        self.modified_at = datetime.now()
        
    def remove_element(self, element_id: str) -> None:
        """Board'dan bir elementi kaldır"""
        if element_id in self.elements:
            # İlgili bağlantıları da kaldır
            connections_to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.source_id == element_id or conn.target_id == element_id:
                    connections_to_remove.append(conn_id)
                    
            for conn_id in connections_to_remove:
                del self.connections[conn_id]
                
            del self.elements[element_id]
            self.modified_at = datetime.now()
            
    def add_branch(self, branch: 'Branch') -> None:
        """Board'a yeni bir branch ekle"""
        self.branches[branch.id] = branch
        self.modified_at = datetime.now()
        
    def add_connection(self, connection: 'Connection') -> None:
        """Board'a yeni bir bağlantı ekle"""
        self.connections[connection.id] = connection
        self.modified_at = datetime.now()
        
    def get_element(self, element_id: str) -> Optional['Element']:
        """ID'ye göre element getir"""
        return self.elements.get(element_id)
        
    def to_dict(self):
        """Board'u JSON serileştirme için dict'e çevir"""
        return {
            'id': self.id,
            'name': self.name,
            'root': self.root,
            'elements': {eid: elem.to_dict() for eid, elem in self.elements.items()},
            'connections': self.connections,  # Bağlantıları kaydet
            'children': self.children,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Dict'ten board oluştur"""
        board = cls(data['name'], data.get('root', False))
        board.id = data['id']
        board.children = data['children']
        board.connections = data.get('connections', {})  # Bağlantıları yükle
        board.created_at = datetime.fromisoformat(data['created_at'])
        board.modified_at = datetime.fromisoformat(data['modified_at'])
        return board