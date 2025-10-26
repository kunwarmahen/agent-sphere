"""
Financial Planning Agent - Manage budgets, investments, and financial goals
"""
import json
from base.agent_framework import Agent, Tool
from datetime import datetime, timedelta


class FinancialPlanner:
    """Manages financial accounts, transactions, budgets, and investments"""
    def __init__(self):
        self.accounts = {
            "checking": 5000.00,
            "savings": 15000.00,
            "investment": 25000.00,
            "crypto": 3500.00
        }
        
        self.transactions = [
            {"date": "2025-01-18", "amount": -50.00, "category": "groceries", "description": "Whole Foods"},
            {"date": "2025-01-18", "amount": -150.00, "category": "utilities", "description": "Electric bill"},
            {"date": "2025-01-17", "amount": -35.00, "category": "entertainment", "description": "Movie tickets"},
            {"date": "2025-01-17", "amount": -20.00, "category": "groceries", "description": "Target"},
            {"date": "2025-01-16", "amount": 3500.00, "category": "income", "description": "Monthly salary"},
            {"date": "2025-01-15", "amount": -200.00, "category": "dining", "description": "Restaurant"},
            {"date": "2025-01-14", "amount": -100.00, "category": "transport", "description": "Gas"},
        ]
        
        self.budget = {
            "groceries": 500.00,
            "utilities": 300.00,
            "entertainment": 200.00,
            "dining": 300.00,
            "transport": 200.00,
            "health": 150.00
        }
        
        self.investments = [
            {"symbol": "AAPL", "shares": 10, "purchase_price": 150.00, "current_price": 195.00},
            {"symbol": "GOOGL", "shares": 5, "purchase_price": 100.00, "current_price": 140.00},
            {"symbol": "MSFT", "shares": 8, "purchase_price": 300.00, "current_price": 380.00},
        ]
        
        self.financial_goals = [
            {"name": "Emergency Fund", "target": 20000, "current": 15000, "deadline": "2025-06-30"},
            {"name": "Vacation", "target": 5000, "current": 2000, "deadline": "2025-08-31"},
            {"name": "New Car", "target": 30000, "current": 8500, "deadline": "2026-12-31"},
        ]
        
        self.recurring_expenses = [
            {"name": "Netflix", "amount": 15.99, "frequency": "monthly"},
            {"name": "Gym", "amount": 50.00, "frequency": "monthly"},
            {"name": "Insurance", "amount": 120.00, "frequency": "monthly"},
        ]
        
        self.alerts = []
    
    def get_account_balance(self, account: str) -> str:
        """Get single account balance"""
        if account not in self.accounts:
            return f"Account '{account}' not found. Available: {list(self.accounts.keys())}"
        return f"{account.title()}: ${self.accounts[account]:,.2f}"
    
    def get_all_balances(self) -> str:
        """Get all account balances and net worth"""
        total = sum(self.accounts.values())
        return json.dumps({
            "accounts": {k: f"${v:,.2f}" for k, v in self.accounts.items()},
            "total_net_worth": f"${total:,.2f}"
        })
    
    def record_transaction(self, amount: float, category: str, description: str = "") -> str:
        """Record a new transaction"""
        if category not in self.budget and category != "income":
            return f"Category '{category}' not found. Available: {list(self.budget.keys())}"
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.transactions.append({
            "date": today,
            "amount": amount,
            "category": category,
            "description": description
        })
        
        # Update checking account
        self.accounts["checking"] += amount
        
        return f"Transaction recorded: ${amount:+.2f} for {category} - {description}"
    
    def get_spending_analysis(self, days: int = 30) -> str:
        """Analyze spending by category"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        recent_txns = [t for t in self.transactions if t["date"] >= cutoff_str and t["amount"] < 0]
        
        by_category = {}
        for tx in recent_txns:
            cat = tx["category"]
            by_category[cat] = by_category.get(cat, 0) + abs(tx["amount"])
        
        analysis = []
        for cat in sorted(by_category.keys()):
            spent = by_category[cat]
            budget = self.budget.get(cat, 0)
            pct = (spent / budget * 100) if budget > 0 else 0
            status = "✓ OK" if spent <= budget else "⚠ OVER"
            analysis.append({
                "category": cat,
                "spent": f"${spent:.2f}",
                "budget": f"${budget:.2f}",
                "percentage": f"{pct:.1f}%",
                "status": status
            })
        
        return json.dumps({"last_days": days, "categories": analysis})
    
    def get_investment_portfolio(self) -> str:
        """Get investment portfolio summary"""
        total_value = 0
        total_cost = 0
        holdings = []
        
        for inv in self.investments:
            current_val = inv["shares"] * inv["current_price"]
            cost_basis = inv["shares"] * inv["purchase_price"]
            gain = current_val - cost_basis
            gain_pct = (gain / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_val
            total_cost += cost_basis
            
            holdings.append({
                "symbol": inv["symbol"],
                "shares": inv["shares"],
                "current_price": f"${inv['current_price']:.2f}",
                "current_value": f"${current_val:.2f}",
                "cost_basis": f"${cost_basis:.2f}",
                "gain_loss": f"${gain:+.2f}",
                "gain_loss_pct": f"{gain_pct:+.2f}%"
            })
        
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
        
        return json.dumps({
            "holdings": holdings,
            "portfolio_value": f"${total_value:.2f}",
            "total_cost_basis": f"${total_cost:.2f}",
            "total_gain_loss": f"${total_gain:+.2f}",
            "total_return_pct": f"{total_gain_pct:+.2f}%"
        })
    
    def buy_investment(self, symbol: str, shares: int, price: float) -> str:
        """Record investment purchase"""
        cost = shares * price
        if self.accounts["investment"] < cost:
            return f"Insufficient funds. Available: ${self.accounts['investment']:,.2f}, Required: ${cost:,.2f}"
        
        # Check if already owned
        for inv in self.investments:
            if inv["symbol"] == symbol:
                inv["shares"] += shares
                self.accounts["investment"] -= cost
                return f"Purchased {shares} shares of {symbol} at ${price:.2f}/share (Total: ${cost:,.2f})"
        
        # New investment
        self.investments.append({
            "symbol": symbol,
            "shares": shares,
            "purchase_price": price,
            "current_price": price
        })
        self.accounts["investment"] -= cost
        
        return f"Purchased {shares} shares of {symbol} at ${price:.2f}/share (Total: ${cost:,.2f})"
    
    def get_financial_goals(self) -> str:
        """Get all financial goals progress"""
        goals_status = []
        for goal in self.financial_goals:
            progress_pct = (goal["current"] / goal["target"] * 100) if goal["target"] > 0 else 0
            remaining = goal["target"] - goal["current"]
            
            goals_status.append({
                "name": goal["name"],
                "target": f"${goal['target']:,.2f}",
                "current": f"${goal['current']:,.2f}",
                "remaining": f"${remaining:,.2f}",
                "progress": f"{progress_pct:.1f}%",
                "deadline": goal["deadline"]
            })
        
        return json.dumps(goals_status)
    
    def add_to_goal(self, goal_name: str, amount: float) -> str:
        """Add funds to a financial goal"""
        for goal in self.financial_goals:
            if goal["name"].lower() == goal_name.lower():
                goal["current"] += amount
                self.accounts["savings"] -= amount
                remaining = goal["target"] - goal["current"]
                return f"Added ${amount:,.2f} to '{goal_name}'. Remaining: ${remaining:,.2f}"
        
        return f"Goal '{goal_name}' not found"
    
    def get_recurring_expenses(self) -> str:
        """Get recurring expense summary"""
        monthly_total = sum(exp["amount"] for exp in self.recurring_expenses if exp["frequency"] == "monthly")
        
        return json.dumps({
            "recurring_expenses": self.recurring_expenses,
            "monthly_total": f"${monthly_total:,.2f}",
            "annual_total": f"${monthly_total * 12:,.2f}"
        })
    
    def project_savings(self, monthly_savings: float, months: int = 12) -> str:
        """Project savings growth"""
        current = self.accounts["savings"]
        projected = current + (monthly_savings * months)
        
        return json.dumps({
            "current_savings": f"${current:,.2f}",
            "monthly_contribution": f"${monthly_savings:,.2f}",
            "months": months,
            "projected_total": f"${projected:,.2f}",
            "total_contributed": f"${monthly_savings * months:,.2f}"
        })
    
    def get_financial_summary(self) -> str:
        """Get complete financial summary"""
        total_net_worth = sum(self.accounts.values())
        
        # Calculate monthly spending
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        monthly_spending = sum(abs(t["amount"]) for t in self.transactions 
                             if t["date"] >= month_ago and t["amount"] < 0)
        
        return json.dumps({
            "net_worth": f"${total_net_worth:,.2f}",
            "liquid_assets": f"${sum([self.accounts['checking'], self.accounts['savings']]):,.2f}",
            "investments": f"${sum([self.accounts['investment'], self.accounts['crypto']]):,.2f}",
            "monthly_spending": f"${monthly_spending:,.2f}",
            "active_goals": len([g for g in self.financial_goals if g["current"] < g["target"]]),
            "recurring_expenses": f"${sum(exp['amount'] for exp in self.recurring_expenses if exp['frequency'] == 'monthly'):,.2f}/month"
        })


# Initialize planner
planner = FinancialPlanner()

# Create tools
finance_tools = [
    Tool("get_account_balance",
         "Get balance of a specific account",
         planner.get_account_balance,
         {"account": "str (checking/savings/investment/crypto)"}),
    
    Tool("get_all_balances",
         "Get all account balances and total net worth",
         planner.get_all_balances,
         {}),
    
    Tool("record_transaction",
         "Record a new income or expense transaction",
         planner.record_transaction,
         {"amount": "float", "category": "str", "description": "str (optional)"}),
    
    Tool("get_spending_analysis",
         "Analyze spending by category",
         planner.get_spending_analysis,
         {"days": "int (optional, default 30)"}),
    
    Tool("get_investment_portfolio",
         "Get investment portfolio summary and gains/losses",
         planner.get_investment_portfolio,
         {}),
    
    Tool("buy_investment",
         "Record investment purchase",
         planner.buy_investment,
         {"symbol": "str", "shares": "int", "price": "float"}),
    
    Tool("get_financial_goals",
         "Get all financial goals and progress",
         planner.get_financial_goals,
         {}),
    
    Tool("add_to_goal",
         "Add funds to a financial goal",
         planner.add_to_goal,
         {"goal_name": "str", "amount": "float"}),
    
    Tool("get_recurring_expenses",
         "Get all recurring expenses",
         planner.get_recurring_expenses,
         {}),
    
    Tool("project_savings",
         "Project future savings with monthly contributions",
         planner.project_savings,
         {"monthly_savings": "float", "months": "int (optional)"}),
    
    Tool("get_financial_summary",
         "Get complete financial overview",
         planner.get_financial_summary,
         {}),
]

# Create agent
finance_agent = Agent(
    name="FinanceBot",
    role="Personal Financial Planning Assistant",
    tools=finance_tools,
    system_instructions="You are a financial planning assistant. Help users manage their money, track spending, and achieve financial goals. Always provide clear financial advice and summaries."
)


if __name__ == "__main__":
    # Test financial agent
    print("=" * 70)
    print("FINANCIAL PLANNING AGENT - Interactive Demo")
    print("=" * 70)
    
    test_requests = [
        "What's my financial summary?",
        "Show me my spending analysis for the last month",
        "What's my investment portfolio performance?",
        "How much progress have I made on my financial goals?",
        "If I save $500 monthly, where will I be in a year?",
        "I just spent $75 on groceries at Trader Joe's"
    ]
    
    for request in test_requests:
        print(f"\nUser: {request}")
        print("-" * 70)
        result = finance_agent.think_and_act(request, verbose=False)
        print(f"Agent: {result}\n")
        finance_agent.clear_memory()