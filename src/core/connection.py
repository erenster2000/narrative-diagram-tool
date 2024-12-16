from uuid import uuid4
from typing import Optional, Dict
from datetime import datetime

class Connection:
    """Connection sınıfı - elementler arası bağlantıları temsil eder"""
    
    def __init__(self, source_id: str, target_id: str):
        self.id: str = str(uuid4())
        self.source_id: str = source_id
        self.target_id: str = target_id
        self.label: str = ""
        self.type: str = "bezier"  # bezier, straight, flowchart
        self.theme: str = "default"
        self.created_at: datetime = datetime.now()
        self.modified_at: datetime = datetime.now()
        
    def set_label(self, label: str) -> None:
        """Bağlantı etiketini ayarla"""
        self.label = label
        self.modified_at = datetime.now()
        
    def set_type(self, connection_type: str) -> None:
        """Bağlantı tipini ayarla"""
        if connection_type in ["bezier", "straight", "flowchart"]:
            self.type = connection_type
            self.modified_at = datetime.now()
            
    def to_dict(self) -> dict:
        """Connection'ı JSON serileştirme için dict'e çevir"""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'label': self.label,
            'type': self.type,
            'theme': self.theme,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Connection':
        """Dict'ten connection oluştur"""
        connection = cls(data['source_id'], data['target_id'])
        connection.id = data['id']
        connection.label = data['label']
        connection.type = data['type']
        connection.theme = data['theme']
        connection.created_at = datetime.fromisoformat(data['created_at'])
        connection.modified_at = datetime.fromisoformat(data['modified_at'])
        return connection