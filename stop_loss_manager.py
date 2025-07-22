import os, json, time, requests, schedule
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

load_dotenv()

# ------------------------------------------------------------
#  Configuration
# ------------------------------------------------------------
RECALL_KEY = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Stop-loss configuration
DEFAULT_STOP_LOSS = 0.15  # 15% default stop-loss
TRAILING_STOP = 0.10      # 10% trailing stop-loss
EMERGENCY_STOP = 0.25     # 25% emergency stop-loss
CHECK_INTERVAL = 300      # Check every 5 minutes

# Token-specific stop-loss levels (can be overridden)
TOKEN_STOP_LOSS = {
    "ETH": 0.12,      # Lower for ETH (more stable)
    "USDC": 0.05,     # Very low for stablecoins
    "USDT": 0.05,     # Very low for stablecoins
    "UNI": 0.18,      # Higher for DeFi tokens
    "LINK": 0.18,     # Higher for DeFi tokens
    "AAVE": 0.20,     # Higher for DeFi tokens
    "COMP": 0.20,     # Higher for DeFi tokens
    "MKR": 0.18,      # Higher for DeFi tokens
    "SNX": 0.22,      # Higher for more volatile tokens
    "YFI": 0.25,      # Higher for more volatile tokens
    "CRV": 0.20,      # Higher for DeFi tokens
    "BAL": 0.20,      # Higher for DeFi tokens
    "SUSHI": 0.22,    # Higher for more volatile tokens
    "1INCH": 0.22,    # Higher for more volatile tokens
    "REN": 0.25,      # Higher for more volatile tokens
    "ZRX": 0.20,      # Higher for DeFi tokens
}

# Token addresses and decimals (same as portfolio_manager.py)
TOKEN_MAP = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    "SNX": "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",
    "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",
    "SUSHI": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
    "1INCH": "0x111111111117dC0aa78b770fA6A738034120C302",
    "REN": "0x408e41876cCcDC0F92210600ef50372656052a38",
    "ZRX": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
}

DECIMALS = {
    "ETH": 18, "USDC": 6, "USDT": 6, "UNI": 18, "LINK": 18, "AAVE": 18,
    "COMP": 18, "MKR": 18, "SNX": 18, "YFI": 18, "CRV": 18, "BAL": 18,
    "SUSHI": 18, "1INCH": 18, "REN": 18, "ZRX": 18
}

COINGECKO_IDS = {
    "ETH": "ethereum", "USDC": "usd-coin", "USDT": "tether",
    "UNI": "uniswap", "LINK": "chainlink", "AAVE": "aave",
    "COMP": "compound-governance-token", "MKR": "maker",
    "SNX": "havven", "YFI": "yearn-finance", "CRV": "curve-dao-token",
    "BAL": "balancer", "SUSHI": "sushi", "1INCH": "1inch",
    "REN": "republic-protocol", "ZRX": "0x",
}

class StopLossManager:
    def __init__(self):
        self.session = requests.Session()
        self.entry_prices = {}  # Track entry prices for each position
        self.highest_prices = {}  # Track highest prices for trailing stops
        self.stop_loss_history = []
        
    def load_stop_loss_config(self) -> Dict:
        """Load stop-loss configuration from file."""
        try:
            with open("stop_loss_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            config = {
                "enabled": True,
                "check_interval": CHECK_INTERVAL,
                "default_stop_loss": DEFAULT_STOP_LOSS,
                "trailing_stop": TRAILING_STOP,
                "emergency_stop": EMERGENCY_STOP,
                "token_stop_loss": TOKEN_STOP_LOSS,
                "max_portfolio_loss": 0.20,  # 20% max portfolio loss
                "enable_trailing_stops": True,
                "enable_emergency_stops": True
            }
            self.save_stop_loss_config(config)
            return config
    
    def save_stop_loss_config(self, config: Dict):
        """Save stop-loss configuration to file."""
        with open("stop_loss_config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    def fetch_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current prices from CoinGecko."""
        ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
        
        params = {"ids": ids, "vs_currencies": "usd"}
        if COINGECKO_KEY:
            params['x_cg_demo_api_key'] = COINGECKO_KEY
        
        try:
            r = self.session.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            
            prices = {}
            for sym in symbols:
                if sym in COINGECKO_IDS and COINGECKO_IDS[sym] in data:
                    prices[sym] = data[COINGECKO_IDS[sym]]["usd"]
                else:
                    print(f"⚠️  Warning: No price data for {sym}")
                    prices[sym] = 0.0
            
            return prices
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            return {}
    
    def fetch_holdings(self) -> Dict[str, float]:
        """Fetch current holdings from Recall sandbox."""
        try:
            r = self.session.get(
                f"{SANDBOX_API}/api/balance",
                headers={"Authorization": f"Bearer {RECALL_KEY}"},
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"❌ Error fetching holdings: {e}")
            return {}
    
    def initialize_entry_prices(self, holdings: Dict[str, float], prices: Dict[str, float]):
        """Initialize entry prices for positions that don't have them."""
        for symbol, amount in holdings.items():
            if amount > 0 and symbol in prices and symbol not in self.entry_prices:
                self.entry_prices[symbol] = prices[symbol]
                self.highest_prices[symbol] = prices[symbol]
                print(f"📊 Initialized entry price for {symbol}: ${prices[symbol]:.6f}")
    
    def update_highest_prices(self, prices: Dict[str, float]):
        """Update highest prices for trailing stop-loss calculation."""
        for symbol, current_price in prices.items():
            if symbol in self.highest_prices:
                if current_price > self.highest_prices[symbol]:
                    self.highest_prices[symbol] = current_price
                    print(f"📈 New high for {symbol}: ${current_price:.6f}")
    
    def calculate_stop_loss_levels(self, symbol: str, entry_price: float, config: Dict) -> Dict:
        """Calculate various stop-loss levels for a token."""
        token_stop_loss = config["token_stop_loss"].get(symbol, config["default_stop_loss"])
        
        return {
            "fixed_stop_loss": entry_price * (1 - token_stop_loss),
            "trailing_stop_loss": self.highest_prices.get(symbol, entry_price) * (1 - config["trailing_stop"]),
            "emergency_stop_loss": entry_price * (1 - config["emergency_stop"]),
            "entry_price": entry_price,
            "current_high": self.highest_prices.get(symbol, entry_price)
        }
    
    def check_stop_loss_triggers(self, holdings: Dict[str, float], prices: Dict[str, float], config: Dict) -> List[Dict]:
        """Check if any stop-loss conditions are triggered."""
        triggers = []
        
        for symbol, amount in holdings.items():
            if amount <= 0 or symbol not in prices or symbol not in self.entry_prices:
                continue
            
            current_price = prices[symbol]
            entry_price = self.entry_prices[symbol]
            stop_levels = self.calculate_stop_loss_levels(symbol, entry_price, config)
            
            # Calculate current loss percentage
            loss_percentage = (entry_price - current_price) / entry_price
            
            # Check fixed stop-loss
            if current_price <= stop_levels["fixed_stop_loss"]:
                triggers.append({
                    "symbol": symbol,
                    "type": "fixed_stop_loss",
                    "current_price": current_price,
                    "entry_price": entry_price,
                    "loss_percentage": loss_percentage,
                    "amount": amount,
                    "reason": f"Fixed stop-loss triggered at {loss_percentage:.2%} loss"
                })
            
            # Check trailing stop-loss
            elif config["enable_trailing_stops"] and current_price <= stop_levels["trailing_stop_loss"]:
                triggers.append({
                    "symbol": symbol,
                    "type": "trailing_stop_loss",
                    "current_price": current_price,
                    "entry_price": entry_price,
                    "loss_percentage": loss_percentage,
                    "amount": amount,
                    "reason": f"Trailing stop-loss triggered at {loss_percentage:.2%} loss"
                })
            
            # Check emergency stop-loss
            elif config["enable_emergency_stops"] and current_price <= stop_levels["emergency_stop_loss"]:
                triggers.append({
                    "symbol": symbol,
                    "type": "emergency_stop_loss",
                    "current_price": current_price,
                    "entry_price": entry_price,
                    "loss_percentage": loss_percentage,
                    "amount": amount,
                    "reason": f"EMERGENCY stop-loss triggered at {loss_percentage:.2%} loss"
                })
        
        return triggers
    
    def execute_stop_loss(self, trigger: Dict) -> bool:
        """Execute stop-loss trade through Recall API."""
        try:
            symbol = trigger["symbol"]
            amount = trigger["amount"]
            
            payload = {
                "fromToken": TOKEN_MAP[symbol],
                "toToken": TOKEN_MAP["USDC"],
                "amount": str(int(Decimal(str(amount)) * (10 ** DECIMALS[symbol]))),
                "reason": f"Stop-loss execution: {trigger['reason']}",
            }
            
            r = self.session.post(
                f"{SANDBOX_API}/api/trade/execute",
                json=payload,
                headers={
                    "Authorization": f"Bearer {RECALL_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=20,
            )
            r.raise_for_status()
            
            # Log the stop-loss execution
            self.log_stop_loss(trigger, r.json())
            
            # Remove from tracking
            if symbol in self.entry_prices:
                del self.entry_prices[symbol]
            if symbol in self.highest_prices:
                del self.highest_prices[symbol]
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to execute stop-loss for {trigger['symbol']}: {e}")
            return False
    
    def log_stop_loss(self, trigger: Dict, trade_result: Dict):
        """Log stop-loss execution details."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": trigger["symbol"],
            "type": trigger["type"],
            "entry_price": trigger["entry_price"],
            "exit_price": trigger["current_price"],
            "loss_percentage": trigger["loss_percentage"],
            "amount": trigger["amount"],
            "reason": trigger["reason"],
            "trade_status": trade_result.get("status", "unknown")
        }
        
        self.stop_loss_history.append(log_entry)
        
        # Save to file
        try:
            with open("stop_loss_log.json", "w") as f:
                json.dump(self.stop_loss_history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save stop-loss log: {e}")
    
    def calculate_portfolio_loss(self, holdings: Dict[str, float], prices: Dict[str, float]) -> float:
        """Calculate total portfolio loss percentage."""
        total_value = 0
        total_cost = 0
        
        for symbol, amount in holdings.items():
            if amount > 0 and symbol in prices and symbol in self.entry_prices:
                current_value = amount * prices[symbol]
                cost_basis = amount * self.entry_prices[symbol]
                total_value += current_value
                total_cost += cost_basis
        
        if total_cost == 0:
            return 0.0
        
        return (total_cost - total_value) / total_cost
    
    def run_stop_loss_check(self):
        """Main stop-loss monitoring function."""
        print(f"\n🛡️  Running stop-loss check...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Load configuration
            config = self.load_stop_loss_config()
            
            if not config["enabled"]:
                print("⏸️  Stop-loss monitoring is disabled")
                return
            
            # Fetch current data
            holdings = self.fetch_holdings()
            if not holdings:
                print("❌ No holdings found")
                return
            
            prices = self.fetch_current_prices(list(holdings.keys()))
            if not prices:
                print("❌ No price data available")
                return
            
            # Initialize entry prices for new positions
            self.initialize_entry_prices(holdings, prices)
            
            # Update highest prices for trailing stops
            self.update_highest_prices(prices)
            
            # Check portfolio-level loss
            portfolio_loss = self.calculate_portfolio_loss(holdings, prices)
            print(f"📊 Current portfolio loss: {portfolio_loss:.2%}")
            
            # Check if portfolio loss exceeds maximum
            if portfolio_loss > config["max_portfolio_loss"]:
                print(f"🚨 EMERGENCY: Portfolio loss ({portfolio_loss:.2%}) exceeds maximum ({config['max_portfolio_loss']:.2%})")
                # Execute emergency stop-loss for all positions
                for symbol, amount in holdings.items():
                    if amount > 0:
                        trigger = {
                            "symbol": symbol,
                            "type": "portfolio_emergency",
                            "current_price": prices.get(symbol, 0),
                            "entry_price": self.entry_prices.get(symbol, 0),
                            "loss_percentage": portfolio_loss,
                            "amount": amount,
                            "reason": f"Portfolio emergency stop-loss at {portfolio_loss:.2%} loss"
                        }
                        self.execute_stop_loss(trigger)
                return
            
            # Check individual stop-loss triggers
            triggers = self.check_stop_loss_triggers(holdings, prices, config)
            
            if triggers:
                print(f"🚨 Found {len(triggers)} stop-loss triggers:")
                for trigger in triggers:
                    print(f"  - {trigger['symbol']}: {trigger['reason']}")
                    self.execute_stop_loss(trigger)
            else:
                print("✅ No stop-loss triggers found")
            
            # Print current positions and their status
            self.print_position_status(holdings, prices)
            
        except Exception as e:
            print(f"❌ Stop-loss check failed: {e}")
    
    def print_position_status(self, holdings: Dict[str, float], prices: Dict[str, float]):
        """Print current position status and stop-loss levels."""
        print(f"\n📊 POSITION STATUS")
        print(f"{'='*60}")
        print(f"{'Symbol':<8} {'Amount':<12} {'Entry':<12} {'Current':<12} {'P&L %':<10} {'Stop Level':<12}")
        print("-" * 60)
        
        for symbol, amount in holdings.items():
            if amount > 0 and symbol in prices and symbol in self.entry_prices:
                entry_price = self.entry_prices[symbol]
                current_price = prices[symbol]
                pnl_percentage = (current_price - entry_price) / entry_price
                
                # Get stop-loss level
                config = self.load_stop_loss_config()
                stop_levels = self.calculate_stop_loss_levels(symbol, entry_price, config)
                stop_price = stop_levels["fixed_stop_loss"]
                
                status_icon = "🟢" if pnl_percentage >= 0 else "🔴"
                print(f"{status_icon} {symbol:<6} {amount:>10.4f} ${entry_price:>10.4f} ${current_price:>10.4f} {pnl_percentage:>8.2%} ${stop_price:>10.4f}")

def main():
    """Main function to run the stop-loss manager."""
    manager = StopLossManager()
    
    print("🛡️  Starting Ethereum Ecosystem Stop-Loss Manager...")
    print("Press Ctrl-C to quit")
    
    # Run initial check
    manager.run_stop_loss_check()
    
    # Schedule regular checks
    schedule.every(CHECK_INTERVAL).seconds.do(manager.run_stop_loss_check)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stop-loss manager stopped.")
            break

if __name__ == "__main__":
    main() 