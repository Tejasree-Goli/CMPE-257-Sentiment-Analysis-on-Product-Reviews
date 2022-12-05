# -*- coding: utf-8 -*-
"""06_Bernouli_Pavan_Satyam.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TL5XLIkKLj7yQiwRd-xbpHyaRx88N21l
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

reviews_df=pd.read_csv('/content/drive/MyDrive/cmpe257/merged.csv')
reviews_df.head(5)

reviews_df.shape

#Columns/attributes and their datatypes
reviews_df.dtypes

reviews_df.isnull().sum()

reviews_df = reviews_df.dropna(subset=['reviews.text']) #dropping null reviews text
reviews_df = reviews_df.dropna(subset=['reviews.title']) #dropping null reviews title
reviews_df = reviews_df.dropna(subset=['reviews.rating']) #dropping null ratings

reviews_df.shape

"""Checking the duplicate rows and dropping them"""

reviews_df.duplicated(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date']).sum()

reviews_df=reviews_df.drop_duplicates(subset=['reviews.text', 'reviews.username', 'reviews.rating', 'reviews.date'])

reviews_df.shape

"""Making title and review as one sentence"""

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

"""Removing other characters other than letters"""

def word_cleaner(data):
    words = [re.sub("[^a-zA-Z]", " ", i) for i in data]
    words = [i.lower() for j in words for i in j.split()] # Split all the sentences into words
    words = [i for i in words if not i in set(stopwords.words("english"))] # Split all the sentences into words
    return words

"""Finding most frequent words"""

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

"""#Data Fitting"""

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

"""#Undersampling"""

nm = NearMiss()
X_undersample, y_undersample = nm.fit_resample(train_features, y_ratings)

"""#Oversampling

"""

smote = SMOTE(random_state=42)
X_oversample, y_oversample= smote.fit_resample(train_features, y_ratings)

print('Original dataset shape %s' % Counter(y_ratings))
print('Oversampled dataset shape %s' % Counter(y_oversample))

"""#Bernouli"""

reviews_df = reviews_df[['full_review','reviews.rating']] 

# Converting into binary classification problem

reviews_df['reviews.rating'] = reviews_df['reviews.rating'].apply(lambda x: 0 if x<5 else 1)

# Shape of dataset


# Overview of data
print("\nOverview of data: ")
reviews_df.info

whole_text = reviews_df['full_review']
train_text = reviews_df['full_review']
y_ratings = reviews_df['reviews.rating']

word_vec = TfidfVectorizer(sublinear_tf = True, strip_accents = 'unicode', analyzer = 'word', token_pattern = r'\w{1,}', stop_words = 'english', ngram_range = (1, 1), max_features=10000)
word_vec.fit(whole_text)
train_features = word_vec.transform(train_text)

train_features

nm = NearMiss()
X_undersample, y_undersample = nm.fit_resample(train_features, y_ratings)

smote = SMOTE(random_state=42)
X_oversample, y_oversample= smote.fit_resample(train_features, y_ratings)

print('Original dataset shape %s' % Counter(y_ratings))
print('Oversampled dataset shape %s' % Counter(y_oversample))

from sklearn.model_selection import train_test_split
X_train_us, X_test_us, y_train_us, y_test_us = train_test_split(X_undersample, y_undersample, test_size=0.3, random_state=101)
X_train, X_test, y_train, y_test = train_test_split(train_features, y_ratings, test_size=0.3, random_state=101)
X_train_os, X_test_os, y_train_os, y_test_os = train_test_split(X_oversample, y_oversample, test_size=0.3, random_state=101)

from sklearn.naive_bayes import BernoulliNB
classifier = BernoulliNB()
classifier.fit(X_train, y_train)
classifier.fit(X_train_us, y_train_us)
classifier.fit(X_train_os, y_train_os)

y_pred = classifier.predict(X_test)
y_pred_us=classifier.predict(X_test_us)
y_pred_os=classifier.predict(X_test_os)
from sklearn.metrics import accuracy_score
acc = accuracy_score(y_test, y_pred)
acc_us = accuracy_score(y_test_us, y_pred_us)
acc_os = accuracy_score(y_test_os, y_pred_os)
print('accuracy:',acc)
print('accuracy:',acc_us)
print('accuracy:',acc_os)

from sklearn.metrics import confusion_matrix,f1_score
conf_mat = confusion_matrix(
        y_test, y_pred)
print(conf_mat)

"""Training Score"""

y_pred_train_us= classifier.predict(X_train_us)
print(f1_score(y_train_us, y_pred_train_us))



conf_mat = confusion_matrix(
        y_test_us, y_pred_us)
sns.set(rc={'figure.figsize':(10,10)})
sns.set(font_scale=1)
skplt.metrics.plot_confusion_matrix(y_test_us, y_pred_us, normalize=True, title = 'Confusion Matrix for KneighborsClassifier (undersampled)')
plt.show()
print(conf_mat)

"""Testing score"""

print(f1_score(y_test, y_pred))
print(f1_score())

conf_mat = confusion_matrix(
        y_test_os, y_pred_os)
print(conf_mat)

"""#Test cases"""

custom_test = word_vec.transform(["so satisfied with the purchase good product works well", "this device feels ok it works fine", "really disappointed with the purchase defective product not working", "used to be good but since the change the worst product ever", "used to be bad but from when it was updated it is the best product ever"])

classifier.predict(custom_test)



