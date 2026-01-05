"""
analytics.py - Agent Analytics and Monitoring System
"""

from datetime import datetime
from typing import Dict, List
from store.storage_backends import get_storage_backend
from store.config import Config
import time

class AgentAnalytics:
    """Track and analyze agent performance"""
    
    def __init__(self):
        self.storage = get_storage_backend()
        self.enabled = Config.ENABLE_ANALYTICS
    
    def log_execution(self, agent_id: str, success: bool, response_time_ms: int, 
                     tools_used: List[str] = None, error_message: str = None,
                     user_id: str = "default_user"):
        """Log an agent execution"""
        if not self.enabled:
            return
        
        analytics_entry = {
            "agent_id": agent_id,
            "execution_time": datetime.now().isoformat(),
            "success": success,
            "error_message": error_message,
            "tools_used": tools_used or [],
            "response_time_ms": response_time_ms,
            "user_id": user_id
        }
        
        self.storage.save_analytics(analytics_entry)
    
    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get comprehensive stats for an agent"""
        analytics = self.storage.load_analytics(agent_id)
        
        if not analytics:
            return {
                "agent_id": agent_id,
                "total_executions": 0,
                "success_rate": 0,
                "avg_response_time_ms": 0,
                "total_errors": 0,
                "most_used_tools": [],
                "executions_by_day": {},
                "recent_errors": []
            }
        
        total = len(analytics)
        successful = sum(1 for a in analytics if a['success'])
        response_times = [a['response_time_ms'] for a in analytics if a.get('response_time_ms')]
        
        # Tool usage frequency
        tool_usage = {}
        for entry in analytics:
            for tool in entry.get('tools_used', []):
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        most_used_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Executions by day
        executions_by_day = {}
        for entry in analytics:
            day = entry['execution_time'].split('T')[0]
            executions_by_day[day] = executions_by_day.get(day, 0) + 1
        
        # Recent errors
        recent_errors = [
            {
                "time": a['execution_time'],
                "error": a['error_message']
            }
            for a in analytics if not a['success'] and a.get('error_message')
        ][-10:]  # Last 10 errors
        
        return {
            "agent_id": agent_id,
            "total_executions": total,
            "success_rate": round((successful / total * 100), 2) if total > 0 else 0,
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2) if response_times else 0,
            "total_errors": total - successful,
            "most_used_tools": [{"tool": tool, "count": count} for tool, count in most_used_tools],
            "executions_by_day": executions_by_day,
            "recent_errors": recent_errors
        }
    
    def get_all_stats(self) -> List[Dict]:
        """Get stats for all agents"""
        analytics = self.storage.load_analytics()
        
        # Group by agent_id
        agents = {}
        for entry in analytics:
            agent_id = entry['agent_id']
            if agent_id not in agents:
                agents[agent_id] = []
            agents[agent_id].append(entry)
        
        # Get stats for each agent
        all_stats = []
        for agent_id in agents:
            stats = self.get_agent_stats(agent_id)
            all_stats.append(stats)
        
        return sorted(all_stats, key=lambda x: x['total_executions'], reverse=True)
    
    def clear_analytics(self, agent_id: str = None):
        """Clear analytics data (use with caution)"""
        # For JSON backend, we'd need to rewrite the file
        # For database backend, we'd delete records
        # This is a placeholder - implement based on your needs
        pass


# Context manager for tracking execution time
class ExecutionTimer:
    """Context manager to track execution time and log analytics"""
    
    def __init__(self, analytics: AgentAnalytics, agent_id: str, user_id: str = "default_user"):
        self.analytics = analytics
        self.agent_id = agent_id
        self.user_id = user_id
        self.start_time = None
        self.tools_used = []
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        response_time_ms = int((time.time() - self.start_time) * 1000)
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        self.analytics.log_execution(
            agent_id=self.agent_id,
            success=success,
            response_time_ms=response_time_ms,
            tools_used=self.tools_used,
            error_message=error_message,
            user_id=self.user_id
        )
        
        # Don't suppress exceptions
        return False
    
    def add_tool_used(self, tool_name: str):
        """Track a tool usage during execution"""
        self.tools_used.append(tool_name)


# Initialize global analytics instance
agent_analytics = AgentAnalytics()