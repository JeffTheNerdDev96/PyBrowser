# Made By JeffTheNerdDev96

# Based On PyQt6 and Chromium

#NOT WORKING VERSION WITH ADBLOCKER


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile
from urllib.parse import quote_plus, urlparse
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent


def normalize_adblock_rule(rule):
    """Return a normalized (host, path_prefix) tuple, or None for unsupported rules."""
    rule = rule.strip()
    if not rule or rule.startswith(("#", "!", "[")):
        return None

    rule = rule.split("#", 1)[0].strip()
    rule = rule.split("$", 1)[0].strip()
    if not rule:
        return None

    if rule.startswith(("0.0.0.0 ", "127.0.0.1 ")):
        parts = rule.split()
        rule = parts[1] if len(parts) > 1 else ""
    elif rule.startswith("||"):
        rule = rule[2:]

    rule = rule.lstrip("|").rstrip("^")
    if not rule:
        return None

    parsed = urlparse(rule if "://" in rule else f"https://{rule}")
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host or "." not in host:
        return None

    path_prefix = parsed.path.rstrip("/")
    return host, path_prefix

# --- Adblock Interceptor Class ---
class AdblockInterceptor(QWebEngineUrlRequestInterceptor):
    """
    A URL request interceptor to block requests based on a list of blocked domains.
    """
    def __init__(self, blocked_domains):
        super().__init__()
        self.blocked_hosts = set()
        self.blocked_paths = []
        for rule in blocked_domains:
            normalized = normalize_adblock_rule(rule)
            if normalized is None:
                continue

            host, path_prefix = normalized
            if path_prefix:
                self.blocked_paths.append((host, path_prefix))
            else:
                self.blocked_hosts.add(host)
        
        total_rules = len(self.blocked_hosts) + len(self.blocked_paths)
        print(f"Adblocker initialized with {total_rules} usable rules.")

    def interceptRequest(self, info):
        """
        Intercepts network requests and blocks them if the URL's host matches blocked domains.
        """
        request_url = info.requestUrl()
        host = request_url.host().lower()
        
        # Remove www. prefix for comparison  
        if host.startswith('www.'):
            host = host[4:]
        
        should_block = self._host_is_blocked(host)
        if not should_block:
            request_path = request_url.path().rstrip("/")
            should_block = any(
                self._host_matches(host, blocked_host) and request_path.startswith(path_prefix)
                for blocked_host, path_prefix in self.blocked_paths
            )
        
        if should_block:
            print(f"Blocked by adblocker: {request_url.toString()}")
            info.block(True)  # Block the request
        # Uncomment the line below for debugging allowed requests
        # else:
        #     print(f"Adblocker allowed: {request_url.toString()}")

    def _host_is_blocked(self, host):
        parts = host.split(".")
        return any(".".join(parts[index:]) in self.blocked_hosts for index in range(len(parts)))

    @staticmethod
    def _host_matches(host, blocked_host):
        return host == blocked_host or host.endswith("." + blocked_host)

# --- Browser Class ---
class Browser(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py Browser - Ad Blocker Enabled")
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
        
        self.back_btn = QPushButton("<")
        self.forward_btn = QPushButton(">")
        self.reload_btn = QPushButton("Reload")
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search term...")
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar) 

        # Create browser view first
        self.browser_view = QWebEngineView()
        
        # --- Initialize Adblocker AFTER creating browser view ---
        self.adblock_list = self.load_adblock_list(APP_DIR / "adblock.txt")
        if not self.adblock_list:
            # Add some common ad domains as defaults if no file exists
            self.adblock_list = [
                "doubleclick.net",
                "googleadservices.com", 
                "googlesyndication.com",
                "facebook.com/tr",
                "google-analytics.com",
                "googletagmanager.com",
                "ads.yahoo.com",
                "adsystem.amazon.com"
            ]
            print("Using default ad blocking list.")
        
        self.adblock_interceptor = AdblockInterceptor(self.adblock_list)
        
        # Set up the web engine profile with ad blocker - ensure profile exists
        profile = None
        try:
            # First try to get the profile from the browser view's page
            page = self.browser_view.page()
            if page is not None:
                profile = page.profile()
            
            if profile is not None:
                profile.setUrlRequestInterceptor(self.adblock_interceptor)
                print("Ad blocker interceptor registered successfully with page profile")
            else:
                raise Exception("Page profile is None")
                
        except Exception as e:
            print(f"Error setting up ad blocker with page profile: {e}")
            # Fallback: try default profile
            try:
                profile = QWebEngineProfile.defaultProfile()
                if profile is not None:
                    profile.setUrlRequestInterceptor(self.adblock_interceptor)
                    print("Ad blocker registered with default profile")
                else:
                    print("Default profile is also None")
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                profile = None
        
        self.browser_view.setUrl(QUrl("https://www.google.com"))
        
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.browser_view)
        
        self.back_btn.clicked.connect(self.browser_view.back)
        self.forward_btn.clicked.connect(self.browser_view.forward)
        self.reload_btn.clicked.connect(self.browser_view.reload)
        self.url_bar.returnPressed.connect(self.navigate)
        self.browser_view.urlChanged.connect(lambda url: self.url_bar.setText(url.toString()))
        self.browser_view.loadFinished.connect(self.on_load_finished)

        # Security Note: QWebEngineView uses Chromium's sandboxing by default.
        # It is crucial NOT to disable the sandbox (e.g., via command-line arguments like --no-sandbox)
        # as this significantly increases security risks.

    def load_adblock_list(self, filename):
        """
        Loads a list of blocked domains from the specified file.
        Assumes one domain per line. Supports comments starting with #.
        """
        blocked_domains = []
        adblock_path = Path(filename)
        if adblock_path.exists():
            try:
                with adblock_path.open('r', encoding='utf-8') as f:
                    for line in f:
                        domain = line.strip()
                        if normalize_adblock_rule(domain) is not None:
                            blocked_domains.append(domain)
                            
                print(f"Loaded {len(blocked_domains)} domains from {adblock_path}")
            except IOError as e:
                print(f"Error loading adblock file {adblock_path}: {e}")
        else:
            print(f"Adblock file '{adblock_path}' not found.")
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
            return

        looks_like_domain = "." in url_text and " " not in url_text
        if looks_like_domain:
            prefixed_q_url = QUrl("https://" + url_text)
            if prefixed_q_url.isValid():
                self.browser_view.setUrl(prefixed_q_url)
                return

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
    
    print("PyQt6 Browser with Ad Blocker started!")
    print("Place your ad blocking domains in 'adblock.txt' (one per line)")
    print("Ad blocker is active and monitoring requests")
    
    sys.exit(app.exec())
