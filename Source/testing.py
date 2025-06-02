# Made By JeffTheNerdDev96

# Based On PyQt6 and Chromium

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt 
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile 
from urllib.parse import quote_plus
import os # For checking if adblock.txt exists

# --- Adblock Interceptor Class ---
class AdblockInterceptor(QWebEngineUrlRequestInterceptor):
    """
    A simple URL request interceptor to block requests based on a list of blocked domains.
    """
    def __init__(self, blocked_domains):
        super().__init__()
        # Using a set for efficient lookup
        self.blocked_domains = set(blocked_domains)
        print(f"Adblocker initialized with {len(self.blocked_domains)} blocked domains.")

    def interceptRequest(self, info):
        """
        Interprets the network request and blocks it if the URL's host is in the blocked_domains list.
        """
        request_url = info.requestUrl()
        host = request_url.host()

        if host in self.blocked_domains:
            print(f"Adblocker blocked: {request_url.toString()}")
            info.setBlocked(True) # Block the request
        # else:
            # print(f"Adblocker allowed: {request_url.toString()}") # Uncomment for debugging allowed requests

# --- Browser Class ---
class Browser(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py Browser")
        self.setGeometry(100, 100, 1200, 800) 

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
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8) 
        main_layout.setContentsMargins(8, 8, 8, 8) 

        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search term...")
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar) 

        self.browser_view = QWebEngineView()
        self.browser_view.setUrl(QUrl("https://www.google.com"))
        
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.browser_view)
        
        self.back_btn.clicked.connect(self.browser_view.back)
        self.forward_btn.clicked.connect(self.browser_view.forward)
        self.reload_btn.clicked.connect(self.browser_view.reload)
        self.url_bar.returnPressed.connect(self.navigate)
        self.browser_view.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))
        self.browser_view.loadFinished.connect(self.on_load_finished)

        # --- Adblocker Integration ---
        self.adblock_list = self.load_adblock_list("adblock.txt")
        self.adblock_interceptor = AdblockInterceptor(self.adblock_list)
        # Register the interceptor with the default QWebEngineProfile
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.adblock_interceptor)
        # --- End Adblocker Integration ---

        # Security Note: QWebEngineView uses Chromium's sandboxing by default.
        # It is crucial NOT to disable the sandbox (e.g., via command-line arguments like --no-sandbox)
        # as this significantly increases security risks.

    def load_adblock_list(self, filename):
        """
        Loads a list of blocked domains from the specified file.
        Assumes one domain per line.
        """
        blocked_domains = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        domain = line.strip()
                        if domain and not domain.startswith('#'): # Ignore empty lines and comments
                            blocked_domains.append(domain)
                print(f"Loaded adblock list from {filename}.")
            except IOError as e:
                print(f"Error loading adblock file {filename}: {e}")
        else:
            print(f"Adblock file '{filename}' not found. Adblocker will not block any domains.")
        return blocked_domains

    def navigate(self):
        """Navigates the browser to the URL entered in the URL bar,
        or performs a Google search if the input is not a valid URL.
        """
        url_text = self.url_bar.text().strip()

        if not url_text:
            return

        q_url = QUrl(url_text)

        if q_url.isValid() and q_url.scheme() in ('http', 'https'):
            self.browser_view.setUrl(q_url)
        else:
            prefixed_url = "https://" + url_text
            prefixed_q_url = QUrl(prefixed_url)

            if prefixed_q_url.isValid() and prefixed_q_url.scheme() == 'https':
                self.browser_view.setUrl(prefixed_q_url)
            else:
                search_query = quote_plus(url_text) 
                search_url = QUrl(f"https://www.google.com/search?q={search_query}")
                self.browser_view.setUrl(search_url)

    def on_load_finished(self, ok):
        """Handles the completion of a page load, checking for errors."""
        if not ok:
            error_message = f"Failed to load page: {self.browser_view.url().toString()}"
            print(error_message) 

    def show_message_box(self, title, message):
        """Displays a simple message box to the user."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


# Entry point for the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    
    browser_window = Browser()
    browser_window.show()
    
    sys.exit(app.exec())