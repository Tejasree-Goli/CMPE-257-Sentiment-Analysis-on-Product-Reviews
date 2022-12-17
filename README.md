[CMPE 257 - Project Proposal.pdf](https://github.com/Tejasree-Goli/CMPE-257-Project/files/9925449/CMPE.257.-.Project.Proposal.pdf)
# CMPE-257: Sentiment Analysis on Product Reviews
## Machine Learning Project - Sentiment Analysis on Product Reviews

**Team Details - Team 1:** [Student name - GitHub username]

Teja Sree Goli - Tejasree-Goli,

Pranjali Seth - pranjaliseth,

Sai Teja Kandukuri - AIDANXhang,

Pavan Satyam - Pavan-Satyam,

**Dataset (Online Product Reviews Data)**: 

https://data.world/datafiniti/amazon-and-best-buy-electronics [from data.world]

https://data.world/datafiniti/grammar-and-online-product-reviews [from data.world]

The above data set is taken from Data World [primary source: Datafiniti’s Product Database]. The dataset contains around 7200 online reviews posted on e-commerce websites like Amazon, BestBuy and Walmart for various brand products. The data set reviews about 50 electronic products that contain 27 different attributes including reviews title, reviews text, reviews username, reviews rating, product name, manufacturer, brand, image urls, etc.
    
**Problem Statement**:

The world is drastically shifting towards the era of online shopping and social media. People find it extremely feasible and less time consuming to shop online by just sitting and shopping for anything and everything they need from the comfort of their homes. This leads to a minimal customer-manufacturer interaction and for this reason, it raises a concern for the suppliers to figure out their product performance and analyze feedback. A manufacturer requires constant feedback on how their products are doing in the market and the level of customer satisfaction that they are delivering. 

Therefore, to address this, we have a need for text and sentiment analysis of consumer feedback and product reviews that are purchased by consumers on online platforms. This approach will help in categorizing data based on certain attributes which will make it easier to analyze and observe the trends/reviews of products.

**Objective:** To determine whether a review on a given product is positive or negative by analyzing the text in user reviews on various products and performing classification of each product's reviews.

**Approach:** We will be implementing our model on supervised learning methods using word embeddings to predict or classify different sentiments. We plan on experimenting and exploring the data using KNN, SVMs, Random Forest Classifier or different BERT architectures.

**Data Cleaning and Preprocessing:** The raw data is cleaned by removing the rows which have null values for the columns: reviews.rating, reviews.title and reviews.text columns. The duplicate records in the dataset have been dropped. Stopwords have been removed using the Natural Language Toolkit (NLTK) module.

**Initial Findings:** Post data visualization, we observed the frequently used words by consumers in the reviews, frequency of the ratings, average rating of various brands and the correlation between variables in the data. The reviews are mostly positive, even on the brand/manufacturer level. Moreover, the text reviews are significantly higher for the positive ratings and most of the products are recommended by the users which shows an incline towards higher positive ratings in the data.

**Challenges:** There is imbalance in the dataset with a majority of positive ratings. Also, for the negative ratings, the review texts are minimal.
