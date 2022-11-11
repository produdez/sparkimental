import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle

nltk.download('vader_lexicon')

# Model: https://medium.com/@b.terryjack/nlp-pre-trained-sentiment-analysis-1eb52a9d742c
model = SentimentIntensityAnalyzer() 
model_name = type(model).__name__

# Pickle serialization
pickle_filename = f"./models/{model_name}.pkl"
pickle_out = open(pickle_filename, "wb")
pickle.dump(model, pickle_out)
pickle_out.close()
print('Model saved to: ', pickle_filename)
