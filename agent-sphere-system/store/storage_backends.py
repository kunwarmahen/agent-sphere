"""
storage_backends.py - Abstract storage layer supporting JSON and Database
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import json
from pathlib import Path
from store.config import Config

# Database imports (optional)
try:
    from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean, DateTime, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, scoped_session
    from datetime import datetime
    
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
    
    class AgentModel(Base):
        __tablename__ = 'custom_agents'
        
        id = Column(String(8), primary_key=True)
        name = Column(String(255), nullable=False)
        role = Column(String(255), nullable=False)
        description = Column(Text)
        system_instructions = Column(Text)
        tools = Column(JSON)  # Stored as JSON array
        created_by = Column(String(100))
        created_at = Column(String(50))
        updated_at = Column(String(50))
        published = Column(Boolean, default=False)
        status = Column(String(20))
        version = Column(String(20))
        tags = Column(JSON)  # Stored as JSON array
        published_at = Column(String(50), nullable=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'role': self.role,
                'description': self.description,
                'system_instructions': self.system_instructions,
                'tools': self.tools or [],
                'created_by': self.created_by,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'published': self.published,
                'status': self.status,
                'version': self.version,
                'tags': self.tags or [],
                'published_at': self.published_at
            }
    
    class ToolModel(Base):
        __tablename__ = 'custom_tools'
        
        id = Column(String(8), primary_key=True)
        name = Column(String(255), nullable=False)
        description = Column(Text)
        integration_type = Column(String(50))
        created_by = Column(String(100))
        created_at = Column(String(50))
        updated_at = Column(String(50))
        config = Column(JSON)
        parameters = Column(JSON)
        status = Column(String(20))
        test_result = Column(JSON, nullable=True)
        version = Column(String(20))
        published_at = Column(String(50), nullable=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'integration_type': self.integration_type,
                'created_by': self.created_by,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'config': self.config or {},
                'parameters': self.parameters or {},
                'status': self.status,
                'test_result': self.test_result,
                'version': self.version,
                'published_at': self.published_at
            }
    
    class AnalyticsModel(Base):
        __tablename__ = 'agent_analytics'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        agent_id = Column(String(8), nullable=False, index=True)
        execution_time = Column(String(50))
        success = Column(Boolean)
        error_message = Column(Text, nullable=True)
        tools_used = Column(JSON)
        response_time_ms = Column(Integer)
        user_id = Column(String(100))
        
        def to_dict(self):
            return {
                'id': self.id,
                'agent_id': self.agent_id,
                'execution_time': self.execution_time,
                'success': self.success,
                'error_message': self.error_message,
                'tools_used': self.tools_used or [],
                'response_time_ms': self.response_time_ms,
                'user_id': self.user_id
            }
    
    class TestResultModel(Base):
        __tablename__ = 'test_results'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        agent_id = Column(String(8), nullable=False, index=True)
        test_name = Column(String(255))
        test_input = Column(JSON)
        expected_output = Column(Text, nullable=True)
        actual_output = Column(Text, nullable=True)
        passed = Column(Boolean)
        error_message = Column(Text, nullable=True)
        execution_time = Column(String(50))
        response_time_ms = Column(Integer)
        
        def to_dict(self):
            return {
                'id': self.id,
                'agent_id': self.agent_id,
                'test_name': self.test_name,
                'test_input': self.test_input,
                'expected_output': self.expected_output,
                'actual_output': self.actual_output,
                'passed': self.passed,
                'error_message': self.error_message,
                'execution_time': self.execution_time,
                'response_time_ms': self.response_time_ms
            }
    
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("⚠️  SQLAlchemy not available. Install with: pip install sqlalchemy")


# Abstract Storage Interface
class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def save_agents(self, agents: Dict) -> bool:
        pass
    
    @abstractmethod
    def load_agents(self) -> Dict:
        pass
    
    @abstractmethod
    def save_tools(self, tools: Dict) -> bool:
        pass
    
    @abstractmethod
    def load_tools(self) -> Dict:
        pass
    
    @abstractmethod
    def save_analytics(self, analytics_entry: Dict) -> bool:
        pass
    
    @abstractmethod
    def load_analytics(self, agent_id: str = None) -> List[Dict]:
        pass
    
    @abstractmethod
    def save_test_result(self, test_result: Dict) -> bool:
        pass
    
    @abstractmethod
    def load_test_results(self, agent_id: str) -> List[Dict]:
        pass


# JSON Storage Backend
class JSONStorageBackend(StorageBackend):
    """File-based JSON storage"""
    
    def __init__(self):
        self.agents_file = Config.DATA_DIR / "custom_agents.json"
        self.tools_file = Config.DATA_DIR / "custom_tools.json"
        self.analytics_file = Config.DATA_DIR / "analytics.json"
        self.tests_file = Config.DATA_DIR / "test_results.json"
    
    def save_agents(self, agents: Dict) -> bool:
        try:
            with open(self.agents_file, 'w') as f:
                json.dump(agents, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving agents: {e}")
            return False
    
    def load_agents(self) -> Dict:
        if not self.agents_file.exists():
            return {}
        try:
            with open(self.agents_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading agents: {e}")
            return {}
    
    def save_tools(self, tools: Dict) -> bool:
        try:
            with open(self.tools_file, 'w') as f:
                json.dump(tools, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tools: {e}")
            return False
    
    def load_tools(self) -> Dict:
        if not self.tools_file.exists():
            return {}
        try:
            with open(self.tools_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tools: {e}")
            return {}
    
    def save_analytics(self, analytics_entry: Dict) -> bool:
        try:
            analytics = []
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    analytics = json.load(f)
            
            analytics.append(analytics_entry)
            
            with open(self.analytics_file, 'w') as f:
                json.dump(analytics, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving analytics: {e}")
            return False
    
    def load_analytics(self, agent_id: str = None) -> List[Dict]:
        if not self.analytics_file.exists():
            return []
        try:
            with open(self.analytics_file, 'r') as f:
                analytics = json.load(f)
            
            if agent_id:
                return [a for a in analytics if a.get('agent_id') == agent_id]
            return analytics
        except Exception as e:
            print(f"Error loading analytics: {e}")
            return []
    
    def save_test_result(self, test_result: Dict) -> bool:
        try:
            tests = []
            if self.tests_file.exists():
                with open(self.tests_file, 'r') as f:
                    tests = json.load(f)
            
            tests.append(test_result)
            
            with open(self.tests_file, 'w') as f:
                json.dump(tests, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving test result: {e}")
            return False
    
    def load_test_results(self, agent_id: str) -> List[Dict]:
        if not self.tests_file.exists():
            return []
        try:
            with open(self.tests_file, 'r') as f:
                tests = json.load(f)
            return [t for t in tests if t.get('agent_id') == agent_id]
        except Exception as e:
            print(f"Error loading test results: {e}")
            return []


# Database Storage Backend
class DatabaseStorageBackend(StorageBackend):
    """SQLAlchemy-based database storage"""
    
    def __init__(self):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for database backend")
        
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        print(f"✅ Database connected: {Config.DATABASE_URL}")
    
    def save_agents(self, agents: Dict) -> bool:
        """Save agents data structure to database"""
        session = self.Session()
        try:
            # Clear existing and insert new
            for agent_id, agent_data in agents.get('custom_agents', {}).items():
                existing = session.query(AgentModel).filter_by(id=agent_id).first()
                if existing:
                    for key, value in agent_data.items():
                        setattr(existing, key, value)
                else:
                    agent_model = AgentModel(**agent_data)
                    session.add(agent_model)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving agents to database: {e}")
            return False
        finally:
            session.close()
    
    def load_agents(self) -> Dict:
        """Load agents from database into the expected dict structure"""
        session = self.Session()
        try:
            agents = session.query(AgentModel).all()
            
            custom_agents = {}
            published_agents = {}
            marketplace = []
            
            for agent in agents:
                agent_dict = agent.to_dict()
                custom_agents[agent.id] = agent_dict
                
                if agent.published:
                    published_agents[agent.id] = agent_dict
                    marketplace.append({
                        "id": agent.id,
                        "name": agent.name,
                        "role": agent.role,
                        "description": agent.description,
                        "created_by": agent.created_by,
                        "published_at": agent.published_at,
                        "version": agent.version,
                        "tags": agent.tags or [],
                        "downloads": 0,
                        "rating": 0,
                        "reviews": []
                    })
            
            return {
                "custom_agents": custom_agents,
                "published_agents": published_agents,
                "agent_marketplace": marketplace
            }
        except Exception as e:
            print(f"Error loading agents from database: {e}")
            return {}
        finally:
            session.close()
    
    def save_tools(self, tools: Dict) -> bool:
        session = self.Session()
        try:
            for tool_id, tool_data in tools.items():
                existing = session.query(ToolModel).filter_by(id=tool_id).first()
                if existing:
                    for key, value in tool_data.items():
                        setattr(existing, key, value)
                else:
                    tool_model = ToolModel(**tool_data)
                    session.add(tool_model)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving tools to database: {e}")
            return False
        finally:
            session.close()
    
    def load_tools(self) -> Dict:
        session = self.Session()
        try:
            tools = session.query(ToolModel).all()
            return {tool.id: tool.to_dict() for tool in tools}
        except Exception as e:
            print(f"Error loading tools from database: {e}")
            return {}
        finally:
            session.close()
    
    def save_analytics(self, analytics_entry: Dict) -> bool:
        session = self.Session()
        try:
            analytics_model = AnalyticsModel(**analytics_entry)
            session.add(analytics_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving analytics: {e}")
            return False
        finally:
            session.close()
    
    def load_analytics(self, agent_id: str = None) -> List[Dict]:
        session = self.Session()
        try:
            query = session.query(AnalyticsModel)
            if agent_id:
                query = query.filter_by(agent_id=agent_id)
            
            analytics = query.all()
            return [a.to_dict() for a in analytics]
        except Exception as e:
            print(f"Error loading analytics: {e}")
            return []
        finally:
            session.close()
    
    def save_test_result(self, test_result: Dict) -> bool:
        session = self.Session()
        try:
            test_model = TestResultModel(**test_result)
            session.add(test_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving test result: {e}")
            return False
        finally:
            session.close()
    
    def load_test_results(self, agent_id: str) -> List[Dict]:
        session = self.Session()
        try:
            tests = session.query(TestResultModel).filter_by(agent_id=agent_id).all()
            return [t.to_dict() for t in tests]
        except Exception as e:
            print(f"Error loading test results: {e}")
            return []
        finally:
            session.close()


# Storage Factory
def get_storage_backend() -> StorageBackend:
    """Get the configured storage backend"""
    backend_type = Config.get_storage_backend()
    
    if backend_type == 'database':
        if not SQLALCHEMY_AVAILABLE:
            print("⚠️  Database backend not available, falling back to JSON")
            return JSONStorageBackend()
        return DatabaseStorageBackend()
    else:
        return JSONStorageBackend()