# Rotten to Riches
Objective: Make Rotten Tomatoes score (threshold) predictions based on early released movie reviews. We use the predictions to make bets on Kalshi with the Kalshi API.
- Webscrape using Playwright
- Optimize runtime with async
- NLTK to preprocess web-scrapped text and label movie reviews as good or bad
- Naive Bayesian classifier to score a movie based on the reviews
- Decision Trees (Random Forest Classification, XGBoost) + Vectorization for better decisions
- Use API to see other people’s bets and place bets on kalshi
