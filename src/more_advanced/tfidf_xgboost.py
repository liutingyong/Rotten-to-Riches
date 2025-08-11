#now using tf-idf for xgboost, which does the actual predictions
#we should tune later


from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import joblib
import glob

from pathlib import Path

directory = Path("src/webscraping/scraped_data")
text_paths = glob.glob(str(directory / "*.txt"))
text_files = [Path(text).stem for text in text_paths]

y = [0, 1, 1, 0] #defo need more data

X_train, X_test, Y_train, Y_test = train_test_split(text_paths, test_size=0.2, random_state=42, stratify=y)

#honestly we can change the parameters later, idk if these are the best
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(input='filename', stop_words='english', lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.95, max_features=30000)),
    ("xgb", XGBClassifier(objective='binary:logistic', n_estimators=400, learning_rate=0.05, max_depth=6, subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0, tree_method='hist', eval_metric='logloss', n_jobs=-1))
])

pipe.fit(X_train, Y_train)

pred = pipe.predict(X_test)
#positive class probability, since positive class is 1
probability = pipe.predict_proba(X_test)[:1]
print(f"Accuracy: {accuracy_score(Y_test, pred, digits=4)}")

#we can test with new files later