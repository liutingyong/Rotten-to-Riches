import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from pathlib import Path

#might be a good idea to use nltk.corpus.movie_reviews for our movie reviews
#should we discard some stopwords?

#punkt is a pretrained sentence/word tokenizer
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
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = [t for t in tokens if t not in stop_words]
    
    # Lemmatize the words (aka converting word to base def)
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    
    return ' '.join(tokens)

#testing
directory = Path("src/webscraping/scraped_data")

for filename in directory.glob("*.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
        print(f"Data preprocessing file: {filename.name}")
        data = preprocess_text(text)

print(data)

