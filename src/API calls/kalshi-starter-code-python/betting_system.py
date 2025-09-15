"""
Betting System for Kalshi Markets
Integrates with market analysis and provides betting functionality with confirmation prompts
Uses the official KalshiClientsBaseV2ApiKey client structure
"""

import json
import uuid
import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add the src directory to the path to import sentiment analysis
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from basic_processing_and_sentiment_analysis.sentiment_classifier import sentiment_analyzer

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
    
    def analyze_markets_for_betting(self, market_data: Dict[str, Dict], scraped_data: Dict[str, List[str]] = None) -> List[BetRecommendation]:
        """
        Analyze market data and return betting recommendations using sentiment analysis
        
        Args:
            market_data: Dictionary of market data from main.py
            scraped_data: Dictionary mapping tickers to lists of scraped text data
            
        Returns:
            List of BetRecommendation objects
        """
        recommendations = []
        
        if scraped_data is None:
            scraped_data = {}
        
        for ticker, data in market_data.items():
            # Get scraped data for this ticker, or use empty list if none available
            ticker_scraped_data = scraped_data.get(ticker, [])
            
            # Use sentiment analysis for betting recommendations
            recommendation = self._analyze_sentiment_for_market(ticker, data, ticker_scraped_data)
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_sentiment_for_market(self, ticker: str, market_data: Dict, scraped_data: List[str]) -> Optional[BetRecommendation]:
        """
        Analyze sentiment for a specific market using scraped data and NLTK sentiment analysis
        
        Args:
            ticker: Market ticker
            market_data: Market data dictionary
            scraped_data: List of scraped text data for sentiment analysis
            
        Returns:
            BetRecommendation if sentiment analysis suggests a bet, None otherwise
        """
        if not scraped_data:
            print(f"No scraped data available for {ticker}, skipping sentiment analysis")
            return None
        
        try:
            # Get sentiment-based betting recommendation
            sentiment_rec = sentiment_analyzer.get_betting_recommendation(
                texts=scraped_data,
                market_title=market_data.get('title', ticker)
            )
            
            # Only proceed if we have a clear recommendation
            if sentiment_rec['side'] is None:
                print(f"Neutral sentiment for {ticker}, no betting recommendation")
                return None
            
            # Get current market prices
            yes_bid = market_data.get('yes_bid', 0)
            no_bid = market_data.get('no_bid', 0)
            
            # Determine which price to use based on the recommended side
            if sentiment_rec['side'] == 'yes' and yes_bid > 0:
                current_price = yes_bid
            elif sentiment_rec['side'] == 'no' and no_bid > 0:
                current_price = no_bid
            else:
                print(f"No valid price available for {sentiment_rec['side']} side of {ticker}")
                return None
            
            # Only recommend if confidence is above threshold and price is reasonable
            confidence_threshold = 0.55  # Minimum confidence for betting
            min_price = 10  # Minimum price threshold (10 cents)
            
            if sentiment_rec['confidence'] >= confidence_threshold and current_price >= min_price:
                return BetRecommendation(
                    ticker=ticker,
                    side=sentiment_rec['side'],
                    confidence=sentiment_rec['confidence'],
                    reasoning=sentiment_rec['reasoning'],
                    market_title=market_data.get('title', ticker),
                    current_price=current_price
                )
            else:
                print(f"Low confidence ({sentiment_rec['confidence']:.2%}) or price ({current_price}) for {ticker}, skipping")
                return None
                
        except Exception as e:
            print(f"Error analyzing sentiment for {ticker}: {str(e)}")
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
    
    def process_betting_workflow(self, market_data: Dict[str, Dict], scraped_data: Dict[str, List[str]] = None) -> None:
        """
        Complete betting workflow: analyze markets, get recommendations, confirm, and place bets
        
        Args:
            market_data: Dictionary of market data from main.py
            scraped_data: Dictionary mapping tickers to lists of scraped text data
        """
        print(f"\nSTARTING BETTING WORKFLOW")
        print("=" * 50)
        
        # Step 1: Analyze markets for betting opportunities
        print("Analyzing markets for betting opportunities using sentiment analysis...")
        recommendations = self.analyze_markets_for_betting(market_data, scraped_data)
        
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


def integrate_sentiment_analysis(market_data: Dict[str, Dict], scraped_data: Dict[str, List[str]]) -> List[BetRecommendation]:
    """
    Integrate sentiment analysis with scraped data to generate betting recommendations
    
    Args:
        market_data: Dictionary of market data from main.py
        scraped_data: Dictionary mapping tickers to lists of scraped text data
        
    Returns:
        List of BetRecommendation objects based on sentiment analysis
    """
    print("Integrating sentiment analysis with scraped data...")
    
    recommendations = []
    
    for ticker, data in market_data.items():
        # Get scraped data for this ticker
        ticker_scraped_data = scraped_data.get(ticker, [])
        
        if not ticker_scraped_data:
            print(f"No scraped data available for {ticker}, skipping")
            continue
        
        try:
            # Get sentiment-based betting recommendation
            sentiment_rec = sentiment_analyzer.get_betting_recommendation(
                texts=ticker_scraped_data,
                market_title=data.get('title', ticker)
            )
            
            # Only proceed if we have a clear recommendation
            if sentiment_rec['side'] is None:
                print(f"Neutral sentiment for {ticker}, no betting recommendation")
                continue
            
            # Get current market prices
            yes_bid = data.get('yes_bid', 0)
            no_bid = data.get('no_bid', 0)
            
            # Determine which price to use based on the recommended side
            if sentiment_rec['side'] == 'yes' and yes_bid > 0:
                current_price = yes_bid
            elif sentiment_rec['side'] == 'no' and no_bid > 0:
                current_price = no_bid
            else:
                print(f"No valid price available for {sentiment_rec['side']} side of {ticker}")
                continue
            
            # Only recommend if confidence is above threshold and price is reasonable
            confidence_threshold = 0.55  # Minimum confidence for betting
            min_price = 10  # Minimum price threshold (10 cents)
            
            if sentiment_rec['confidence'] >= confidence_threshold and current_price >= min_price:
                recommendation = BetRecommendation(
                    ticker=ticker,
                    side=sentiment_rec['side'],
                    confidence=sentiment_rec['confidence'],
                    reasoning=sentiment_rec['reasoning'],
                    market_title=data.get('title', ticker),
                    current_price=current_price
                )
                recommendations.append(recommendation)
                print(f"Generated recommendation for {ticker}: {sentiment_rec['side']} with {sentiment_rec['confidence']:.1%} confidence")
            else:
                print(f"Low confidence ({sentiment_rec['confidence']:.2%}) or price ({current_price}) for {ticker}, skipping")
                
        except Exception as e:
            print(f"Error analyzing sentiment for {ticker}: {str(e)}")
            continue
    
    print(f"Generated {len(recommendations)} betting recommendations from sentiment analysis")
    return recommendations


if __name__ == "__main__":
    # Example usage
    print("This module provides betting functionality for Kalshi markets")
    print("Import and use BettingSystem class with your KalshiHttpClient")
