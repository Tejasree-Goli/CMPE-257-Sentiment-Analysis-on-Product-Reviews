# -*- coding: utf-8 -*-
"""logistic_regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15UuPHz9cFhYTtHcKujjmccN3a8M2BXne

## Implementing Logistic Regression to predict Online Product reviews - rating to determine the sentiment
"""

#mounting drive
from google.colab import drive
drive.mount('/content/drive')

#importing the required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.tools as tls
import plotly.offline as py
color = sns.color_palette()
import plotly.graph_objs as go
py.init_notebook_mode(connected=True)
import plotly.tools as tls
import warnings
warnings.filterwarnings('ignore')
!pip install scikit-plot
!pip install imbalanced-learn
import scikitplot as skplt
import pickle

!pip install stop_words

# NLP modules
import nltk
import re 
import string
from nltk.corpus import stopwords
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from textblob import TextBlob , Word
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Wordcloud Modules
from wordcloud import WordCloud , STOPWORDS

color = sns.color_palette()
warnings.filterwarnings('ignore')
py.init_notebook_mode(connected=True)
nltk.download("stopwords")
nltk.download("all")

#loading the dataset
reviews_df=pd.read_csv('/content/drive/MyDrive/CMPE_257_Project/amazon_dataset/reviews_data.csv')
reviews_df.head(5)

reviews_df.shape

#Columns/attributes and their datatypes
reviews_df.dtypes

"""### Data Cleaning and Preprocessing"""

reviews_df.isnull().sum()

#dropping null values from the important columns used for model training

reviews_df = reviews_df.dropna(subset=['reviews.text']) #dropping null reviews text
reviews_df = reviews_df.dropna(subset=['reviews.title']) #dropping null reviews title
reviews_df = reviews_df.dropna(subset=['reviews.rating']) #dropping null ratings

reviews_df.shape

reviews_df.duplicated(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date']).sum()

#dropping the duplicated values based on review text, username, rating and date
reviews_df=reviews_df.drop_duplicates(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date'])

reviews_df.shape

reviews_df["full_review"] = reviews_df['reviews.title'].astype(str) +" "+ reviews_df["reviews.text"]

# preprocessing the reviews text (converting to lowercase, removing string literals)
reviews_df["full_review"] = (
    reviews_df["full_review"]
    .str.lower()                    
    .str.replace("[^\w\s]", "")
    .str.replace("\d+", "")
    .str.replace("\n", " ")
    .replace("\r", "")
    .str.replace("[^a-zA-Z0-9\s]", "")
)

reviews_df['full_review']

def word_cleaner(data):
    words = [re.sub("[^a-zA-Z]", " ", i) for i in data]
    words = [i.lower() for j in words for i in j.split()] # Split all the sentences into words
    words = [i for i in words if not i in set(stopwords.words("english"))] # Split all the sentences into words
    return words

word_frequency = pd.DataFrame(
    nltk.FreqDist(word_cleaner(reviews_df["full_review"])).most_common(25),
    columns=["Frequent_Words", "Frequency"],
)

#plotting the most frequently used words in the reviews texts.
plt.figure(figsize=(8, 8))
plt.xticks(rotation=90)
plt.title("Most frequently used words in reviews")
sns.barplot(x="Frequent_Words", y="Frequency", data=word_frequency)

# preprocessing reviews text
lemmatizer_output = WordNetLemmatizer()

reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: word_tokenize(x.lower()) # converting the text to lower case
)
reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: [word for word in x if word not in STOPWORDS] #getting rid of stopwords
)
reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: [lemmatizer_output.lemmatize(word) for word in x] #lemmatizes the words in reviews text
)
reviews_df["full_review"] = reviews_df["full_review"].apply(lambda x: " ".join(x))

reviews_df['full_review'].head(15)

"""### Visualization"""

#plotting wordcloud
from wordcloud import WordCloud, STOPWORDS

stopwords = set(STOPWORDS)


def show_wordcloud(data, title=None):
    wordcloud = WordCloud(
        background_color="black",
        stopwords=stopwords,
        max_words=250,
        max_font_size=45,
        scale=4,
        random_state=1,
    ).generate(str(data))

    fig = plt.figure(1, figsize=(16, 16))
    plt.axis("off")
    if title:
        fig.suptitle(title, fontsize=21)
        fig.subplots_adjust(top=2.1)

    plt.imshow(wordcloud)
    plt.show()


show_wordcloud(reviews_df["full_review"])

plt.figure(figsize=(8,8))
sns.histplot(data=reviews_df, x=reviews_df['reviews.rating'], discrete="True").set(title = "Frequency of each rating")

#review by brand
reviews_df.groupby(reviews_df['brand']).mean()['reviews.rating']

reviews_df["reviews_length"] = reviews_df["reviews.text"].apply(len)
sns.set(font_scale=2.0)

graph = sns.FacetGrid(reviews_df,col='reviews.rating',size=5)
graph.map(plt.hist,'reviews_length', range=[0, 500])

reviews_df['reviews.doRecommend'].fillna("N/A",inplace=True)

plt.figure(figsize = (8,8))
plt.title("Product recommendation from reviews")
reviews_df["reviews.doRecommend"].value_counts().plot.pie(autopct="%1.1f%%",textprops={'fontsize': 18})

plt.figure(figsize=(12,8))
plt.hist(reviews_df['reviews.numHelpful'],range=[1, 25], orientation='horizontal')
plt.title("Helpfulness of the reviews")
plt.xlabel("Count", fontsize=12)
plt.ylabel("No. of people that found the review helpful", fontsize=12)

sns.set(font_scale=1.4)
plt.figure(figsize = (10,5))
plt.title("Heat map - Correlation")
sns.heatmap(reviews_df.corr(),cmap='coolwarm',annot=True,linewidths=.5)

"""### Preprocessing and resampling data"""

# updating sentiments to classify in a linear model
reviews_df.loc[reviews_df['reviews.rating'] < 4, 'sentiment'] = 0 #0 indicating not a happy review
reviews_df.loc[reviews_df['reviews.rating'] >= 4, 'sentiment'] = 1 #1 indicating a happy review

reviews_df['sentiment']

from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

whole_text = reviews_df['full_review']
train_text = reviews_df['full_review']
y_sentiment = reviews_df['sentiment']

#vectorizing the input reviews text
word_vec = TfidfVectorizer(sublinear_tf = True, strip_accents = 'unicode', analyzer = 'word', token_pattern = r'\w{1,}', stop_words = 'english', ngram_range = (1, 1), max_features=10000)
word_vec.fit(whole_text)
train_features = word_vec.transform(train_text)

from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler, NearMiss
from collections import Counter

#Undersampling for linear model (lm)

nm_lm = NearMiss()
X_lm_undersample, y_lm_undersample = nm_lm.fit_resample(train_features, y_sentiment)

#Oversampling for linear model (lm)

smote_lm = SMOTE(random_state=42)
X_lm_oversample, y_lm_oversample= smote_lm.fit_resample(train_features, y_sentiment)

print('Original dataset shape after updating sentiment %s' % Counter(y_sentiment))
print('Undersampled dataset shape after updating sentiment %s' % Counter(y_lm_undersample))
print('Oversampled dataset shape after updating sentiment %s' % Counter(y_lm_oversample))

from sklearn.model_selection import train_test_split
X_lm_train_us, X_lm_test_us, y_lm_train_us, y_lm_test_us = train_test_split(X_lm_undersample, y_lm_undersample, test_size=0.3, random_state=101)
X_lm_train, X_lm_test, y_lm_train, y_lm_test = train_test_split(train_features, y_sentiment, test_size=0.3, random_state=101)
X_lm_train_os, X_lm_test_os, y_lm_train_os, y_lm_test_os = train_test_split(X_lm_oversample, y_lm_oversample, test_size=0.3, random_state=101)

from sklearn.linear_model import LogisticRegression

lr_us = LogisticRegression().fit(X_lm_train_us, y_lm_train_us)
lr_pred_us = lr_us.predict(X_lm_test_us)
print(lr_pred_us)
lr_us.score(X_lm_train_us, y_lm_train_us)

lr = LogisticRegression().fit(X_lm_train, y_lm_train)
lr_pred = lr.predict(X_lm_test)
print(lr_pred)
lr.score(X_lm_train, y_lm_train)

lr_os = LogisticRegression().fit(X_lm_train_os, y_lm_train_os)
lr_pred_os = lr_os.predict(X_lm_test_os)
print(lr_pred_os)
lr_os.score(X_lm_train_os, y_lm_train_os)

print("Training accuracy score on undersampled data: ", lr_us.score(X_lm_train_us, y_lm_train_us))
print("Training accuracy score on original data: ", lr.score(X_lm_train, y_lm_train))
print("Training accuracy score on oversampled data: ", lr_os.score(X_lm_train_os, y_lm_train_os))

"""To ensure that there is enough  data for building a good model, I applied resampling techniques. 

The training accuracy score for the models is close to a hundred percent. This implies that the error for the models on training is close to zero. This ensures that the model is learned properly. 
"""

# saving the models to use them for any further testing
filename = '/content/drive/MyDrive/CMPE_257_Project/logisticregression_undersampled.sav'
pickle.dump(lr_us, open(filename, 'wb'))
filename = '/content/drive/MyDrive/CMPE_257_Project/logisticregression.sav'
pickle.dump(lr, open(filename, 'wb'))
filename = '/content/drive/MyDrive/CMPE_257_Project/logisticregression_oversampled.sav'
pickle.dump(lr_os, open(filename, 'wb'))

from sklearn.metrics import classification_report
print("Classification report for Undersampled data using Logisitic Regression (Linear model).")
print(classification_report(y_lm_test_us, lr_pred_us, labels=[0,1]))
print("\nClassification report for Original (no resampling) data using Logisitic Regression (Linear model).")
print(classification_report(y_lm_test, lr_pred, labels=[0,1]))
print("\nClassification report for Oversampled data using Logisitic Regression (Linear model).")
print(classification_report(y_lm_test_os, lr_pred_os, labels=[0,1]))

"""The f1 score for oversampled data is good. For no resampling, the f1 score is low for class 0.

The testing accuracy or f1 score is close to a hundred. This implies that the error for out of training data is close to zero. This ensures that the errors for insample and out of sample data are similar, close to zero and the model is learned properly. 
"""

sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_lm_test_us, lr_pred_us, normalize=True, title = 'Confusion Matrix for Logistic Regression (undersampled)')
plt.show()

sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_lm_test, lr_pred, normalize=True, title = 'Confusion Matrix for Logistic Regression (no resampling)')
plt.show()

sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_lm_test_os, lr_pred_os, normalize=True, title = 'Confusion Matrix for Logistic Regression (oversampling)')
plt.show()

probas3 = lr.predict_proba(X_lm_test_us)
sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_precision_recall_curve(y_lm_test_us, probas3, title = 'Precision-Recall Curve for Logistic Regression (undersampled)')
plt.show()

probas4 = lr.predict_proba(X_lm_test)
sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_precision_recall_curve(y_lm_test, probas4, title = 'Precision-Recall Curve for Logistic Regression (unsampled)')
plt.show()

probas5 = lr_os.predict_proba(X_lm_test_os)
sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_precision_recall_curve(y_lm_test_os, probas5, title = 'Precision-Recall Curve for Logistic Regression (oversampled)')
plt.show()

"""Even from visualizations it is observed that without resampling, the predictions for class 0 are not satisfactory.

The curves for the model that is trained on oversampled data is better and more consistent in classification
"""

from sklearn.metrics import log_loss
probas5_us = lr_us.predict_proba(X_lm_test_us)
probas5_ = lr.predict_proba(X_lm_test)
print("Log loss for undersampled data on Logistic Regression")
print(log_loss(y_lm_test_us, probas5_us))
print("\nLog loss for original (no resampling) data on Logistic Regression")
print(log_loss(y_lm_test, probas5_))
print("\nLog loss for oversampled data on Logistic Regression")
print(log_loss(y_lm_test_os, probas5))

"""The loss is low for this model. On the given dataset, the loss is closer to zero.

### Custom test cases
"""

# giving some custom test inputs to evaluate the model
custom_test_inputs = ["so satisfied with the purchase good product works well", "this device feels ok it works fine", "really disappointed with the purchase defective product not working", "used to be good but since the change the worst product ever", "used to be bad but from when it was updated it is the best product ever"]
inputs_vec = word_vec.transform(custom_test_inputs)

# testing on rfc_os model (Logisitic Regression model that was trained on the oversampled data.)
custom_preds = lr_us.predict(inputs_vec)
for index in range(len(custom_test_inputs)):
  if custom_preds[index] == 0:
    print("The rating predicted for the review - \"", custom_test_inputs[index], "\" is : ", custom_preds[index], " (Not satisfied/Negative review)")
  elif custom_preds[index] == 1:
    print("The rating predicted for the review - \"", custom_test_inputs[index], "\" is : ", custom_preds[index], " (Satisfied/Positive review)")

"""On undersampled data, the rating predictions on this version of the model are not accurate."""

# testing on rfc_os model (Logisitic Regression model that was trained on the oversampled data.)
custom_preds = lr_os.predict(inputs_vec)
for index in range(len(custom_test_inputs)):
  if custom_preds[index] == 0:
    print("The rating predicted for the review - \"", custom_test_inputs[index], "\" is : ", custom_preds[index], " (Not satisfied/Negative review)")
  elif custom_preds[index] == 1:
    print("The rating predicted for the review - \"", custom_test_inputs[index], "\" is : ", custom_preds[index], " (Satisfied/Positive review)")

"""On Oversampled data, the rating predictions on this version of the model are pretty accurate."""

