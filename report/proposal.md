# Community Detection in Social Graphs and its Application

## Section 1: Background

Detecting communities and the influencers within a community is key in the analysis of social networks. There are multiple approaches to community detection and determining who the influencers are **find papers pls**. Its applications ranges from biology to sociology. In our project, we seek to detect communities in the Foursquare social network. We also aim to assess the effectiveness of using the output of such an analysis by applying it into a recommendation engine.

## Section 2: Motivation

Our motivation arises from the fact that food is a favourite past time in Singapore. While there is an abundance of information on great food places on this island, there are limited ways to discover novel cuisines or restaurants based on one's preferences. Given that social network data are now readily available for analysis, we can now detect the various communities present in Singapore when it comes to food, and perhaps use this information to make recommendations.

The output from the analysis can then be used by bloggers to help decide which cuisines to cover so as to appeal to certain communities, or even applied in a recommendation engine as part of a web portal or mobile application.  

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

Following which, clustering or dimension reduction will be applied to detect communities within, using the above adjacency matrices. The result of the clustering or dimension reduction will then be appended to the user attributes to form the data set to be used for recommendations. A high level representation of the data set is shown below.

![dataset](img_proposal/proposal_clus.png)

This will also help us answer questions such as:
* What kind of photo (food / face / random) does one tend to share of restaurant given one's membership in a community?
* Are the different communities based on photos and restaurants visited?

Using the data set prepared, we will attempt to develop a recommendation engine with the purpose of suggesting restaurants based on community memberships of the users and their attributes. This will be done by leveraging on machine learning algorithms.

Depending on the results, we may further enrich the data set to contain the user's past check-ins in making recommendations.

## Section 5: Evaluation and Comments

Evaluation will be done by comparing the recommendations to the actual check-ins of the users. The precision and recall method will be used as measures for evaluation. We will then comment on the effectiveness of using our methods for a recommendation engine.

## Section 6: Reference
[1] Effects of the Presence of Others on Food Intake: A Normative Interpretation from http://web.a.ebscohost.com.libproxy.smu.edu.sg/ehost/pdfviewer/pdfviewer?sid=6daab7ae-3314-4ca7-a929-1b67c5d0d35d%40sessionmgr4006&vid=1&hid=4101 retrieved on 25 Jun 17

[2]
