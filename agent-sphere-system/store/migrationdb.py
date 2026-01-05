# migration_script.py
from storage_backends import JSONStorageBackend, DatabaseStorageBackend
from store.config import Config

# Load from JSON
json_backend = JSONStorageBackend()
agents_data = json_backend.load_agents()
tools_data = json_backend.load_tools()

# Save to Database
Config.STORAGE_BACKEND = 'database'
db_backend = DatabaseStorageBackend()
db_backend.save_agents(agents_data)
db_backend.save_tools(tools_data)

print("✅ Migration complete!")