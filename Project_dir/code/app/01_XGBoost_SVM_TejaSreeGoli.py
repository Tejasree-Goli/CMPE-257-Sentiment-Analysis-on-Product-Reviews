# -*- coding: utf-8 -*-
"""255_project_XGBoost.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iEAlEYo6cQuXWS6wFrmxuRacxanlWOWM
"""

from google.colab import drive
drive.mount('/content/drive')

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

reviews_df=pd.read_csv('/content/drive/MyDrive/CMPE_257_Project/amazon_dataset/reviews_data.csv')
reviews_df.head(5)

reviews_df.shape

#Columns/attributes and their datatypes
reviews_df.dtypes

reviews_df.isnull().sum()

reviews_df = reviews_df.dropna(subset=['reviews.text']) #dropping null reviews text
reviews_df = reviews_df.dropna(subset=['reviews.title']) #dropping null reviews title
reviews_df = reviews_df.dropna(subset=['reviews.rating']) #dropping null ratings

reviews_df.shape

reviews_df.duplicated(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date']).sum()

reviews_df=reviews_df.drop_duplicates(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date'])

reviews_df.shape

reviews_df["full_review"] = reviews_df['reviews.title'].astype(str) +" "+ reviews_df["reviews.text"]

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

plt.figure(figsize=(8, 8))
plt.xticks(rotation=90)
plt.title("Most frequently used words in reviews")
sns.barplot(x="Frequent_Words", y="Frequency", data=word_frequency)

lemmatizer_output = WordNetLemmatizer()

reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: word_tokenize(x.lower())
)
reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: [word for word in x if word not in STOPWORDS]
)
reviews_df["full_review"] = reviews_df["full_review"].apply(
    lambda x: [lemmatizer_output.lemmatize(word) for word in x]
)
reviews_df["full_review"] = reviews_df["full_review"].apply(lambda x: " ".join(x))

reviews_df['full_review'].head(15)

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

# reviews_df = reviews_df.replace(np.nan, 0)
# reviews_dfm = reviews_df.groupby(reviews_df["brand"]).mean()["reviews.rating"]
# plt.title("Average Ratings per brand")
# plt.xticks(fontsize=8)
# reviews_dfm.plot(
#     kind="bar",
#     ylabel="Mean Rating",
#     xlabel="Brand Manufacturer",
#     figsize=(9, 9),
#     color="limegreen",
# )

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





!pip install imbalanced-learn

from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler, NearMiss
from collections import Counter

from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer

whole_text = reviews_df['full_review']
train_text = reviews_df['full_review']
y_ratings = reviews_df['reviews.rating']

word_vec = TfidfVectorizer(sublinear_tf = True, strip_accents = 'unicode', analyzer = 'word', token_pattern = r'\w{1,}', stop_words = 'english', ngram_range = (1, 1), max_features=10000)
word_vec.fit(whole_text)
train_features = word_vec.transform(train_text)

train_features

#Undersampling

nm = NearMiss()
X_undersample, y_undersample = nm.fit_resample(train_features, y_ratings)

#Oversampling

smote = SMOTE(random_state=42)
X_oversample, y_oversample= smote.fit_resample(train_features, y_ratings)

print('Original dataset shape %s' % Counter(y_ratings))
print('Undersampled dataset shape %s' % Counter(y_undersample))
print('Oversampled dataset shape %s' % Counter(y_oversample))

from sklearn.model_selection import train_test_split
X_train_us, X_test_us, y_train_us, y_test_us = train_test_split(X_undersample, y_undersample, test_size=0.3, random_state=101)
X_train, X_test, y_train, y_test = train_test_split(train_features, y_ratings, test_size=0.3, random_state=101)
X_train_os, X_test_os, y_train_os, y_test_os = train_test_split(X_oversample, y_oversample, test_size=0.3, random_state=101)

"""XGBoost"""

import xgboost as xgb

# for undersampled data
xgb_us = xgb.XGBClassifier()
xgb_us.fit(X_train_us,y_train_us)
xgb_pred_us = xgb_us.predict(X_test_us)
print(xgb_pred_us)
xgb_us.score(X_train_us, y_train_us)

# for normal data
xgbc = xgb.XGBClassifier()
xgbc.fit(X_train,y_train)
xgb_pred = xgbc.predict(X_test)
print(xgb_pred)
xgbc.score(X_train, y_train)

# for oversampled data
import xgboost as xgb
xgb_os = xgb.XGBClassifier()
xgb_os.fit(X_train_os,y_train_os)
xgb_pred_os = xgb_os.predict(X_test_os)
print(xgb_pred_os)
xgb_os.score(X_train_os, y_train_os)

# filename = '/content/drive/MyDrive/CMPE_257_Project/amazon_dataset/xgb_us.sav'
# pickle.dump(xgb_us, open(filename, 'wb'))
# filename = '/content/drive/MyDrive/CMPE_257_Project/amazon_dataset/xgbc.sav'
# pickle.dump(xgbc, open(filename, 'wb'))
# filename = '/content/drive/MyDrive/CMPE_257_Project/amazon_dataset/xgb_os.sav'
# pickle.dump(xgb_os, open(filename, 'wb'))

# metrics calculations
from sklearn.metrics import classification_report
print("Classification report for Undersampled data using XGBoostClassifier.")
print(classification_report(y_test_us, xgb_pred_us, labels=[1, 2, 3, 4, 5]))
print("\nClassification report for Original (no resampling) data using XGBoostClassifier.")
print(classification_report(y_test, xgb_pred, labels=[1, 2, 3, 4, 5]))
print("\nClassification report for Oversampled data using XGBoostClassifier.")
print(classification_report(y_test_os, xgb_pred_os, labels=[1, 2, 3, 4, 5]))

# confusion matrix for over-sampled data
sns.set(rc={'figure.figsize':(6,6)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_test_os, xgb_pred_os, normalize=True, title = 'Confusion Matrix for XGBoostClassifier (oversampled)')
plt.show()

# precision-recall plot for oversampled data
probas4 = xgb_os.predict_proba(X_test_os)
sns.set(rc={'figure.figsize':(6,6)})
sns.set(font_scale=1)
skplt.metrics.plot_precision_recall_curve(y_test_os, probas4)
plt.show()

# loss calculations
from sklearn.metrics import log_loss
probas4_us = xgb_us.predict_proba(X_test_us)
probas4_ = xgbc.predict_proba(X_test)
print("Log loss for undersampled data on XGBoostClassifier")
print(log_loss(y_test_us, probas4_us))
print("\nLog loss for original (no resampling) data on XGBoostClassifier")
print(log_loss(y_test, probas4_))
print("\nLog loss for oversampled data on XGBoostClassifier")
print(log_loss(y_test_os, probas4))

"""SVM Model"""

from sklearn.svm import SVC
svc_model = SVC(kernel='linear', random_state=32)
svc_model.fit(X_train, y_train)
svc_pred=svc_model.predict(X_test)
print(svc_pred)
svc_model.score(X_train, y_train)

# metrics calculations
from sklearn.metrics import classification_report
print("\nClassification report for Original (no resampling) data using SVM.")
print(classification_report(y_test, svc_pred, labels=[1, 2, 3, 4, 5]))

# confusion matrix for over-sampled data
sns.set(rc={'figure.figsize':(6,6)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_test, svc_pred, normalize=True, title = 'Confusion Matrix for SVM')
plt.show()