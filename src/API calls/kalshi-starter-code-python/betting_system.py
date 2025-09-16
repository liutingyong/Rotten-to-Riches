"""
Betting System for Kalshi Markets
Integrates with market analysis and provides betting functionality with confirmation prompts
Uses the official KalshiClientsBaseV2ApiKey client structure
"""

import json
import uuid
import sys
import os
import time
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
    predicted_probability: float = 0.0  # Our predicted probability
    expected_value: float = 0.0  # Expected value of the bet
    recommended_bet_size: int = 1  # Recommended bet size in shares

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
            # Get scraped data for this ticker using intelligent matching
            ticker_scraped_data = self._find_matching_scraped_data(ticker, scraped_data)
            
            # Use sentiment analysis for betting recommendations
            recommendation = self._analyze_sentiment_for_market(ticker, data, ticker_scraped_data)
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _find_matching_scraped_data(self, ticker: str, scraped_data: Dict[str, List[str]]) -> List[str]:
        """
        Find the best matching scraped data for a ticker
        
        Args:
            ticker: Market ticker (e.g., "KXRTTRONARES-45")
            scraped_data: Dictionary of scraped data
            
        Returns:
            List of matching scraped text data
        """
        # Extract base ticker (remove suffix like -45, -50, etc.)
        base_ticker = ticker.split('-')[0] if '-' in ticker else ticker
        
        # Try base ticker match first
        if base_ticker in scraped_data:
            return scraped_data[base_ticker]
        
        # Try exact ticker match
        if ticker in scraped_data:
            return scraped_data[ticker]
        
        # Try generic fallback
        if 'GENERIC' in scraped_data:
            return scraped_data['GENERIC']
        
        # Return empty list if no match found
        return []
    
    def _analyze_sentiment_for_market(self, ticker: str, market_data: Dict, scraped_data: List[str]) -> Optional[BetRecommendation]:
        """
        Analyze sentiment for a specific market using intelligent betting logic
        
        Args:
            ticker: Market ticker
            market_data: Market data dictionary
            scraped_data: List of scraped text data for sentiment analysis
            
        Returns:
            BetRecommendation if profitable bet is found, None otherwise
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
            
            # Debug: Show sentiment analysis details
            sentiment_data = sentiment_rec['sentiment_data']
            print(f"Sentiment analysis for {ticker}:")
            print(f"  Positive percentage: {sentiment_data['positive_percentage']:.1%}")
            print(f"  Overall sentiment: {sentiment_data['overall_sentiment']}")
            print(f"  Confidence: {sentiment_rec['confidence']:.1%}")
            print(f"  Side recommendation: {sentiment_rec['side']}")
            
            # Handle neutral sentiment intelligently
            if sentiment_rec['side'] is None:
                # For neutral sentiment, we can still bet if the market is mispriced
                # If sentiment is ~50% but market price suggests different probability, there's opportunity
                sentiment_percentage = sentiment_data['positive_percentage']
                
                # Get market prices to calculate implied probability
                yes_bid = market_data.get('yes_bid', 0)
                yes_ask = market_data.get('yes_ask', 0)
                no_bid = market_data.get('no_bid', 0)
                no_ask = market_data.get('no_ask', 0)
                
                # Calculate implied probability from market prices
                if yes_ask > 0 and no_ask > 0:
                    implied_prob_yes = yes_ask / 100  # Market thinks this is the probability
                    implied_prob_no = no_ask / 100    # Market thinks this is the probability
                    
                    # Check for arbitrage opportunities or market mispricing
                    market_implied_total = implied_prob_yes + implied_prob_no
                    
                    # If market probabilities don't add up to ~100%, there's inefficiency
                    if abs(market_implied_total - 1.0) > 0.05:  # 5% inefficiency threshold
                        if market_implied_total > 1.05:  # Market overpriced
                            side = 'no'
                            reasoning = f"Market overpriced (total: {market_implied_total:.1%}), betting NO"
                        else:  # Market underpriced
                            side = 'yes'
                            reasoning = f"Market underpriced (total: {market_implied_total:.1%}), betting YES"
                        
                        sentiment_rec['side'] = side
                        sentiment_rec['reasoning'] = reasoning
                        print(f"Market inefficiency found for {ticker}: {reasoning}")
                    
                    # If our sentiment differs significantly from market expectation
                    elif abs(sentiment_percentage - implied_prob_yes) > 0.15:  # 15% difference
                        if sentiment_percentage > implied_prob_yes:
                            side = 'yes'
                            reasoning = f"Neutral sentiment ({sentiment_percentage:.1%}) vs market expectation ({implied_prob_yes:.1%}) - betting YES"
                        else:
                            side = 'no'
                            reasoning = f"Neutral sentiment ({sentiment_percentage:.1%}) vs market expectation ({implied_prob_yes:.1%}) - betting NO"
                        
                        sentiment_rec['side'] = side
                        sentiment_rec['reasoning'] = reasoning
                        print(f"Neutral sentiment betting opportunity found for {ticker}: {reasoning}")
                    
                    # Check for value betting based on neutral sentiment
                    elif sentiment_percentage > 0.48 and sentiment_percentage < 0.52:  # True neutral (48-52%)
                        # For true neutral, bet on the side with better odds
                        if implied_prob_yes < 0.45:  # Market thinks <45% chance, bet YES
                            side = 'yes'
                            reasoning = f"True neutral sentiment ({sentiment_percentage:.1%}), market undervalues YES ({implied_prob_yes:.1%})"
                        elif implied_prob_no < 0.45:  # Market thinks <45% chance, bet NO
                            side = 'no'
                            reasoning = f"True neutral sentiment ({sentiment_percentage:.1%}), market undervalues NO ({implied_prob_no:.1%})"
                        else:
                            print(f"True neutral sentiment for {ticker}, market pricing seems fair")
                            return None
                        
                        sentiment_rec['side'] = side
                        sentiment_rec['reasoning'] = reasoning
                        print(f"Neutral value bet found for {ticker}: {reasoning}")
                    else:
                        print(f"Neutral sentiment for {ticker}, market pricing seems fair")
                        return None
                else:
                    print(f"Neutral sentiment for {ticker}, no market prices available")
                    return None
            
            # Extract market threshold from ticker (e.g., "KXTRON-50" -> 50)
            market_threshold = self._extract_market_threshold(ticker)
            if market_threshold is None:
                print(f"Could not extract threshold from ticker {ticker}")
                return None
            
            # Calculate our predicted probability based on sentiment
            base_probability = sentiment_rec['sentiment_data']['positive_percentage']
            confidence = sentiment_rec['confidence']
            
            # Adjust probability based on market threshold
            adjusted_probability = self._adjust_probability_for_threshold(base_probability, market_threshold)
            
            # Get current market prices
            yes_bid = market_data.get('yes_bid', 0)
            yes_ask = market_data.get('yes_ask', 0)
            no_bid = market_data.get('no_bid', 0)
            no_ask = market_data.get('no_ask', 0)
            
            # Calculate expected value for both sides
            yes_ev = self._calculate_expected_value(adjusted_probability, yes_bid, yes_ask, 'yes')
            no_ev = self._calculate_expected_value(1 - adjusted_probability, no_bid, no_ask, 'no')
            
            # Choose the side with higher expected value
            if yes_ev > no_ev and yes_ev > 0:
                side = 'yes'
                current_price = yes_ask  # Use ask price since we're buying
                expected_value = yes_ev
            elif no_ev > yes_ev and no_ev > 0:
                side = 'no'
                current_price = no_ask  # Use ask price since we're buying
                expected_value = no_ev
            else:
                print(f"No profitable bet found for {ticker} (Yes EV: {yes_ev:.3f}, No EV: {no_ev:.3f})")
                return None
            
            # Calculate bet size based on confidence and expected value
            bet_size = self._calculate_bet_size(confidence, expected_value, current_price)
            
            if bet_size <= 0:
                print(f"Bet size too small for {ticker}")
                return None
            
            return BetRecommendation(
                ticker=ticker,
                side=side,
                confidence=confidence,
                reasoning=f"Predicted {adjusted_probability:.1%} probability above {market_threshold}. EV: {expected_value:.3f}",
                market_title=market_data.get('title', ticker),
                current_price=current_price,
                predicted_probability=adjusted_probability,
                expected_value=expected_value,
                recommended_bet_size=bet_size
            )
                
        except Exception as e:
            print(f"Error analyzing sentiment for {ticker}: {str(e)}")
            return None
    
    def _extract_market_threshold(self, ticker: str) -> Optional[int]:
        """
        Extract the numerical threshold from a market ticker
        e.g., "KXTRON-50" -> 50, "KXTRON-70" -> 70
        """
        try:
            # Look for pattern like "-50", "-70", etc.
            parts = ticker.split('-')
            if len(parts) >= 2:
                threshold_str = parts[-1]
                # Extract just the number part
                threshold = int(''.join(filter(str.isdigit, threshold_str)))
                return threshold
            return None
        except (ValueError, IndexError):
            return None
    
    def _adjust_probability_for_threshold(self, base_probability: float, market_threshold: int) -> float:
        """
        Adjust probability based on market threshold hierarchy
        
        If we're 65% confident it's above 70, we should be even more confident it's above 50
        """
        # Assume a reasonable baseline threshold (e.g., 50)
        baseline_threshold = 50
        
        # Calculate the difference from baseline
        threshold_diff = market_threshold - baseline_threshold
        
        # Adjust probability based on threshold difference
        # Lower thresholds should have higher probabilities
        adjustment_factor = threshold_diff * 0.02  # 2% per threshold point
        
        adjusted_probability = base_probability - adjustment_factor
        
        # Ensure probability stays within bounds
        return max(0.01, min(0.99, adjusted_probability))
    
    def _calculate_expected_value(self, probability: float, bid: float, ask: float, side: str) -> float:
        """
        Calculate expected value for a bet
        
        Args:
            probability: Our predicted probability of winning
            bid: Bid price (what we can sell at)
            ask: Ask price (what we'd have to buy at)
            side: 'yes' or 'no'
        """
        if side == 'yes':
            # For YES bets: we win if outcome is YES
            # Profit = 100 - ask_price, Loss = ask_price
            if ask <= 0:
                return 0
            expected_profit = probability * (100 - ask) - (1 - probability) * ask
            return expected_profit / 100  # Convert to decimal
        else:
            # For NO bets: we win if outcome is NO
            # Profit = 100 - ask_price, Loss = ask_price
            if ask <= 0:
                return 0
            expected_profit = probability * (100 - ask) - (1 - probability) * ask
            return expected_profit / 100  # Convert to decimal
    
    def _calculate_bet_size(self, confidence: float, expected_value: float, price: float) -> int:
        """
        Calculate optimal bet size based on Kelly Criterion
        
        Args:
            confidence: Our confidence level (0-1)
            expected_value: Expected value of the bet
            price: Current market price
            
        Returns:
            Recommended bet size in shares
        """
        if expected_value <= 0:
            return 0
        
        # Kelly Criterion: f = (bp - q) / b
        # where b = odds, p = probability of winning, q = probability of losing
        
        # Convert price to odds
        if price > 0 and price < 100:  # Avoid division by zero when price is 100
            odds = (100 - price) / price  # Decimal odds
            
            # Avoid division by zero in Kelly calculation
            if odds > 0:
                kelly_fraction = (odds * confidence - (1 - confidence)) / odds
                
                # Apply conservative Kelly (use 25% of Kelly fraction)
                conservative_kelly = kelly_fraction * 0.25
                
                # Convert to shares (minimum 1, maximum 10 for safety)
                bet_size = max(1, min(10, int(conservative_kelly * 100)))
                
                return bet_size
        
        # Default to 1 share for edge cases
        return 1
    
    def display_betting_recommendations(self, recommendations: List[BetRecommendation]) -> None:
        """
        Display betting recommendations to the user
        
        Args:
            recommendations: List of BetRecommendation objects
        """
        if not recommendations:
            print("\nNo betting opportunities found based on current analysis")
            return
        
        print(f"\nINTELLIGENT BETTING RECOMMENDATIONS ({len(recommendations)} opportunities):")
        print("=" * 100)
        
        # Sort by expected value (highest first)
        recommendations.sort(key=lambda x: x.expected_value, reverse=True)
        
        total_expected_value = 0
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.market_title}")
            print(f"   Ticker: {rec.ticker}")
            print(f"   Recommendation: BET {rec.side.upper()}")
            print(f"   Our Prediction: {rec.predicted_probability:.1%} probability")
            print(f"   Confidence: {rec.confidence:.1%}")
            print(f"   Current Price: {rec.current_price} cents")
            print(f"   Expected Value: {rec.expected_value:.3f}")
            print(f"   Recommended Bet Size: {rec.recommended_bet_size} shares")
            print(f"   Reasoning: {rec.reasoning}")
            
            # Calculate potential profit/loss
            if rec.side == 'yes':
                potential_profit = rec.recommended_bet_size * (100 - rec.current_price)
                potential_loss = rec.recommended_bet_size * rec.current_price
            else:
                potential_profit = rec.recommended_bet_size * (100 - rec.current_price)
                potential_loss = rec.recommended_bet_size * rec.current_price
            
            print(f"   Potential Profit: ${potential_profit/100:.2f}")
            print(f"   Potential Loss: ${potential_loss/100:.2f}")
            
            # Avoid division by zero in risk/reward ratio
            if potential_loss > 0:
                risk_reward_ratio = potential_profit / potential_loss
                print(f"   Risk/Reward Ratio: {risk_reward_ratio:.2f}:1")
            else:
                print(f"   Risk/Reward Ratio: N/A (no risk)")
            
            total_expected_value += rec.expected_value * rec.recommended_bet_size
            print("-" * 80)
        
        print(f"\nPORTFOLIO SUMMARY:")
        print(f"Total Expected Value: {total_expected_value:.3f}")
        print(f"Number of Bets: {len(recommendations)}")
        
        # Avoid division by zero
        if len(recommendations) > 0:
            print(f"Average Expected Value per Bet: {total_expected_value/len(recommendations):.3f}")
        else:
            print(f"Average Expected Value per Bet: N/A")
    
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
            confirm_amount = input(f"Do you want to proceed with betting 1 share? (yes/no): ").lower()
            if confirm_amount in ['yes', 'y']:
                break
            elif confirm_amount in ['no', 'n']:
                return None
            else:
                print("Please enter 'yes' or 'no'")
        
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
    
    def place_bet(self, bet_order: BetOrder, mock_mode: bool = False) -> bool:
        """
        Place a bet order on Kalshi using the KalshiHttpClient
        
        Args:
            bet_order: BetOrder object
            mock_mode: If True, simulate the bet without actually placing it
            
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
            # Use market order to ensure execution, or limit order slightly above ask for better fill
            if bet_order.side == 'yes':
                # For YES bets, use market order or limit slightly above ask
                order_price = bet_order.price + 1  # Add 1 cent to improve fill probability
                order_type = "limit"
            else:
                # For NO bets, use market order or limit slightly above ask  
                order_price = bet_order.price + 1  # Add 1 cent to improve fill probability
                order_type = "limit"
            
            print(f"Placing {order_type} order at {order_price} cents (original ask: {bet_order.price} cents)")
            
            # Debug: Print order details before sending
            print(f"Order details:")
            print(f"  Ticker: {bet_order.ticker}")
            print(f"  Side: {bet_order.side}")
            print(f"  Amount: {bet_order.amount}")
            print(f"  Price: {order_price}")
            print(f"  Order Type: {order_type}")
            
            if mock_mode:
                print("MOCK MODE: Simulating bet placement...")
                print("✅ Bet would have been placed successfully!")
                print(f"Mock Order ID: MOCK_{int(time.time())}")
                print(f"Mock Order Status: pending")
                return True
            
            response = self.client.create_order(
                ticker=bet_order.ticker,
                side=bet_order.side,
                amount=bet_order.amount,
                price=order_price,
                order_type=order_type
            )
            
            print(f"API Response: {response}")
            
            if response:
                print(f"Bet placed successfully!")
                print(f"Order ID: {response.get('order_id', 'Unknown')}")
                print(f"Order Status: {response.get('status', 'Unknown')}")
                return True
            else:
                print(f"Failed to place bet - no response from API")
                print(f"This could be due to:")
                print(f"  - Insufficient balance")
                print(f"  - Market closed")
                print(f"  - Invalid ticker")
                print(f"  - API authentication issues")
                return False
                
        except Exception as e:
            print(f"Error placing bet: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"This could be due to:")
            print(f"  - Network connectivity issues")
            print(f"  - API rate limiting")
            print(f"  - Invalid order parameters")
            print(f"  - Market not accepting orders")
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
            # Test real API calls
            if self.place_bet(bet_order, mock_mode=False):
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
    
    def test_api_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            print("Testing API connection...")
            
            # Test 1: Get exchange status
            status = self.client.get_exchange_status()
            print(f"Exchange status: {status}")
            
            # Test 2: Get account balance
            balance = self.client.get_balance()
            print(f"Account balance: {balance}")
            
            # Test 3: Get a market
            markets = self.client.get_markets()
            if markets and 'markets' in markets:
                first_market = markets['markets'][0]
                ticker = first_market.get('ticker')
                print(f"Testing with market: {ticker}")
                
                # Test 4: Get market details
                market_data = self.client.get_market(ticker)
                print(f"Market data: {market_data}")
                
                # Test 5: Try a simple POST request to see if orders endpoint exists
                print("Testing orders endpoint...")
                test_order = {
                    "ticker": ticker,
                    "side": "yes",
                    "amount": 1,
                    "price": 1,  # Very low price to avoid real order
                    "order_type": "limit"
                }
                
                # Try to make a POST request manually
                try:
                    response = self.client.post("/trade-api/v2/portfolio/orders", test_order)
                    print(f"Orders endpoint response: {response}")
                except Exception as e:
                    print(f"Orders endpoint test failed: {str(e)}")
                
            return True
            
        except Exception as e:
            print(f"API connection test failed: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False


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
            yes_ask = data.get('yes_ask', 0)
            no_ask = data.get('no_ask', 0)
            
            # Determine which price to use based on the recommended side
            if sentiment_rec['side'] == 'yes' and yes_ask > 0:
                current_price = yes_ask  # Use ask price since we're buying
            elif sentiment_rec['side'] == 'no' and no_ask > 0:
                current_price = no_ask  # Use ask price since we're buying
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
