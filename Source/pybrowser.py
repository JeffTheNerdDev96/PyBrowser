# Made By JeffTheNerdDev96

#Based On PyQt6 and Chromium

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt # Import Qt for alignment 
# from PyQt6.QtGui import QIcon # Import favicon

class Browser(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py Browser")
        # Set a reasonable default geometry. Adjust as needed.
        # This will set the initial size and position.
        self.setGeometry(100, 100, 1200, 800) 
        
        # Apply stylesheet once during initialization.
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
        
        # Central widget is crucial for a QMainWindow to hold other widgets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout for the central widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8) # Space between widgets/layouts
        main_layout.setContentsMargins(8, 8, 8, 8) # Padding around the edges

        # Navigation bar layout
        nav_layout = QHBoxLayout()
        
        # Initialize navigation buttons
        # Ensure buttons have clear parentage if not added directly to a layout immediately
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        
        # Initialize URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        
        # Add widgets to the navigation layout
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar) # QLineEdit naturally expands in QHBoxLayout

        # Web view widget
        self.browser_view = QWebEngineView()

        # Setting the initial URL directly on the QWebEngineView
        self.browser_view.setUrl(QUrl("https://www.google.com"))
        
        # Add the navigation layout and the browser view to the main layout
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.browser_view)
        
        # Connect signals and slots
        self.back_btn.clicked.connect(self.browser_view.back)
        self.forward_btn.clicked.connect(self.browser_view.forward)
        self.reload_btn.clicked.connect(self.browser_view.reload)
        
        # Connecting QLineEdit's returnPressed signal to custom navigate method
        self.url_bar.returnPressed.connect(self.navigate)
        
        # Connecting browser's urlChanged signal to update the URL bar.
        self.browser_view.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))

        # self.browser_view.urlChanged.connect(self._update_url_bar)

    def navigate(self):
        """Navigates the browser to the URL entered in the URL bar."""
        url_text = self.url_bar.text()
        # Basic URL prefixing for convenience.
        if not url_text.startswith(('http://', 'https://')):
            url_text = 'https://' + url_text
        self.browser_view.setUrl(QUrl(url_text))

    def _update_url_bar(self, url: QUrl):
        self.url_bar.setText(url.toString())

# Entry point for the application
if __name__ == "__main__":
    # QApplication must be created first.
    app = QApplication(sys.argv)
    
    # Setting the style to 'Fusion' gives a modern, consistent look across platforms.
    app.setStyle('Fusion') 
    
    # Create and show the main window
    browser_window = Browser()
    browser_window.show()
    
    # Start the Qt event loop. This line blocks until the application exits.
    sys.exit(app.exec())