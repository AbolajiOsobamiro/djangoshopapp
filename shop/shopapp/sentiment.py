from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

lexicon_file = os.path.join(os.path.dirname(__file__), 'vader_lexicon.txt')

sia = SentimentIntensityAnalyzer(lexicon_file=lexicon_file)

def analyze_review(review_text):
    # Analyze the sentiment of the review
    sentiment = sia.polarity_scores(review_text)
    compound_score = sentiment['compound']
    # Determine if the sentiment is positive, negative, or neutral
    if compound_score >= 0.05:
        sentiment_category = 'POSITIVE'
    elif compound_score <= -0.05:
        sentiment_category = 'NEGATIVE'
    else:
        sentiment_category = 'NEUTRAL'
    return sentiment_category, compound_score
    

