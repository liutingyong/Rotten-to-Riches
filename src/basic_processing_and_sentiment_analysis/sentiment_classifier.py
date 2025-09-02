import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from pathlib import Path
#should we discard some stopwords?

#punkt is a pretrained sentence/word tokenizer, splits better (knows abbreviations, punctuation, etc.)
nltk.download('punkt')
#stopwords are irrelevant words that don't contribute to meaning but important for grammar like i, me, the, etc.
nltk.download('stopwords')
#synonym/antonym 
nltk.download('wordnet') #wordnet is lexical database for english

def preprocess_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation and stopwords
    #stopwords are actually in multiple languages
    #set for faster lookup
    #string.punctuation is a string containing all punctuation characters
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = [t for t in tokens if t not in stop_words]
    
    # Lemmatize the words (aka converting word to base def)
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    
    #return ' '.join(tokens)
    return tokens

#testing
directory = Path("src/webscraping/scraped_data")

for filename in directory.glob("*.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        print(f"Data preprocessing file: {filename.name}")
        data = preprocess_text(text)

#print(data)

def extract_features(words):
    return {word: True for word in words}

from nltk.corpus import movie_reviews
nltk.download('movie_reviews')
import random

#categories are positiev or negative
docs = []
for category in movie_reviews.categories():
    #this part gets all the fileids of a specifi ccategory
    for fileid in movie_reviews.fileids(category):
        #movie_reviews.words(fileid) gets all the words in that file (tokenized)
        #docs is a list of tuples, where each tuple contains a list of words and their corresponding category (pos, neg)
        docs.append((list(movie_reviews.words(fileid)), category))

random.shuffle(docs)
featuresets = []
for (words, label) in docs:
    try:
        featuresets.append((extract_features(preprocess_text("".join(words))), label))
    except Exception as e:
        print(f"Error processing {words}: {e}")
#featuresets = [(extract_features(preprocess_text(words)), label) for (words, label) in docs]
#do we split in half or just split by first 1500 and rest?
training_set = featuresets[:1500]
testing_set = featuresets[1500:]

#naivebayesclassifier, supervised ML (learns from labeled data)
#bayes theorem for probability calcs
#naive bc assumes independence between features
#counts how often each word appears in each category (pos, neg)
from nltk import NaiveBayesClassifier
print(f'# of training examples: {len(training_set)}')
print(f'# of featuresets: {len(featuresets)}')
classifier = NaiveBayesClassifier.train(training_set)
#test accuracy
print(f"Classifier accuracy: {nltk.classify.accuracy(classifier, testing_set)}")


classifications = []
for filename in directory.glob("*.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        print(f"Classifying file: {filename.name}")
        features = extract_features(preprocess_text(text))
        label = classifier.classify(features)
        if label == 'pos':
            classifications.append(1)
        else:
            classifications.append(0)
        print(f"Sentiment for {filename.name}: {label}")

#we can improve accuracy by using more data, better preprocessing, or more advanced models

#change our current data to be more relevant to our use case so we can make actual bets
percentage_pos = classifications.count(1) / len(classifications)
print(f"Percentage of positive sentiment: {percentage_pos:.2%}")
if percentage_pos > 0.6:
    print("Overall Sentiment: Positive")
elif percentage_pos < 0.4:
    print("Overall Sentiment: Negative")