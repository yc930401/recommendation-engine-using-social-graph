# Community Detection in Social Graphs and its Application 

## Section 1: Background

Detecting communities and the influencers within that community is a key in analysis of social networks. There are multiple approaches to community detection and determining who are the influencers **find papers pls**. Its applications ranges from biology to sociology. In our project, we seek to detect communities in the Foursquare social network and its influencers. We also aim to assess the effectiveness of using the output of such an analysis in a recommendation engine. 

## Section 2: Motivation

Our motivation primarily arise from the fact that food is a favourite past time in Singapore. While there is an abundance of information on where are some of the nicer foods on the island, there are limited ways to discover novel cuisines or restaurants based on one's preferences. Given that social network data are now readily available for analysis, we can now detect the various communities present in Singapore when it comes to food, and perhaps use the information for making recommendations.
 
 The output of the analysis can then be used by bloggers to help decide on the cuisines to cover so as to appeal to certain communities, or even in a recommendation engine as part of a web portal or mobile application.  

## Section 3: About the Dataset

Our dataset will be retrieved from Foursquare through 2 methods. 

* **Foursqure API** - For users, venues and photos data
* **Web Scraping** - For reviews, not available via the Foursquare API. 

The records used for this analysis are summarized below:

| Data Set :                | # of Records|
| :-------------|:-------------:|
| Users : | 16,736|
| Venues : |132,308  |
| Photos : |132,308  |
| Tips? Reviews? : |132,308  |

**<Insert details on user, venues, photos etc>**

## Section 4: Methods 

Data retrieved from Foursquare will be transformed into adjancency matrices with each row representing users and columns representing restaurants or photos. The user-restaurant matrix will be constructed based on the # of check-ins a user has at a particular restaurant. Photos will be first classified into cuisines (eg. Indian, Chinese etc), people or others.
   
Following which, clustering or dimension reduction will be applied to detect communities within using the above adjacency matrices. The result of the clustering or dimension reduction will then be appended to the user attributes to form the data set to be used for recommendations. A high level representation of the data set is shown below. 

![dataset](img_proposal/proposal_clus.png)

This will also help us answer questions such as:
* What kind of photo (food / face / random) does one tend to share of restaurant given one's membership in a community?
* Are the different communities based on photos and restaurants visited?

Using the data set prepared, we will attempt to create a recommendation engine for the purpose of suggesting restaurants based on the community memberships of the users and their attributes. This will be done by leveraging machine learning algorithms. 
 
 Depending on the results, we may further enrich the data set to contain the user's past check-ins in making recommendations. 

## Section 5: Evaluation and Comments

Evaluation will be done by comparing the recommendations to the actual check-ins of the users. Precision and recall will be used as the measures for evaluation. We will then comment on the effectiveness of using our methods for a recommendation engine. 

## Section 6: Reference
[1] 

[2]

