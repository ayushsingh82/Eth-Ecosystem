import os, json, time, math, requests, schedule
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()                                     # read .env

# ------------------------------------------------------------
#  Configuration
# ------------------------------------------------------------
RECALL_KEY  = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Ethereum ecosystem token addresses (you'll need to update these with actual addresses)
TOKEN_MAP = {
    "ETH": "0x0000000000000000000000000000000000000000",  # Ethereum
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # 6 dec
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # 6 dec
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",   # Uniswap
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",  # Chainlink
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",  # Aave
    "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",  # Compound
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",   # Maker
    "SNX": "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",   # Synthetix
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",   # Yearn Finance
    "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",   # Curve
    "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",   # Balancer
    "SUSHI": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2", # SushiSwap
    "1INCH": "0x111111111117dC0aa78b770fA6A738034120C302", # 1inch
    "REN": "0x408e41876cCcDC0F92210600ef50372656052a38",   # Ren
    "ZRX": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",   # 0x Protocol
}

DECIMALS = {
    "ETH": 18, "USDC": 6, "USDT": 6, "UNI": 18, "LINK": 18, "AAVE": 18,
    "COMP": 18, "MKR": 18, "SNX": 18, "YFI": 18, "CRV": 18, "BAL": 18,
    "SUSHI": 18, "1INCH": 18, "REN": 18, "ZRX": 18
}

COINGECKO_IDS = {
    "ETH": "ethereum",
    "USDC": "usd-coin",
    "USDT": "tether",
    "UNI": "uniswap",
    "LINK": "chainlink",
    "AAVE": "aave",
    "COMP": "compound-governance-token",
    "MKR": "maker",
    "SNX": "havven",
    "YFI": "yearn-finance",
    "CRV": "curve-dao-token",
    "BAL": "balancer",
    "SUSHI": "sushi",
    "1INCH": "1inch",
    "REN": "republic-protocol",
    "ZRX": "0x",
}

DRIFT_THRESHOLD = 0.03    # rebalance if > 3% off target (lower for DeFi tokens)
REB_TIME        = "09:00" # local server time
MAX_SLIPPAGE    = 0.05    # 5% max slippage for DeFi tokens

# ------------------------------------------------------------
#  Helper utilities
# ------------------------------------------------------------
def load_targets() -> dict[str, float]:
    """Load target portfolio weights from config file."""
    try:
        with open("eth_portfolio_config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        # Default Ethereum DeFi portfolio weights
        default_targets = {
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
            "SUSHI": 0.02,    # 2% SushiSwap (DEX)
        }
        save_targets(default_targets)
        return default_targets

def save_targets(targets: dict[str, float]):
    """Save target portfolio weights to config file."""
    with open("eth_portfolio_config.json", "w") as f:
        json.dump(targets, f, indent=2)

def to_base_units(amount_float: float, decimals: int) -> str:
    """Convert human units → integer string that Recall expects."""
    scaled = Decimal(str(amount_float)) * (10 ** decimals)
    return str(int(scaled.quantize(Decimal("1"), rounding=ROUND_DOWN)))

def log_trade(symbol: str, side: str, amount: float, price: float, status: str):
    """Log trade details to file."""
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

# ------------------------------------------------------------
#  Market data
# ------------------------------------------------------------
def fetch_prices(symbols: list[str]) -> dict[str, float]:
    """Fetch current prices from CoinGecko."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {"ids": ids, "vs_currencies": "usd"}
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    r = requests.get(
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

def fetch_holdings() -> dict[str, float]:
    """Return whole‑token balances from Recall's sandbox."""
    r = requests.get(
        f"{SANDBOX_API}/api/balance",
        headers={"Authorization": f"Bearer {RECALL_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

def get_defi_metrics(symbols: list[str]) -> dict[str, dict]:
    """Get additional metrics for DeFi tokens (volume, market cap, etc.)."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {
        "ids": ids,
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    r = requests.get(
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

# ------------------------------------------------------------
#  Trading logic
# ------------------------------------------------------------
def compute_orders(targets, prices, holdings):
    """Return a list of {'symbol','side','amount'} trades."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    if total_value == 0:
        raise ValueError("No balances found; fund your sandbox wallet first.")

    overweight, underweight = [], []
    for sym, weight in targets.items():
        if sym not in prices or prices[sym] == 0:
            continue
            
        current_val = holdings.get(sym, 0) * prices[sym]
        target_val  = total_value * weight
        drift_pct   = (current_val - target_val) / total_value
        
        if abs(drift_pct) >= DRIFT_THRESHOLD:
            delta_val = abs(target_val - current_val)
            token_amt = delta_val / prices[sym]
            side      = "sell" if drift_pct > 0 else "buy"
            
            # Add slippage protection for DeFi tokens
            if side == "buy":
                token_amt *= (1 + MAX_SLIPPAGE)  # Account for potential slippage
            
            (overweight if side == "sell" else underweight).append(
                {"symbol": sym, "side": side, "amount": token_amt}
            )

    # Execute sells first so we have USDC to fund buys
    return overweight + underweight

def execute_trade(symbol, side, amount_float):
    """Execute a trade through Recall API."""
    if symbol not in TOKEN_MAP:
        raise ValueError(f"Unknown token symbol: {symbol}")
    
    from_token, to_token = (
        (TOKEN_MAP[symbol], TOKEN_MAP["USDC"]) if side == "sell"
        else (TOKEN_MAP["USDC"], TOKEN_MAP[symbol])
    )

    payload = {
        "fromToken": from_token,
        "toToken":   to_token,
        "amount":    to_base_units(amount_float, DECIMALS[symbol]),
        "reason":    f"Automatic DeFi portfolio rebalance - {side} {symbol}",
    }
    
    r = requests.post(
        f"{SANDBOX_API}/api/trade/execute",
        json=payload,
        headers={
            "Authorization": f"Bearer {RECALL_KEY}",
            "Content-Type":  "application/json",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

def analyze_portfolio_performance(holdings, prices, targets):
    """Analyze current portfolio performance."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    
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

# ------------------------------------------------------------
#  Risk management
# ------------------------------------------------------------
def check_defi_alerts(symbols: list[str]):
    """Check for DeFi protocol risks and issue alerts."""
    metrics = get_defi_metrics(symbols)
    
    print(f"\n{'='*50}")
    print("DEFI RISK ALERTS")
    print(f"{'='*50}")
    
    for symbol, data in metrics.items():
        price_change = data['price_change_24h']
        
        if abs(price_change) > 15:
            alert = "🚨 HIGH VOLATILITY" if abs(price_change) > 30 else "⚠️  MODERATE VOLATILITY"
            print(f"{symbol}: {alert} - {price_change:+.2f}% (24h)")
        
        # Check volume
        if data['volume_24h'] < 5000000:  # Less than $5M volume
            print(f"{symbol}: ⚠️  LOW VOLUME - ${data['volume_24h']:,.0f} (24h)")
        
        # Check market cap for small caps
        if data['market_cap'] < 100000000:  # Less than $100M market cap
            print(f"{symbol}: ⚠️  SMALL CAP - ${data['market_cap']:,.0f} market cap")

def adjust_targets_for_risk(targets: dict[str, float], metrics: dict[str, dict]) -> dict[str, float]:
    """Adjust targets based on risk metrics and market conditions."""
    adjusted_targets = targets.copy()
    
    for symbol, data in metrics.items():
        if symbol in adjusted_targets:
            price_change = abs(data['price_change_24h'])
            volume = data['volume_24h']
            market_cap = data['market_cap']
            
            # Reduce allocation for high-risk tokens
            risk_factor = 1.0
            
            # Volatility adjustment
            if price_change > 30:
                risk_factor *= 0.8  # Reduce by 20%
                print(f"Reducing {symbol} allocation due to high volatility ({price_change:.1f}%)")
            
            # Volume adjustment
            if volume < 10000000:  # Less than $10M volume
                risk_factor *= 0.9  # Reduce by 10%
                print(f"Reducing {symbol} allocation due to low volume (${volume:,.0f})")
            
            # Market cap adjustment
            if market_cap < 50000000:  # Less than $50M market cap
                risk_factor *= 0.85  # Reduce by 15%
                print(f"Reducing {symbol} allocation due to small market cap (${market_cap:,.0f})")
            
            # Increase allocation for stable tokens
            if price_change < 5 and volume > 50000000 and market_cap > 1000000000:
                risk_factor *= 1.05  # Increase by 5%
                print(f"Increasing {symbol} allocation due to stability")
            
            adjusted_targets[symbol] *= risk_factor
    
    # Normalize weights to sum to 1
    total_weight = sum(adjusted_targets.values())
    if total_weight > 0:
        adjusted_targets = {k: v/total_weight for k, v in adjusted_targets.items()}
    
    return adjusted_targets

def calculate_portfolio_metrics(holdings, prices, targets):
    """Calculate portfolio risk and performance metrics."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    metrics = get_defi_metrics(list(targets.keys()))
    
    # Calculate weighted average metrics
    weighted_volatility = 0
    weighted_volume = 0
    weighted_market_cap = 0
    
    for symbol, target_weight in targets.items():
        if symbol in metrics and symbol in holdings and holdings[symbol] > 0:
            current_weight = (holdings[symbol] * prices[symbol]) / total_value
            weighted_volatility += abs(metrics[symbol]['price_change_24h']) * current_weight
            weighted_volume += metrics[symbol]['volume_24h'] * current_weight
            weighted_market_cap += metrics[symbol]['market_cap'] * current_weight
    
    print(f"\n📊 PORTFOLIO METRICS")
    print(f"{'='*30}")
    print(f"Weighted Avg Volatility: {weighted_volatility:.2f}%")
    print(f"Weighted Avg Volume: ${weighted_volume:,.0f}")
    print(f"Weighted Avg Market Cap: ${weighted_market_cap:,.0f}")

# ------------------------------------------------------------
#  Daily job
# ------------------------------------------------------------
def rebalance():
    """Main rebalancing function."""
    print(f"\n🔄 Starting Ethereum DeFi portfolio rebalance...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        targets = load_targets()
        prices = fetch_prices(list(targets.keys()))
        holdings = fetch_holdings()
        
        # Analyze current portfolio
        analyze_portfolio_performance(holdings, prices, targets)
        
        # Check DeFi risks and adjust targets
        metrics = get_defi_metrics(list(targets.keys()))
        check_defi_alerts(list(targets.keys()))
        
        # Calculate portfolio metrics
        calculate_portfolio_metrics(holdings, prices, targets)
        
        # Adjust targets based on risk metrics
        adjusted_targets = adjust_targets_for_risk(targets, metrics)
        if adjusted_targets != targets:
            print(f"\n📊 Adjusting targets based on risk metrics...")
            save_targets(adjusted_targets)
            targets = adjusted_targets
        
        # Compute and execute orders
        orders = compute_orders(targets, prices, holdings)

        if not orders:
            print("✅ Portfolio already within ±3% of target.")
            return

        print(f"\n📈 Executing {len(orders)} trades...")
        for order in orders:
            try:
                res = execute_trade(**order)
                price = prices.get(order['symbol'], 0)
                log_trade(order['symbol'], order['side'], order['amount'], price, res.get('status', 'unknown'))
                print(f"✅ Executed {order['side']} {order['amount']:.6f} {order['symbol']} → {res.get('status', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed to execute {order}: {e}")

        print("🎯 Ethereum DeFi portfolio rebalance complete.")
        
    except Exception as e:
        print(f"❌ Rebalancing failed: {e}")

# ------------------------------------------------------------
#  Scheduler
# ------------------------------------------------------------
schedule.every().day.at(REB_TIME).do(rebalance)

if __name__ == "__main__":
    print("🚀 Starting Ethereum DeFi Portfolio Manager...")
    print("Press Ctrl-C to quit")
    
    # Run initial rebalance
    rebalance()
    
    # Schedule daily rebalancing
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Portfolio manager stopped.")
            break 