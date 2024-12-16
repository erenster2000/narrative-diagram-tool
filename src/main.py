import sys
import os

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Ana pencereyi oluştur
    window = MainWindow()
    window.show()

    # Uygulamayı başlat
    sys.exit(app.exec())


if __name__ == "__main__":
    main()