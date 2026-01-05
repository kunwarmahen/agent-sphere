"""
testing.py - Agent Testing & Validation Framework
"""

from datetime import datetime
from typing import Dict, List
import time
import requests
from store.storage_backends import get_storage_backend
from store.config import Config
import logging

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:5000/api"


class TestCase:
    """Represents a single test case for an agent"""
    
    def __init__(self, name: str, input_message: str, expected_output: str = None, 
                 validation_func=None, timeout: int = 30):
        self.name = name
        self.input_message = input_message
        self.expected_output = expected_output
        self.validation_func = validation_func  # Custom validation function
        self.timeout = timeout
    
    def to_dict(self):
        return {
            "name": self.name,
            "input_message": self.input_message,
            "expected_output": self.expected_output,
            "timeout": self.timeout
        }


class TestSuite:
    """Collection of test cases for an agent"""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.test_cases = []
    
    def add_test(self, test_case: TestCase):
        """Add a test case to the suite"""
        self.test_cases.append(test_case)
    
    def add_quick_test(self, name: str, input_message: str, expected_contains: str = None):
        """Quick way to add a simple test"""
        validation = None
        if expected_contains:
            validation = lambda response: expected_contains.lower() in response.lower()
        
        test = TestCase(
            name=name,
            input_message=input_message,
            expected_output=expected_contains,
            validation_func=validation
        )
        self.add_test(test)
    
    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "test_count": len(self.test_cases),
            "tests": [tc.to_dict() for tc in self.test_cases]
        }


class AgentTester:
    """Test runner for agents"""
    
    def __init__(self):
        self.storage = get_storage_backend()
        self.enabled = Config.ENABLE_TESTING
        self.test_suites = {}  # agent_id -> TestSuite
    
    def create_test_suite(self, agent_id: str, agent_name: str) -> TestSuite:
        """Create a new test suite for an agent"""
        suite = TestSuite(agent_id, agent_name)
        self.test_suites[agent_id] = suite
        return suite
    
    def get_test_suite(self, agent_id: str) -> TestSuite:
        """Get existing test suite or create new one"""
        if agent_id not in self.test_suites:
            return self.create_test_suite(agent_id, f"Agent {agent_id}")
        return self.test_suites[agent_id]
    
    def run_test(self, agent_id: str, test_case: TestCase, agent_type: str = "custom") -> Dict:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            # Call the agent
            if agent_type == "custom":
                endpoint = f"{API_BASE_URL}/agents/custom/{agent_id}/chat"
            else:
                endpoint = f"{API_BASE_URL}/agents/{agent_id}/chat"
            
            response = requests.post(
                endpoint,
                json={"message": test_case.input_message},
                timeout=test_case.timeout
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code != 200:
                return {
                    "test_name": test_case.name,
                    "passed": False,
                    "error_message": f"HTTP {response.status_code}: {response.text}",
                    "response_time_ms": response_time_ms,
                    "actual_output": None
                }
            
            data = response.json()
            actual_output = data.get('response', '')
            
            # Validate the response
            passed = True
            error_message = None
            
            if test_case.validation_func:
                try:
                    passed = test_case.validation_func(actual_output)
                    if not passed:
                        error_message = "Custom validation failed"
                except Exception as e:
                    passed = False
                    error_message = f"Validation error: {str(e)}"
            elif test_case.expected_output:
                # Simple substring check
                passed = test_case.expected_output.lower() in actual_output.lower()
                if not passed:
                    error_message = f"Expected '{test_case.expected_output}' not found in response"
            
            return {
                "test_name": test_case.name,
                "passed": passed,
                "error_message": error_message,
                "response_time_ms": response_time_ms,
                "actual_output": actual_output[:500],  # Truncate for storage
                "expected_output": test_case.expected_output
            }
        
        except requests.Timeout:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "test_name": test_case.name,
                "passed": False,
                "error_message": f"Timeout after {test_case.timeout}s",
                "response_time_ms": response_time_ms,
                "actual_output": None,
                "expected_output": test_case.expected_output
            }
        
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "test_name": test_case.name,
                "passed": False,
                "error_message": str(e),
                "response_time_ms": response_time_ms,
                "actual_output": None,
                "expected_output": test_case.expected_output
            }
    
    def run_test_suite(self, agent_id: str, agent_type: str = "custom") -> Dict:
        """Run all tests in a suite"""
        if agent_id not in self.test_suites:
            return {
                "success": False,
                "error": "No test suite found for this agent"
            }
        
        suite = self.test_suites[agent_id]
        results = []
        
        logger.info(f"Running {len(suite.test_cases)} tests for agent {agent_id}")
        
        for test_case in suite.test_cases:
            result = self.run_test(agent_id, test_case, agent_type)
            
            # Save result to storage
            if self.enabled:
                test_result = {
                    "agent_id": agent_id,
                    "test_name": result["test_name"],
                    "test_input": {"message": test_case.input_message},
                    "expected_output": result.get("expected_output"),
                    "actual_output": result.get("actual_output"),
                    "passed": result["passed"],
                    "error_message": result.get("error_message"),
                    "execution_time": datetime.now().isoformat(),
                    "response_time_ms": result["response_time_ms"]
                }
                self.storage.save_test_result(test_result)
            
            results.append(result)
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["passed"])
        failed_tests = total_tests - passed_tests
        avg_response_time = sum(r["response_time_ms"] for r in results) / total_tests if total_tests > 0 else 0
        
        return {
            "success": True,
            "agent_id": agent_id,
            "agent_name": suite.agent_name,
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "test_results": results,
            "executed_at": datetime.now().isoformat()
        }
    
    def get_test_history(self, agent_id: str) -> List[Dict]:
        """Get historical test results for an agent"""
        return self.storage.load_test_results(agent_id)
    
    def get_test_summary(self, agent_id: str) -> Dict:
        """Get summary of all test runs"""
        history = self.get_test_history(agent_id)
        
        if not history:
            return {
                "agent_id": agent_id,
                "total_test_runs": 0,
                "total_tests": 0,
                "overall_pass_rate": 0,
                "recent_runs": []
            }
        
        total_runs = len(history)
        total_tests = len(history)
        passed_tests = sum(1 for h in history if h.get("passed"))
        
        # Group by execution time to get runs
        runs_by_time = {}
        for test in history:
            exec_time = test.get("execution_time", "").split("T")[0]  # Group by day
            if exec_time not in runs_by_time:
                runs_by_time[exec_time] = []
            runs_by_time[exec_time].append(test)
        
        recent_runs = []
        for exec_time in sorted(runs_by_time.keys(), reverse=True)[:10]:
            tests = runs_by_time[exec_time]
            passed = sum(1 for t in tests if t.get("passed"))
            recent_runs.append({
                "date": exec_time,
                "total": len(tests),
                "passed": passed,
                "failed": len(tests) - passed
            })
        
        return {
            "agent_id": agent_id,
            "total_test_runs": len(runs_by_time),
            "total_tests": total_tests,
            "overall_pass_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0,
            "recent_runs": recent_runs
        }


# Initialize global tester instance
agent_tester = AgentTester()