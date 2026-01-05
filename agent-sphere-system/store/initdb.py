# Optional: Run this script once to create database tables
from storage_backends import DatabaseStorageBackend
from store.config import Config

Config.STORAGE_BACKEND = 'database'
backend = DatabaseStorageBackend()
print("✅ Database initialized!")