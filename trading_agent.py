#!/usr/bin/env python3
"""
🚀 Eth-Ecosystem Trading Agent - Recall Hackathon
================================================

Main trading agent that integrates all components:
- Token discovery and analysis
- Portfolio management and rebalancing
- Stop-loss management
- Risk assessment
- Recall sandbox integration

This is the main entry point for the Eth-Ecosystem agent.
"""

import os
import json
import time
import requests
import schedule
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# ------------------------------------------------------------
#  Configuration
# ------------------------------------------------------------
RECALL_KEY = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Trading configuration
DRIFT_THRESHOLD = 0.03    # 3% drift threshold for rebalancing
REB_TIME = "09:00"        # Daily rebalancing time
MAX_SLIPPAGE = 0.05       # 5% max slippage
CHECK_INTERVAL = 300      # 5 minutes for stop-loss checks

# Token configuration
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

# Stop-loss configuration
TOKEN_STOP_LOSS = {
    "ETH": 0.12, "USDC": 0.05, "USDT": 0.05, "UNI": 0.18, "LINK": 0.18,
    "AAVE": 0.20, "COMP": 0.20, "MKR": 0.18, "SNX": 0.22, "YFI": 0.25,
    "CRV": 0.20, "BAL": 0.20, "SUSHI": 0.22, "1INCH": 0.22, "REN": 0.25, "ZRX": 0.20
}

# ------------------------------------------------------------
#  Import agent modules (with fallbacks)
# ------------------------------------------------------------
try:
    from eth_tokens import EthereumTokenFetcher
    from token_analyzer import TokenAnalyzer
    from portfolio_manager import (
        load_targets, fetch_prices, fetch_holdings, get_defi_metrics,
        analyze_portfolio_performance, compute_orders,
        check_defi_alerts, calculate_portfolio_metrics
    )
    from stop_loss_manager import StopLossManager
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Some modules not available - {e}")
    print("Running with integrated functionality...")
    MODULES_AVAILABLE = False

# ------------------------------------------------------------
#  Integrated Trading Agent Class
# ------------------------------------------------------------
class EthEcosystemTradingAgent:
    """Main trading agent that integrates all components."""
    
    def __init__(self):
        self.session = requests.Session()
        self.entry_prices = {}
        self.highest_prices = {}
        self.stop_loss_history = []
        
        # Initialize modules if available
        if MODULES_AVAILABLE:
            self.fetcher = EthereumTokenFetcher()
            self.analyzer = TokenAnalyzer()
            self.stop_loss_manager = StopLossManager()
        else:
            self.fetcher = None
            self.analyzer = None
            self.stop_loss_manager = None
    
    def load_targets(self) -> Dict[str, float]:
        """Load target portfolio weights."""
        try:
            with open("eth_portfolio_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default DeFi portfolio
            default_targets = {
                "ETH": 0.30, "USDC": 0.15, "UNI": 0.12, "LINK": 0.10,
                "AAVE": 0.08, "COMP": 0.06, "MKR": 0.05, "SNX": 0.04,
                "YFI": 0.03, "CRV": 0.03, "BAL": 0.02, "SUSHI": 0.02
            }
            self.save_targets(default_targets)
            return default_targets
    
    def save_targets(self, targets: Dict[str, float]):
        """Save target portfolio weights."""
        with open("eth_portfolio_config.json", "w") as f:
            json.dump(targets, f, indent=2)
    
    def fetch_prices(self, symbols: List[str]) -> Dict[str, float]:
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
        if not RECALL_KEY:
            print("⚠️  No RECALL_API_KEY found")
            return {}
        
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
    
    def get_defi_metrics(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get DeFi metrics for tokens."""
        ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
        
        params = {
            "ids": ids, "vs_currency": "usd", "order": "market_cap_desc",
            "per_page": 50, "page": 1, "sparkline": False
        }
        
        if COINGECKO_KEY:
            params['x_cg_demo_api_key'] = COINGECKO_KEY
        
        try:
            r = self.session.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params=params,
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            
            metrics = {}
            for coin in data:
                symbol = next((sym for sym, cg_id in COINGECKO_IDS.items() if cg_id == coin['id']), None)
                if symbol:
                    metrics[symbol] = {
                        "market_cap": coin['market_cap'],
                        "volume_24h": coin['total_volume'],
                        "price_change_24h": coin['price_change_percentage_24h'],
                        "market_cap_rank": coin['market_cap_rank']
                    }
            
            return metrics
        except Exception as e:
            print(f"❌ Error fetching metrics: {e}")
            return {}
    
    def to_base_units(self, amount_float: float, decimals: int) -> str:
        """Convert to base units for Recall API."""
        scaled = Decimal(str(amount_float)) * (10 ** decimals)
        return str(int(scaled.quantize(Decimal("1"), rounding=ROUND_DOWN)))
    
    def execute_trade(self, symbol: str, side: str, amount_float: float) -> bool:
        """Execute a trade through Recall API."""
        if symbol not in TOKEN_MAP:
            print(f"❌ Unknown token symbol: {symbol}")
            return False
        
        from_token, to_token = (
            (TOKEN_MAP[symbol], TOKEN_MAP["USDC"]) if side == "sell"
            else (TOKEN_MAP["USDC"], TOKEN_MAP[symbol])
        )
        
        payload = {
            "fromToken": from_token,
            "toToken": to_token,
            "amount": self.to_base_units(amount_float, DECIMALS[symbol]),
            "reason": f"Eth-Ecosystem agent: {side} {symbol}",
        }
        
        headers = {
            "Authorization": f"Bearer {RECALL_KEY}",
            "Content-Type": "application/json",
        }
        
        try:
            r = self.session.post(
                f"{SANDBOX_API}/api/trade/execute",
                json=payload,
                headers=headers,
                timeout=20,
            )
            r.raise_for_status()
            result = r.json()
            print(f"✅ Trade executed: {side} {amount_float:.6f} {symbol}")
            return True
        except Exception as e:
            print(f"❌ Trade failed: {e}")
            return False
    
    def analyze_portfolio(self, holdings: Dict[str, float], prices: Dict[str, float], targets: Dict[str, float]):
        """Analyze portfolio performance."""
        total_value = sum(holdings.get(s, 0) * prices.get(s, 0) for s in targets)
        
        print(f"\n{'='*60}")
        print(f"PORTFOLIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"Total Portfolio Value: ${total_value:,.2f}")
        print(f"\n{'Symbol':<8} {'Current %':<12} {'Target %':<12} {'Drift %':<12} {'Value':<15}")
        print("-" * 60)
        
        total_drift = 0
        for sym, target_weight in targets.items():
            if sym not in prices or prices[sym] == 0:
                continue
                
            current_val = holdings.get(sym, 0) * prices[sym]
            current_weight = current_val / total_value if total_value > 0 else 0
            drift_pct = (current_weight - target_weight) * 100
            
            print(f"{sym:<8} {current_weight*100:>8.2f}% {target_weight*100:>10.2f}% {drift_pct:>10.2f}% ${current_val:>12,.2f}")
            total_drift += abs(drift_pct)
        
        print(f"\nAverage Drift: {total_drift/len(targets):.2f}%")
        print(f"Rebalance Threshold: {DRIFT_THRESHOLD*100:.1f}%")
    
    def compute_orders(self, targets: Dict[str, float], prices: Dict[str, float], holdings: Dict[str, float]) -> List[Dict]:
        """Compute rebalancing orders."""
        total_value = sum(holdings.get(s, 0) * prices.get(s, 0) for s in targets)
        if total_value == 0:
            return []
        
        orders = []
        for sym, weight in targets.items():
            if sym not in prices or prices[sym] == 0:
                continue
                
            current_val = holdings.get(sym, 0) * prices[sym]
            target_val = total_value * weight
            drift_pct = (current_val - target_val) / total_value
            
            if abs(drift_pct) >= DRIFT_THRESHOLD:
                delta_val = abs(target_val - current_val)
                token_amt = delta_val / prices[sym]
                side = "sell" if drift_pct > 0 else "buy"
                
                if side == "buy":
                    token_amt *= (1 + MAX_SLIPPAGE)
                
                orders.append({
                    "symbol": sym,
                    "side": side,
                    "amount": token_amt,
                    "drift": drift_pct
                })
        
        return orders
    
    def check_stop_loss(self, holdings: Dict[str, float], prices: Dict[str, float]) -> List[Dict]:
        """Check for stop-loss triggers."""
        triggers = []
        
        for symbol, amount in holdings.items():
            if amount <= 0 or symbol not in prices or symbol not in self.entry_prices:
                continue
            
            current_price = prices[symbol]
            entry_price = self.entry_prices[symbol]
            stop_loss_pct = TOKEN_STOP_LOSS.get(symbol, 0.15)
            stop_price = entry_price * (1 - stop_loss_pct)
            
            if current_price <= stop_price:
                loss_pct = (entry_price - current_price) / entry_price
                triggers.append({
                    "symbol": symbol,
                    "current_price": current_price,
                    "entry_price": entry_price,
                    "loss_percentage": loss_pct,
                    "amount": amount,
                    "stop_price": stop_price
                })
        
        return triggers
    
    def initialize_entry_prices(self, holdings: Dict[str, float], prices: Dict[str, float]):
        """Initialize entry prices for new positions."""
        for symbol, amount in holdings.items():
            if amount > 0 and symbol in prices and symbol not in self.entry_prices:
                self.entry_prices[symbol] = prices[symbol]
                self.highest_prices[symbol] = prices[symbol]
                print(f"📊 Initialized entry price for {symbol}: ${prices[symbol]:.6f}")
    
    def update_highest_prices(self, prices: Dict[str, float]):
        """Update highest prices for trailing stops."""
        for symbol, current_price in prices.items():
            if symbol in self.highest_prices and current_price > self.highest_prices[symbol]:
                self.highest_prices[symbol] = current_price
    
    def log_trade(self, symbol: str, side: str, amount: float, price: float, status: str):
        """Log trade details."""
        trade_log = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "status": status
        }
        
        try:
            with open("trade_log.json", "r") as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(trade_log)
        
        with open("trade_log.json", "w") as f:
            json.dump(logs, f, indent=2)
    
    def run_portfolio_rebalance(self):
        """Main portfolio rebalancing function."""
        print(f"\n🔄 Starting Eth-Ecosystem portfolio rebalance...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Load configuration and fetch data
            targets = self.load_targets()
            prices = self.fetch_prices(list(targets.keys()))
            holdings = self.fetch_holdings()
            
            if not holdings:
                print("❌ No holdings found")
                return
            
            if not prices:
                print("❌ No price data available")
                return
            
            # Initialize entry prices
            self.initialize_entry_prices(holdings, prices)
            
            # Analyze portfolio
            self.analyze_portfolio(holdings, prices, targets)
            
            # Check stop-loss triggers
            stop_loss_triggers = self.check_stop_loss(holdings, prices)
            if stop_loss_triggers:
                print(f"\n🚨 Found {len(stop_loss_triggers)} stop-loss triggers:")
                for trigger in stop_loss_triggers:
                    print(f"  - {trigger['symbol']}: {trigger['loss_percentage']:.2%} loss")
                    success = self.execute_trade(
                        trigger['symbol'], 'sell', trigger['amount']
                    )
                    if success:
                        # Remove from tracking
                        if trigger['symbol'] in self.entry_prices:
                            del self.entry_prices[trigger['symbol']]
                        if trigger['symbol'] in self.highest_prices:
                            del self.highest_prices[trigger['symbol']]
            
            # Compute and execute rebalancing orders
            orders = self.compute_orders(targets, prices, holdings)
            
            if not orders:
                print("✅ Portfolio already within target ranges")
                return
            
            print(f"\n📈 Executing {len(orders)} rebalancing trades...")
            for order in orders:
                success = self.execute_trade(
                    order['symbol'], order['side'], order['amount']
                )
                if success:
                    price = prices.get(order['symbol'], 0)
                    self.log_trade(
                        order['symbol'], order['side'], 
                        order['amount'], price, 'executed'
                    )
            
            print("🎯 Portfolio rebalance complete!")
            
        except Exception as e:
            print(f"❌ Rebalancing failed: {e}")
    
    def run_stop_loss_check(self):
        """Run stop-loss monitoring."""
        print(f"\n🛡️  Running stop-loss check...")
        
        try:
            holdings = self.fetch_holdings()
            if not holdings:
                return
            
            prices = self.fetch_prices(list(holdings.keys()))
            if not prices:
                return
            
            self.initialize_entry_prices(holdings, prices)
            self.update_highest_prices(prices)
            
            triggers = self.check_stop_loss(holdings, prices)
            if triggers:
                print(f"🚨 Found {len(triggers)} stop-loss triggers")
                for trigger in triggers:
                    print(f"  - {trigger['symbol']}: {trigger['loss_percentage']:.2%} loss")
                    self.execute_trade(trigger['symbol'], 'sell', trigger['amount'])
            else:
                print("✅ No stop-loss triggers")
                
        except Exception as e:
            print(f"❌ Stop-loss check failed: {e}")
    
    def test_recall_connection(self):
        """Test Recall API connection."""
        if not RECALL_KEY:
            print("❌ No RECALL_API_KEY found")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {RECALL_KEY}",
                "Content-Type": "application/json"
            }
            
            # Test balance endpoint
            r = self.session.get(
                f"{SANDBOX_API}/api/balance",
                headers=headers,
                timeout=10
            )
            
            if r.ok:
                print("✅ Recall API connection successful")
                balances = r.json()
                if balances:
                    print("📊 Current balances:")
                    for token, amount in balances.items():
                        print(f"  - {token}: {amount:,.2f}")
                return True
            else:
                print(f"❌ Recall API error: {r.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Recall API connection failed: {e}")
            return False

# ------------------------------------------------------------
#  Main execution
# ------------------------------------------------------------
def main():
    """Main function to run the trading agent."""
    print("🚀 Starting Eth-Ecosystem Trading Agent...")
    print("=" * 60)
    
    agent = EthEcosystemTradingAgent()
    
    # Test Recall connection
    if not agent.test_recall_connection():
        print("⚠️  Cannot connect to Recall sandbox. Check your API key.")
        return
    
    # Run initial rebalance
    agent.run_portfolio_rebalance()
    
    # Schedule regular tasks
    schedule.every().day.at(REB_TIME).do(agent.run_portfolio_rebalance)
    schedule.every(CHECK_INTERVAL).seconds.do(agent.run_stop_loss_check)
    
    print(f"\n📅 Scheduled tasks:")
    print(f"  • Portfolio rebalancing: Daily at {REB_TIME}")
    print(f"  • Stop-loss monitoring: Every {CHECK_INTERVAL} seconds")
    print(f"\nPress Ctrl-C to stop the agent...")
    
    # Main loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Eth-Ecosystem Trading Agent stopped.")
            break

if __name__ == "__main__":
    main()