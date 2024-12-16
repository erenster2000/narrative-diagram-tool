import json
from datetime import datetime
import os

class ProjectFileHandler:
    @staticmethod
    def save_project(project, filepath):
        """Projeyi JSON olarak kaydet"""
        print(f"Saving project: {project.name}")
        print(f"Number of boards: {len(project.boards)}")
        
        # En üst seviye proje verisi
        project_data = {
            'project': {  # Burayı düzelttik
                'id': project.id,
                'name': project.name,
                'created_at': project.created_at.isoformat(),
                'modified_at': datetime.now().isoformat(),
                'boards': {}
            }
        }
        
        for board_id, board in project.boards.items():
            print(f"Saving board: {board.name}")
            print(f"Number of elements: {len(board.elements)}")
            print(f"Number of connections: {len(board.connections)}")
            
            board_data = {
                'id': board.id,
                'name': board.name,
                'root': board.root,
                'elements': {},
                'connections': []
            }
            
            # Elementleri kaydet
            for element_id, element in board.elements.items():
                print(f"Saving element: {element.title} at position {element.position}")
                board_data['elements'][element_id] = {
                    'id': element.id,
                    'title': element.title,
                    'content': element.content,
                    'position': element.position,
                    'size': element.size
                }
            
            # Bağlantıları kaydet
            for connection_id, connection in board.connections.items():
                print(f"Saving connection from {connection.source_id} to {connection.target_id}")
                board_data['connections'].append({
                    'id': connection.id,
                    'source_id': connection.source_id,
                    'target_id': connection.target_id
                })
            
            project_data['project']['boards'][board_id] = board_data
        
        # JSON'a kaydet
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)
            print(f"Project saved to: {filepath}")

    @staticmethod
    def load_project(filepath):
        """JSON dosyasından proje yükle"""
        from core.project import Project
        from core.board import Board
        from core.element import Element
        from core.connection import Connection
        
        print(f"Loading project from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("File loaded successfully")
            print(f"Project data: {data.keys()}")
        
        project_data = data['project']  # Burayı düzelttik
        
        # Yeni proje oluştur
        project = Project(project_data['name'])
        project.id = project_data['id']
        project.created_at = datetime.fromisoformat(project_data['created_at'])
        
        # Board'ları yükle
        for board_id, board_data in project_data['boards'].items():
            print(f"Loading board: {board_data['name']}")
            board = Board(board_data['name'], board_data.get('root', False))
            board.id = board_data['id']
            
            # Elementleri yükle
            print(f"Loading {len(board_data.get('elements', {}))} elements")
            for element_id, element_data in board_data.get('elements', {}).items():
                print(f"Loading element: {element_data['title']}")
                element = Element(element_data['title'], element_data.get('content', ''))
                element.id = element_data['id']
                element.position = element_data['position']
                element.size = element_data['size']
                board.elements[element_id] = element
            
            # Bağlantıları yükle
            print(f"Loading {len(board_data.get('connections', []))} connections")
            for conn_data in board_data.get('connections', []):
                connection = Connection(conn_data['source_id'], conn_data['target_id'])
                connection.id = conn_data['id']
                board.connections[connection.id] = connection
            
            project.boards[board_id] = board
        
        return project