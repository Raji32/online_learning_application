from textblob import TextBlob
from transformers import pipeline
from models import Review


# Sentiment Analysis function
def analyze_sentiment(review_text):
    blob = TextBlob(review_text)
    sentiment_score = blob.sentiment.polarity
    
    if sentiment_score > 0:
        return 'positive'
    elif sentiment_score < 0:
        return 'negative'
    else:
        return 'neutral'

# Summarization function
summarizer = pipeline("summarization")

def summarize_reviews(reviews_text):
    full_text = " ".join(reviews_text)
    summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Calculate review summary for a course
def calculate_review_summary(course_id, db):
    reviews = db.session.query(Review).filter_by(course_id=course_id).all()

    reviews_text = [review.comment for review in reviews]
    sentiments = [analyze_sentiment(review.comment) for review in reviews_text]
    
    # Summarize all reviews
    summary = summarize_reviews(reviews_text)
    
    # Calculate the overall sentiment
    overall_sentiment = max(set(sentiments), key=sentiments.count)
    
    return {
        "sentiments": sentiments,
        "overall_sentiment": overall_sentiment,
        "summary": summary
    }
