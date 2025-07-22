import requests
import json
from typing import List, Dict, Optional
import time

class EthereumTokenFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
    def get_ethereum_tokens(self, limit: int = 100, page: int = 1) -> List[Dict]:
        """
        Fetch Ethereum ecosystem tokens from CoinGecko
        
        Args:
            limit: Number of tokens to fetch (max 250)
            page: Page number for pagination
            
        Returns:
            List of token data
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),
                'page': page,
                'sparkline': False,
                'platform': 'ethereum'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
    
    def get_token_details(self, token_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific token
        
        Args:
            token_id: CoinGecko token ID
            
        Returns:
            Detailed token information
        """
        try:
            url = f"{self.base_url}/coins/{token_id}"
            params = {
                'localization': False,
                'tickers': False,
                'market_data': True,
                'community_data': False,
                'developer_data': False,
                'sparkline': False
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching token details for {token_id}: {e}")
            return None
    
    def get_top_defi_tokens(self, limit: int = 50) -> List[Dict]:
        """
        Fetch top DeFi tokens on Ethereum
        
        Args:
            limit: Number of tokens to fetch
            
        Returns:
            List of DeFi token data
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'category': 'decentralized-finance-defi',
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
            print(f"Error fetching DeFi tokens: {e}")
            return []
    
    def search_tokens(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for tokens by name or symbol
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of matching tokens
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                'query': query
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            coins = data.get('coins', [])
            
            # Filter for Ethereum tokens and limit results
            eth_tokens = [coin for coin in coins if coin.get('platform') == 'ethereum'][:limit]
            
            return eth_tokens
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching tokens: {e}")
            return []

def main():
    """Example usage of the EthereumTokenFetcher"""
    fetcher = EthereumTokenFetcher()
    
    print("🔍 Fetching top Ethereum ecosystem tokens...")
    print("=" * 60)
    
    # Get top Ethereum tokens
    tokens = fetcher.get_ethereum_tokens(limit=20)
    
    if tokens:
        print(f"Found {len(tokens)} tokens:")
        print()
        
        for i, token in enumerate(tokens, 1):
            print(f"{i:2d}. {token['name']} ({token['symbol'].upper()})")
            print(f"    Price: ${token['current_price']:,.6f}")
            print(f"    Market Cap: ${token['market_cap']:,.0f}")
            print(f"    24h Change: {token['price_change_percentage_24h']:+.2f}%")
            print(f"    Volume: ${token['total_volume']:,.0f}")
            print()
    
    print("🔍 Fetching top DeFi tokens...")
    print("=" * 60)
    
    # Get top DeFi tokens
    defi_tokens = fetcher.get_top_defi_tokens(limit=10)
    
    if defi_tokens:
        print(f"Found {len(defi_tokens)} DeFi tokens:")
        print()
        
        for i, token in enumerate(defi_tokens, 1):
            print(f"{i:2d}. {token['name']} ({token['symbol'].upper()})")
            print(f"    Price: ${token['current_price']:,.6f}")
            print(f"    Market Cap: ${token['market_cap']:,.0f}")
            print(f"    24h Change: {token['price_change_percentage_24h']:+.2f}%")
            print()

if __name__ == "__main__":
    main() 