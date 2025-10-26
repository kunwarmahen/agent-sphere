"""
persistence.py - Add this file to save/load custom agents and tools
"""

import json
import os
from pathlib import Path

# Data directory for persistence
DATA_DIR = Path("data")
AGENTS_FILE = DATA_DIR / "custom_agents.json"
TOOLS_FILE = DATA_DIR / "custom_tools.json"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(exist_ok=True)

def save_custom_agents(custom_agents_dict):
    """Save custom agents to JSON file"""
    ensure_data_dir()
    try:
        with open(AGENTS_FILE, 'w') as f:
            json.dump(custom_agents_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving custom agents: {e}")
        return False

def load_custom_agents():
    """Load custom agents from JSON file"""
    if not AGENTS_FILE.exists():
        return {}
    
    try:
        with open(AGENTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading custom agents: {e}")
        return {}

def save_custom_tools(custom_tools_dict):
    """Save custom tools to JSON file"""
    ensure_data_dir()
    try:
        with open(TOOLS_FILE, 'w') as f:
            json.dump(custom_tools_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving custom tools: {e}")
        return False

def load_custom_tools():
    """Load custom tools from JSON file"""
    if not TOOLS_FILE.exists():
        return {}
    
    try:
        with open(TOOLS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading custom tools: {e}")
        return {}