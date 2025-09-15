"""
Client wrapper to provide compatibility between official ExchangeClient and existing market analysis functions
"""

from typing import Dict, Any, Optional
import sys
import os

# Add the official client path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'KalshiAPIStarterCodeWithApiKey'))
from KalshiClientsBaseV2ApiKey import ExchangeClient

class KalshiClientWrapper:
    """
    Wrapper around the official ExchangeClient to provide compatibility with existing market analysis functions
    """
    
    def __init__(self, exchange_client: ExchangeClient):
        """
        Initialize wrapper with official ExchangeClient
        
        Args:
            exchange_client: Official ExchangeClient instance
        """
        self.client = exchange_client
    
    def get_market(self, ticker: str) -> Dict[str, Any]:
        """
        Get market data for a specific ticker
        
        Args:
            ticker: Market ticker
            
        Returns:
            Market data dictionary
        """
        return self.client.get_market(ticker)
    
    def get_markets(self, event_ticker: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get markets data
        
        Args:
            event_ticker: Event ticker to filter by
            **kwargs: Additional parameters
            
        Returns:
            Markets data dictionary
        """
        return self.client.get_markets(event_ticker=event_ticker, **kwargs)
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance
        
        Returns:
            Balance data dictionary
        """
        return self.client.get_balance()
    
    def create_order(self, ticker: str, side: str, amount: int, price: float, order_type: str = "limit") -> Dict[str, Any]:
        """
        Create an order (compatibility method for betting system)
        
        Args:
            ticker: Market ticker
            side: Order side ('yes' or 'no')
            amount: Number of shares
            price: Price in cents
            order_type: Order type (not used in official client)
            
        Returns:
            Order response dictionary
        """
        import uuid
        
        # Generate unique client order ID
        client_order_id = str(uuid.uuid4())
        
        # Create order using official client
        return self.client.create_order(
            ticker=ticker,
            client_order_id=client_order_id,
            side=side,
            action="buy",
            count=amount,
            type="limit",
            yes_price=int(price) if side == "yes" else None,
            no_price=int(price) if side == "no" else None
        )
    
    def get_orders(self, ticker: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get orders
        
        Args:
            ticker: Market ticker to filter by
            **kwargs: Additional parameters
            
        Returns:
            Orders data dictionary
        """
        return self.client.get_orders(ticker=ticker, **kwargs)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancel response dictionary
        """
        return self.client.cancel_order(order_id)
    
    def get_positions(self, ticker: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Get positions
        
        Args:
            ticker: Market ticker to filter by
            **kwargs: Additional parameters
            
        Returns:
            Positions data dictionary
        """
        return self.client.get_positions(ticker=ticker, **kwargs)
