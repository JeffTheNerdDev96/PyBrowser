import sys
import os 
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor


# --- Ad Blocker Logic ---

def load_ad_block_list(filename="adblock_domains.txt"):
    """
    Loads ad blocking domains from a text file.
    Each line in the file should be a domain or pattern to block.
    """
    block_list = set() # Use a set for faster lookup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'): # Ignore empty lines and comments
                    block_list.add(line)
        print(f"Loaded {len(block_list)} ad blocking rules from {filename}")
    except FileNotFoundError:
        print(f"Warning: Ad block list file '{filename}' not found at {filepath}. Ad blocker will not function.")
    except Exception as e:
        print(f"Error loading ad block list from {filename}: {e}")
    return block_list
