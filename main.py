import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QPushButton { 
                background-color: #2d2d2d; color: #ffffff; border: 1px solid #404040;
                padding: 8px 16px; border-radius: 6px; font-size: 14px;
            }
            QPushButton:hover { background-color: #3d3d3d; }
            QPushButton:pressed { background-color: #1d1d1d; }
            QLineEdit { 
                background-color: #2d2d2d; color: #ffffff; border: 1px solid #404040;
                padding: 8px; border-radius: 6px; font-size: 14px;
            }
        """)
        
        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Navigation bar
        nav = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        
        nav.addWidget(self.back_btn)
        nav.addWidget(self.forward_btn)
        nav.addWidget(self.reload_btn)
        nav.addWidget(self.url_bar)
        
        # Web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        
        layout.addLayout(nav)
        layout.addWidget(self.browser)
        
        # Connect signals
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.url_bar.returnPressed.connect(self.navigate)
        self.browser.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))
        
    def navigate(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = Browser()
    window.show()
    sys.exit(app.exec())