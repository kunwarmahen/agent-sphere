"""
config.py - Centralized configuration with environment variables
"""

import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    
    # Storage backend: 'json' or 'database'
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'json')
    
    # Database configuration (if using database backend)
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite' or 'postgresql'
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/agents.db')
    
    # PostgreSQL example:
    # DATABASE_URL = 'postgresql://user:password@localhost:5432/agents_db'
    
    # Analytics
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    
    # Templates
    TEMPLATES_DIR = DATA_DIR / "templates"
    
    # Testing
    ENABLE_TESTING = os.getenv('ENABLE_TESTING', 'true').lower() == 'true'
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.TEMPLATES_DIR.mkdir(exist_ok=True)
        
    @classmethod
    def get_storage_backend(cls):
        """Get the configured storage backend"""
        return cls.STORAGE_BACKEND
    
    @classmethod
    def switch_storage_backend(cls, backend: str):
        """Switch storage backend at runtime"""
        if backend not in ['json', 'database']:
            raise ValueError("Backend must be 'json' or 'database'")
        cls.STORAGE_BACKEND = backend
        print(f"✅ Switched storage backend to: {backend}")


# Initialize directories on import
Config.ensure_directories()