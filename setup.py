#!/usr/bin/env python3
"""
🚀 Eth-Ecosystem Agent Setup Script
===================================

Quick setup script for the Recall hackathon project.
This script helps you configure and run the Eth-Ecosystem agent.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 ETH-ECOSYSTEM AGENT SETUP")
    print("=" * 60)
    print("Recall Hackathon Project")
    print("Intelligent Ethereum Ecosystem Trading Agent")
    print("Advanced DeFi Portfolio Management")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file with API keys."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔧 Creating .env file...")
    
    env_content = """# Eth-Ecosystem Agent Configuration
# Recall API (Required)
RECALL_API_KEY=your_recall_api_key_here

# CoinGecko API (Optional - for enhanced data)
PRODUCTION_API_KEY=your_coingecko_production_key_here
SANDBOX_API_KEY=your_coingecko_sandbox_key_here

# Trading Configuration
TRADING_MODE=moderate  # conservative, moderate, aggressive
REBALANCE_FREQUENCY=daily  # hourly, daily, weekly
STOP_LOSS_ENABLED=true
DRIFT_THRESHOLD=0.03  # 3% drift threshold
MAX_SLIPPAGE=0.05     # 5% max slippage
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update RECALL_API_KEY with your actual API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_portfolio_config():
    """Create default portfolio configuration."""
    config_file = Path("eth_portfolio_config.json")
    
    if config_file.exists():
        print("✅ Portfolio config already exists")
        return True
    
    print("📋 Creating default DeFi portfolio configuration...")
    
    config = {
        "ETH": 0.30,      # 30% Ethereum (core)
        "USDC": 0.15,     # 15% USDC (stable)
        "UNI": 0.12,      # 12% Uniswap (DEX)
        "LINK": 0.10,     # 10% Chainlink (oracle)
        "AAVE": 0.08,     # 8% Aave (lending)
        "COMP": 0.06,     # 6% Compound (lending)
        "MKR": 0.05,      # 5% Maker (stablecoin)
        "SNX": 0.04,      # 4% Synthetix (synthetics)
        "YFI": 0.03,      # 3% Yearn (yield)
        "CRV": 0.03,      # 3% Curve (stable swaps)
        "BAL": 0.02,      # 2% Balancer (AMM)
        "SUSHI": 0.02     # 2% SushiSwap (DEX)
    }
    
    try:
        import json
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Portfolio configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create portfolio config: {e}")
        return False

def create_stop_loss_config():
    """Create stop-loss configuration."""
    config_file = Path("stop_loss_config.json")
    
    if config_file.exists():
        print("✅ Stop-loss config already exists")
        return True
    
    print("🛡️  Creating stop-loss configuration...")
    
    config = {
        "enabled": True,
        "check_interval": 300,
        "default_stop_loss": 0.15,
        "trailing_stop": 0.10,
        "emergency_stop": 0.25,
        "token_stop_loss": {
            "ETH": 0.12,
            "USDC": 0.05,
            "USDT": 0.05,
            "UNI": 0.18,
            "LINK": 0.18,
            "AAVE": 0.20,
            "COMP": 0.20,
            "MKR": 0.18,
            "SNX": 0.22,
            "YFI": 0.25,
            "CRV": 0.20,
            "BAL": 0.20,
            "SUSHI": 0.22,
            "1INCH": 0.22,
            "REN": 0.25,
            "ZRX": 0.20
        },
        "max_portfolio_loss": 0.20,
        "enable_trailing_stops": True,
        "enable_emergency_stops": True
    }
    
    try:
        import json
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Stop-loss configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create stop-loss config: {e}")
        return False

def create_gitignore():
    """Create .gitignore file."""
    gitignore_file = Path(".gitignore")
    
    if gitignore_file.exists():
        print("✅ .gitignore already exists")
        return True
    
    print("🚫 Creating .gitignore file...")
    
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
.venv/
venv/
ENV/

# Logs
*.log
trade_log.json
stop_loss_log.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Configuration files with sensitive data
eth_portfolio_config.json
stop_loss_config.json
"""
    
    try:
        with open(gitignore_file, "w") as f:
            f.write(gitignore_content)
        print("✅ .gitignore file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .gitignore: {e}")
        return False

def test_recall_connection():
    """Test Recall API connection."""
    print("🔗 Testing Recall API connection...")
    
    # Check if .env exists and has API key
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found, skipping connection test")
        return True
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("RECALL_API_KEY")
        if not api_key or api_key == "your_recall_api_key_here":
            print("⚠️  RECALL_API_KEY not set, skipping connection test")
            return True
        
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        r = requests.get(
            "https://api.sandbox.competitions.recall.network/api/balance",
            headers=headers,
            timeout=10
        )
        
        if r.ok:
            print("✅ Recall API connection successful")
            return True
        else:
            print(f"⚠️  Recall API connection failed: {r.status_code}")
            return True  # Don't fail setup for this
            
    except Exception as e:
        print(f"⚠️  Recall API test failed: {e}")
        return True  # Don't fail setup for this

def run_demo():
    """Run the demo to test the setup."""
    print("🎮 Running demo to test setup...")
    try:
        subprocess.check_call([sys.executable, "eth_ecosystem_demo.py"])
        return True
    except subprocess.CalledProcessError:
        print("❌ Demo failed to run")
        return False
    except FileNotFoundError:
        print("⚠️  Demo script not found, skipping demo")
        return True

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. 🔑 Update your RECALL_API_KEY in the .env file")
    print("2. 🚀 Run the main agent: python trading_agent.py")
    print("3. 🎮 Run the demo: python eth_ecosystem_demo.py")
    print("4. 📊 Monitor performance in the generated log files")
    print()
    print("Available Commands:")
    print("   • python trading_agent.py           # Main trading agent")
    print("   • python eth_tokens.py              # Token discovery")
    print("   • python token_analyzer.py          # Performance analysis")
    print("   • python portfolio_manager.py       # Portfolio management")
    print("   • python stop_loss_manager.py       # Stop-loss management")
    print("   • python eth_ecosystem_demo.py      # Feature demo")
    print()
    print("📚 Documentation: README.md")
    print("🐛 Issues: Check the log files for errors")
    print()
    print("🚀 Ready to dominate the Ethereum DeFi ecosystem!")
    print("=" * 60)

def show_configuration_info():
    """Show configuration information."""
    print("\n📋 Configuration Files Created:")
    print("   • .env                    - Environment variables & API keys")
    print("   • eth_portfolio_config.json - Portfolio allocation weights")
    print("   • stop_loss_config.json   - Stop-loss settings")
    print("   • .gitignore              - Git ignore rules")
    print()
    print("🔧 Key Configuration Options:")
    print("   • DRIFT_THRESHOLD: 3%     - Rebalancing trigger")
    print("   • MAX_SLIPPAGE: 5%        - Maximum trade slippage")
    print("   • REBALANCE_FREQUENCY: Daily")
    print("   • STOP_LOSS_ENABLED: True")
    print()
    print("🛡️  Risk Management:")
    print("   • Token-specific stop-loss levels")
    print("   • Portfolio-level risk limits")
    print("   • Trailing stop-loss protection")
    print("   • Emergency stop-loss triggers")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    print()
    
    # Create .env file
    if not create_env_file():
        return False
    
    print()
    
    # Create portfolio config
    if not create_portfolio_config():
        return False
    
    print()
    
    # Create stop-loss config
    if not create_stop_loss_config():
        return False
    
    print()
    
    # Create .gitignore
    if not create_gitignore():
        return False
    
    print()
    
    # Test Recall connection
    test_recall_connection()
    
    print()
    
    # Show configuration info
    show_configuration_info()
    
    print()
    
    # Run demo (optional)
    demo_choice = input("🎮 Run demo to test setup? (y/n): ").lower().strip()
    if demo_choice in ['y', 'yes']:
        run_demo()
    
    print()
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1) 