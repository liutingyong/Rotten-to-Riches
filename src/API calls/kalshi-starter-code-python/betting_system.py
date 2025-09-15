"""
Betting System for Kalshi Markets
Integrates with market analysis and provides betting functionality with confirmation prompts
Uses the official KalshiClientsBaseV2ApiKey client structure
"""

import json
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class BetRecommendation:
    """Data class for bet recommendations from sentiment analysis"""
    ticker: str
    side: str  # 'yes' or 'no'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    market_title: str
    current_price: float

@dataclass
class BetOrder:
    """Data class for bet orders"""
    ticker: str
    side: str  # 'yes' or 'no'
    amount: int  # Number of shares (always 1 for safety)
    price: float  # Price in cents
    market_title: str
    client_order_id: str  # Unique order ID

class BettingSystem:
    """Main betting system class that handles bet recommendations and placement"""
    
    def __init__(self, client):
        """
        Initialize the betting system with a Kalshi client
        
        Args:
            client: KalshiHttpClient instance
        """
        self.client = client
        self.pending_bets = []
    
    def analyze_markets_for_betting(self, market_data: Dict[str, Dict]) -> List[BetRecommendation]:
        """
        Analyze market data and return betting recommendations
        This is where sentiment analysis will be integrated
        
        Args:
            market_data: Dictionary of market data from main.py
            
        Returns:
            List of BetRecommendation objects
        """
        recommendations = []
        
        for ticker, data in market_data.items():
            # Placeholder for sentiment analysis integration
            # This will be replaced with actual sentiment analysis
            recommendation = self._mock_sentiment_analysis(ticker, data)
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _mock_sentiment_analysis(self, ticker: str, market_data: Dict) -> Optional[BetRecommendation]:
        """
        Mock sentiment analysis - replace this with actual sentiment analysis
        This is a placeholder that simulates analysis results
        """
        # Mock analysis based on price patterns
        yes_bid = market_data.get('yes_bid', 0)
        yes_ask = market_data.get('yes_ask', 0)
        no_bid = market_data.get('no_bid', 0)
        no_ask = market_data.get('no_ask', 0)
        
        # Simple mock logic - in real implementation, this would use scraped data
        if yes_bid and yes_ask and no_bid and no_ask:
            yes_spread = yes_ask - yes_bid
            no_spread = no_ask - no_bid
            
            # Mock recommendation based on spread analysis
            if yes_spread < no_spread and yes_bid > 30:
                return BetRecommendation(
                    ticker=ticker,
                    side='yes',
                    confidence=0.75,
                    reasoning="Low spread and strong yes bid suggests bullish sentiment",
                    market_title=market_data.get('title', 'Unknown'),
                    current_price=yes_bid
                )
            elif no_spread < yes_spread and no_bid > 30:
                return BetRecommendation(
                    ticker=ticker,
                    side='no',
                    confidence=0.70,
                    reasoning="Low spread and strong no bid suggests bearish sentiment",
                    market_title=market_data.get('title', 'Unknown'),
                    current_price=no_bid
                )
        
        return None
    
    def display_betting_recommendations(self, recommendations: List[BetRecommendation]) -> None:
        """
        Display betting recommendations to the user
        
        Args:
            recommendations: List of BetRecommendation objects
        """
        if not recommendations:
            print("\nNo betting opportunities found based on current analysis")
            return
        
        print(f"\nBETTING RECOMMENDATIONS ({len(recommendations)} opportunities):")
        print("=" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.market_title}")
            print(f"   Ticker: {rec.ticker}")
            print(f"   Recommendation: BET {rec.side.upper()}")
            print(f"   Confidence: {rec.confidence:.1%}")
            print(f"   Current Price: {rec.current_price} cents")
            print(f"   Reasoning: {rec.reasoning}")
            print("-" * 60)
    
    def get_user_bet_confirmation(self, recommendation: BetRecommendation) -> Optional[BetOrder]:
        """
        Get user confirmation for a specific bet recommendation
        
        Args:
            recommendation: BetRecommendation object
            
        Returns:
            BetOrder object if confirmed, None if cancelled
        """
        print(f"\nBET CONFIRMATION")
        print("=" * 50)
        print(f"Market: {recommendation.market_title}")
        print(f"Ticker: {recommendation.ticker}")
        print(f"Side: {recommendation.side.upper()}")
        print(f"Confidence: {recommendation.confidence:.1%}")
        print(f"Current Price: {recommendation.current_price} cents")
        print(f"Reasoning: {recommendation.reasoning}")
        
        # Confirm bet amount (fixed at 1 share for safety)
        amount = 1
        print(f"\nSAFETY LIMIT: Betting exactly 1 share")
        
        # Ask for confirmation to proceed
        while True:
            confirm_amount = input(f"Do you want to proceed with betting 1 share? (yes/no/skip): ").lower()
            if confirm_amount in ['yes', 'y']:
                break
            elif confirm_amount in ['no', 'n', 'skip']:
                return None
            else:
                print("Please enter 'yes', 'no', or 'skip'")
        
        # Get price confirmation
        print(f"\nYou will bet {amount} shares of {recommendation.side.upper()} at {recommendation.current_price} cents each")
        print(f"Total cost: ${amount * recommendation.current_price / 100:.2f}")
        
        while True:
            confirm = input("\nDo you want to place this bet? (yes/no): ").lower()
            if confirm in ['yes', 'y']:
                return BetOrder(
                    ticker=recommendation.ticker,
                    side=recommendation.side,
                    amount=amount,
                    price=recommendation.current_price,
                    market_title=recommendation.market_title,
                    client_order_id=str(uuid.uuid4())
                )
            elif confirm in ['no', 'n']:
                return None
            else:
                print("Please enter 'yes' or 'no'")
    
    def place_bet(self, bet_order: BetOrder) -> bool:
        """
        Place a bet order on Kalshi using the KalshiHttpClient
        
        Args:
            bet_order: BetOrder object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nPlacing bet order...")
            print(f"Ticker: {bet_order.ticker}")
            print(f"Side: {bet_order.side}")
            print(f"Amount: {bet_order.amount}")
            print(f"Price: {bet_order.price} cents")
            print(f"Client Order ID: {bet_order.client_order_id}")
            
            # Place the order using the KalshiHttpClient
            response = self.client.create_order(
                ticker=bet_order.ticker,
                side=bet_order.side,
                amount=bet_order.amount,
                price=bet_order.price,
                order_type="limit"
            )
            
            if response:
                print(f"Bet placed successfully!")
                print(f"Order ID: {response.get('order_id', 'Unknown')}")
                return True
            else:
                print(f"Failed to place bet")
                return False
                
        except Exception as e:
            print(f"Error placing bet: {str(e)}")
            return False
    
    def process_betting_workflow(self, market_data: Dict[str, Dict]) -> None:
        """
        Complete betting workflow: analyze markets, get recommendations, confirm, and place bets
        
        Args:
            market_data: Dictionary of market data from main.py
        """
        print(f"\nSTARTING BETTING WORKFLOW")
        print("=" * 50)
        
        # Step 1: Analyze markets for betting opportunities
        print("Analyzing markets for betting opportunities...")
        recommendations = self.analyze_markets_for_betting(market_data)
        
        # Step 2: Display recommendations
        self.display_betting_recommendations(recommendations)
        
        if not recommendations:
            return
        
        # Step 3: Get user confirmation for each recommendation
        confirmed_bets = []
        for recommendation in recommendations:
            bet_order = self.get_user_bet_confirmation(recommendation)
            if bet_order:
                confirmed_bets.append(bet_order)
        
        if not confirmed_bets:
            print("\nNo bets confirmed by user")
            return
        
        # Step 4: Place confirmed bets
        print(f"\nPLACING {len(confirmed_bets)} CONFIRMED BETS")
        print("=" * 50)
        
        successful_bets = 0
        for bet_order in confirmed_bets:
            if self.place_bet(bet_order):
                successful_bets += 1
        
        print(f"\nBETTING SUMMARY")
        print("=" * 30)
        print(f"Total recommendations: {len(recommendations)}")
        print(f"Confirmed bets: {len(confirmed_bets)}")
        print(f"Successfully placed: {successful_bets}")
        print(f"Failed: {len(confirmed_bets) - successful_bets}")
    
    def get_account_balance(self) -> Dict:
        """
        Get current account balance
        
        Returns:
            Dictionary with balance information
        """
        try:
            balance = self.client.get_balance()
            return balance
        except Exception as e:
            print(f"Error getting balance: {str(e)}")
            return {}
    
    def display_account_balance(self) -> None:
        """Display current account balance"""
        balance = self.get_account_balance()
        if balance:
            print(f"\nACCOUNT BALANCE")
            print("=" * 30)
            print(f"Available Balance: ${balance.get('balance', 0) / 100:.2f}")
            print(f"Pending Balance: ${balance.get('pending_balance', 0) / 100:.2f}")
        else:
            print("Could not retrieve account balance")


def integrate_sentiment_analysis(market_data: Dict[str, Dict], scraped_data: List[str]) -> List[BetRecommendation]:
    """
    Placeholder function for integrating sentiment analysis with scraped data
    
    Args:
        market_data: Dictionary of market data from main.py
        scraped_data: List of scraped text data for sentiment analysis
        
    Returns:
        List of BetRecommendation objects
    """
    # This is where you'll integrate your sentiment analysis modules
    # from src.basic_processing_and_sentiment_analysis.sentiment_classifier import analyze_sentiment
    # from src.scikit_ensemble.tfidf_xgboost import predict_sentiment
    
    # For now, return empty list - this will be implemented when sentiment analysis is ready
    print("Sentiment analysis integration placeholder - will be implemented with scraped data")
    return []


if __name__ == "__main__":
    # Example usage
    print("This module provides betting functionality for Kalshi markets")
    print("Import and use BettingSystem class with your KalshiHttpClient")
