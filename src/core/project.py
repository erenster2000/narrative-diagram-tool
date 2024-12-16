from uuid import uuid4
from typing import List, Optional, Dict
from datetime import datetime

class Project:
    """Narrative tool projesi için ana sınıf"""
    
    def __init__(self, name: str):
        self.id: str = str(uuid4())
        self.name: str = name
        self.created_at: datetime = datetime.now()
        self.modified_at: datetime = datetime.now()
        self.boards: Dict[str, 'Board'] = {}  # board_id -> Board
        self.components: Dict[str, 'Component'] = {}  # component_id -> Component
        self.variables: Dict[str, 'Variable'] = {}  # variable_name -> Variable
        self.starting_element: Optional[str] = None  # element_id
        self.save_path: Optional[str] = None
        
    def add_board(self, board: 'Board') -> None:
        """Projeye yeni bir board ekle"""
        self.boards[board.id] = board
        self.modified_at = datetime.now()
        
    def remove_board(self, board_id: str) -> None:
        """Projeden bir board'u kaldır"""
        if board_id in self.boards:
            del self.boards[board_id]
            self.modified_at = datetime.now()
            
    def get_board(self, board_id: str) -> Optional['Board']:
        """ID'ye göre board getir"""
        return self.boards.get(board_id)
    
    def set_starting_element(self, element_id: str) -> None:
        """Başlangıç elementini ayarla"""
        self.starting_element = element_id
        self.modified_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Projeyi JSON serileştirme için dict'e çevir"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'boards': {bid: board.to_dict() for bid, board in self.boards.items()},
            'components': {cid: comp.to_dict() for cid, comp in self.components.items()},
            'variables': {name: var.to_dict() for name, var in self.variables.items()},
            'starting_element': self.starting_element,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Dict'ten proje oluştur"""
        project = cls(data['name'])
        project.id = data['id']
        project.created_at = datetime.fromisoformat(data['created_at'])
        project.modified_at = datetime.fromisoformat(data['modified_at'])
        project.starting_element = data['starting_element']
        
        # Board'ları, component'leri ve variable'ları daha sonra yükleyeceğiz
        return project