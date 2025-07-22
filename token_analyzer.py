import requests
import json
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import time

class TokenAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
    def get_ethereum_tokens(self, limit: int = 100) -> List[Dict]:
        """Fetch Ethereum tokens with 24h price change data"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),
                'page': 1,
                'sparkline': False,
                'platform': 'ethereum'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
    
    def analyze_24h_performance(self, tokens: List[Dict]) -> Dict:
        """
        Analyze 24-hour performance of tokens
        
        Args:
            tokens: List of token data from CoinGecko
            
        Returns:
            Dictionary with analysis results
        """
        if not tokens:
            return {}
        
        # Initialize counters
        gainers = []
        losers = []
        unchanged = []
        
        total_market_cap = 0
        total_volume = 0
        
        for token in tokens:
            price_change = token.get('price_change_percentage_24h', 0)
            market_cap = token.get('market_cap', 0)
            volume = token.get('total_volume', 0)
            
            total_market_cap += market_cap
            total_volume += volume
            
            token_info = {
                'name': token['name'],
                'symbol': token['symbol'].upper(),
                'price': token['current_price'],
                'price_change_24h': price_change,
                'market_cap': market_cap,
                'volume': volume
            }
            
            if price_change > 0:
                gainers.append(token_info)
            elif price_change < 0:
                losers.append(token_info)
            else:
                unchanged.append(token_info)
        
        # Sort by absolute price change
        gainers.sort(key=lambda x: abs(x['price_change_24h']), reverse=True)
        losers.sort(key=lambda x: abs(x['price_change_24h']), reverse=True)
        
        return {
            'total_tokens': len(tokens),
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
            'total_market_cap': total_market_cap,
            'total_volume': total_volume,
            'gainer_count': len(gainers),
            'loser_count': len(losers),
            'unchanged_count': len(unchanged)
        }
    
    def calculate_net_market_impact(self, tokens: List[Dict]) -> Dict:
        """
        Calculate net market impact of price changes
        
        Args:
            tokens: List of token data
            
        Returns:
            Dictionary with net impact calculations
        """
        total_gain_value = 0
        total_loss_value = 0
        net_change = 0
        
        for token in tokens:
            price_change_pct = token.get('price_change_percentage_24h', 0)
            market_cap = token.get('market_cap', 0)
            
            if price_change_pct > 0:
                # Calculate value gained
                gain_value = market_cap * (price_change_pct / 100)
                total_gain_value += gain_value
            elif price_change_pct < 0:
                # Calculate value lost
                loss_value = market_cap * (abs(price_change_pct) / 100)
                total_loss_value += loss_value
            
            net_change += market_cap * (price_change_pct / 100)
        
        return {
            'total_gain_value': total_gain_value,
            'total_loss_value': total_loss_value,
            'net_change': net_change,
            'gain_loss_ratio': total_gain_value / total_loss_value if total_loss_value > 0 else float('inf')
        }
    
    def get_top_performers(self, tokens: List[Dict], top_n: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """
        Get top gainers and losers
        
        Args:
            tokens: List of token data
            top_n: Number of top performers to return
            
        Returns:
            Tuple of (top_gainers, top_losers)
        """
        # Sort by price change percentage
        sorted_tokens = sorted(tokens, key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)
        
        top_gainers = sorted_tokens[:top_n]
        top_losers = sorted_tokens[-top_n:][::-1]  # Reverse to get worst first
        
        return top_gainers, top_losers
    
    def generate_report(self, limit: int = 100) -> None:
        """
        Generate a comprehensive 24-hour performance report
        
        Args:
            limit: Number of tokens to analyze
        """
        print("🔍 Analyzing Ethereum Token Performance (24h)")
        print("=" * 70)
        print(f"📊 Fetching data for top {limit} Ethereum tokens...")
        
        tokens = self.get_ethereum_tokens(limit)
        
        if not tokens:
            print("❌ Failed to fetch token data")
            return
        
        print(f"✅ Successfully fetched {len(tokens)} tokens")
        print()
        
        # Analyze performance
        analysis = self.analyze_24h_performance(tokens)
        market_impact = self.calculate_net_market_impact(tokens)
        top_gainers, top_losers = self.get_top_performers(tokens, 10)
        
        # Print summary
        print("📈 PERFORMANCE SUMMARY")
        print("-" * 40)
        print(f"Total Tokens Analyzed: {analysis['total_tokens']}")
        print(f"Gainers: {analysis['gainer_count']} tokens")
        print(f"Losers: {analysis['loser_count']} tokens")
        print(f"Unchanged: {analysis['unchanged_count']} tokens")
        print()
        
        # Market impact
        print("💰 MARKET IMPACT")
        print("-" * 40)
        print(f"Total Market Cap: ${analysis['total_market_cap']:,.0f}")
        print(f"Total Volume (24h): ${analysis['total_volume']:,.0f}")
        print(f"Net Market Change: ${market_impact['net_change']:,.0f}")
        print(f"Total Value Gained: ${market_impact['total_gain_value']:,.0f}")
        print(f"Total Value Lost: ${market_impact['total_loss_value']:,.0f}")
        if market_impact['gain_loss_ratio'] != float('inf'):
            print(f"Gain/Loss Ratio: {market_impact['gain_loss_ratio']:.2f}")
        print()
        
        # Top gainers
        print("🚀 TOP 10 GAINERS")
        print("-" * 40)
        for i, token in enumerate(top_gainers, 1):
            print(f"{i:2d}. {token['name']} ({token['symbol']})")
            print(f"    Price: ${token['current_price']:,.6f}")
            print(f"    Change: +{token['price_change_percentage_24h']:.2f}%")
            print(f"    Market Cap: ${token['market_cap']:,.0f}")
            print()
        
        # Top losers
        print("📉 TOP 10 LOSERS")
        print("-" * 40)
        for i, token in enumerate(top_losers, 1):
            print(f"{i:2d}. {token['name']} ({token['symbol']})")
            print(f"    Price: ${token['current_price']:,.6f}")
            print(f"    Change: {token['price_change_percentage_24h']:.2f}%")
            print(f"    Market Cap: ${token['market_cap']:,.0f}")
            print()
        
        # Performance distribution
        print("📊 PERFORMANCE DISTRIBUTION")
        print("-" * 40)
        
        # Count tokens in different ranges
        ranges = [
            ("> +20%", lambda x: x > 20),
            ("+10% to +20%", lambda x: 10 < x <= 20),
            ("+5% to +10%", lambda x: 5 < x <= 10),
            ("+1% to +5%", lambda x: 1 < x <= 5),
            ("0% to +1%", lambda x: 0 < x <= 1),
            ("-1% to 0%", lambda x: -1 < x <= 0),
            ("-5% to -1%", lambda x: -5 < x <= -1),
            ("-10% to -5%", lambda x: -10 < x <= -5),
            ("-20% to -10%", lambda x: -20 < x <= -10),
            ("< -20%", lambda x: x <= -20)
        ]
        
        for range_name, condition in ranges:
            count = sum(1 for token in tokens if condition(token.get('price_change_percentage_24h', 0)))
            percentage = (count / len(tokens)) * 100
            print(f"{range_name:12}: {count:3d} tokens ({percentage:5.1f}%)")

def main():
    """Main function to run the token analyzer"""
    analyzer = TokenAnalyzer()
    
    # Generate comprehensive report
    analyzer.generate_report(limit=100)
    
    print("\n" + "=" * 70)
    print("📅 Report generated at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("=" * 70)

if __name__ == "__main__":
    main() 