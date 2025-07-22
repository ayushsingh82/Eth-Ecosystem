# 🚀 Eth-Ecosystem Agent

> **Recall Hackathon Project** - An intelligent agent that discovers, trades, and manages the best Ethereum ecosystem tokens with automated stop-loss protection.

## 🎯 Project Overview

Eth-Ecosystem is an AI-powered trading agent that leverages the Recall sandbox to automatically identify, trade, and manage the most promising Ethereum ecosystem tokens. The agent combines advanced market analysis, risk management, and automated trading to optimize DeFi portfolio performance.

## ✨ Key Features

### 🔍 **Token Discovery & Analysis**
- **Real-time market scanning** for top Ethereum ecosystem tokens
- **Multi-factor analysis** including market cap, volume, volatility, and momentum
- **DeFi protocol health assessment** and risk evaluation
- **Dynamic token selection** based on market conditions

### 📊 **Intelligent Trading**
- **Automated portfolio rebalancing** with smart drift detection
- **Risk-adjusted position sizing** based on volatility and market cap
- **Multi-timeframe analysis** for optimal entry/exit points
- **Gas optimization** for cost-effective transactions

### 🛡️ **Risk Management**
- **Automated stop-loss execution** with configurable thresholds
- **Dynamic position sizing** based on market volatility
- **Portfolio diversification** across DeFi sectors
- **Real-time risk monitoring** and alert system

### 🤖 **Recall Integration**
- **Seamless sandbox integration** for safe testing
- **Real-time balance monitoring** and trade execution
- **Automated order management** with slippage protection
- **Comprehensive trade logging** and performance tracking

## 🏗️ Architecture

```
Eth-Ecosystem Agent
├── 📊 Market Analysis
│   ├── Token Discovery Engine
│   ├── Risk Assessment Module
│   └── Performance Analytics
├── 🤖 Trading Engine
│   ├── Portfolio Manager
│   ├── Order Execution
│   └── Stop-Loss Manager
├── 🛡️ Risk Management
│   ├── Position Sizing
│   ├── Volatility Monitoring
│   └── Alert System
└── 🔗 Recall Integration
    ├── Sandbox Connector
    ├── Balance Monitor
    └── Trade Logger
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Recall API access
- CoinGecko API key (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd eth-eco
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Configuration

Create a `.env` file with your API credentials:

```env
RECALL_API_KEY=your_recall_api_key
PRODUCTION_API_KEY=your_coingecko_production_key
SANDBOX_API_KEY=your_coingecko_sandbox_key
```

## 📁 Project Structure

```
eth-eco/
├── 📊 eth_tokens.py          # Token discovery and analysis
├── 📈 token_analyzer.py      # 24h performance analysis
├── 🤖 portfolio_manager.py   # Main trading agent
├── 🛡️ stop_loss_manager.py  # Stop-loss automation
├── 📋 requirements.txt       # Dependencies
├── ⚙️ .env.example          # Environment template
├── 🚫 .gitignore            # Git ignore rules
└── 📖 README.md             # This file
```

## 🎮 Usage

### 1. Token Discovery
```bash
python3 eth_tokens.py
```
Discovers and analyzes top Ethereum ecosystem tokens.

### 2. Performance Analysis
```bash
python3 token_analyzer.py
```
Analyzes 24-hour performance and market impact.

### 3. Portfolio Management
```bash
python3 portfolio_manager.py
```
Runs the main trading agent with automated rebalancing.

### 4. Stop-Loss Management
```bash
python3 stop_loss_manager.py
```
Manages automated stop-loss execution.

## 🔧 Configuration Files

### Portfolio Configuration (`eth_portfolio_config.json`)
```json
{
  "ETH": 0.30,
  "USDC": 0.15,
  "UNI": 0.12,
  "LINK": 0.10,
  "AAVE": 0.08,
  "COMP": 0.06,
  "MKR": 0.05,
  "SNX": 0.04,
  "YFI": 0.03,
  "CRV": 0.03,
  "BAL": 0.02,
  "SUSHI": 0.02
}
```

### Trading Parameters
- **Drift Threshold**: 3% (rebalance when allocation drifts >3%)
- **Max Slippage**: 5% (maximum acceptable slippage)
- **Rebalance Time**: 9:00 AM daily
- **Stop-Loss Threshold**: Configurable per token

## 🛡️ Risk Management Features

### Stop-Loss Protection
- **Dynamic stop-loss levels** based on volatility
- **Trailing stop-loss** for trending tokens
- **Portfolio-level risk limits**
- **Emergency stop-loss** for extreme market conditions

### Position Sizing
- **Kelly Criterion** for optimal position sizing
- **Volatility-adjusted allocations**
- **Market cap-weighted positions**
- **Maximum position limits**

### Risk Monitoring
- **Real-time volatility tracking**
- **Volume analysis** for liquidity assessment
- **Market cap monitoring** for token health
- **Correlation analysis** for diversification

## 📊 Performance Metrics

The agent tracks comprehensive performance metrics:

- **Total Portfolio Value**
- **24h Performance**
- **Risk-Adjusted Returns**
- **Sharpe Ratio**
- **Maximum Drawdown**
- **Win/Loss Ratio**
- **Average Trade Duration**

## 🔄 Trading Strategy

### Token Selection Criteria
1. **Market Cap**: >$50M minimum
2. **Volume**: >$5M daily volume
3. **Volatility**: <30% daily (adjustable)
4. **Protocol Health**: Active development and community
5. **Liquidity**: Sufficient DEX liquidity

### Entry/Exit Logic
- **Entry**: Technical analysis + fundamental scoring
- **Exit**: Stop-loss, take-profit, or rebalancing
- **Rebalancing**: Daily at 9:00 AM or on significant drift

## 🚨 Alerts & Notifications

The agent provides real-time alerts for:
- **High volatility** (>30% daily change)
- **Low volume** (<$5M daily)
- **Stop-loss triggers**
- **Rebalancing events**
- **Portfolio drift** (>5%)

## 🔧 Customization

### Adding New Tokens
1. Add token address to `TOKEN_MAP`
2. Add CoinGecko ID to `COINGECKO_IDS`
3. Set decimal places in `DECIMALS`
4. Update portfolio weights in config

### Adjusting Risk Parameters
- Modify `DRIFT_THRESHOLD` for rebalancing frequency
- Adjust `MAX_SLIPPAGE` for trade execution
- Update stop-loss percentages per token
- Configure volatility thresholds

## 📈 Backtesting

The agent includes backtesting capabilities:
- **Historical performance analysis**
- **Strategy optimization**
- **Risk parameter tuning**
- **Portfolio simulation**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for the Recall hackathon. Please refer to the hackathon guidelines for usage terms.

## 🆘 Support

For support during the hackathon:
- Check the Recall documentation
- Review the project issues
- Contact the team via hackathon channels

---

**Built with ❤️ for the Recall Hackathon**

*Empowering DeFi with intelligent Ethereum ecosystem trading*
