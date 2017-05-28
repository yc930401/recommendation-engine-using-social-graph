###### [proposal-draft01]
# An Exploratory Study Using Graph Theory to Classify Images

## Section 1: Background
Reddit.com is a community news site where it empowers users to share any content such as stories, images, and links - related to a topic that he/she is interested it. The others are able to evaluate, vote, and comments on these posts. These ratings are then used to promote contents and gain higher visibility.

## Section 2: Objective
It is the priority of social sites to increase traffics to the site. Thus, it is crucial for reddit.com to identify the interest of the communities and users, so as to design strategies to attract more users to the site.

In this project, we aim to help reddit.com to do so by identifying (A) existing communities, and (B) members in each of these communities via;

1. Number, size, and strength of the existing communities
2. Topics that these communities are interested in
3. Traits / characteristics of key / influential members
4. Any common interests of these members in other communities

via focusing on content that have been re-submitted multiple times, so as to determine the factor(s) that determine the popularity of the content.

We will do so by analyzing the images that have been submitted/resubmitted with multiple titles to multiple communities - and thereafter; the votes, comments, and users related to posts. Images are the dominant form of content that were shared on the site, and often; it is the images that drive the popularity of the sharing; instead of the title.[1]

## Section 3: About the Dataset
This dataset is downloaded from snap.stanford.edu for research purposes. It is made up submissions of images that have been submitted to reddit.com multiple times. The dataset includes the these fields; (1) time of submission, (2) name of user, (3) name of community, (4) number of ratings (positive / negative), (5) submission titles, (6) no. of comments received, (7) html of comment pages.

The statistics related to the data as below;

| Timespan :                | July 2008 - Jan 2013|
| :-------------|:-------------:|
| Number of unique images : | 16,736|
| No. of submissions : |132,308  |

## Section 4: Analysis Approach

The overview of the methodology to meet the objective of the analysis as below;

[add a diagram of overview]

<HY: we need to discuss on how to implement>
1. prepare data (may want to update data by downloading from API)
2. apply graph theory to identify the community (image, meta data, users)
3. machine learning to classify images (unsupervised)
4. compare the results

### 4.1: Data Preparation

<in html for each comment : need to list down how to clean each of the file>

### 4.2: blah blah

### 4.3: blah blah blah

## Section 5: Validation of Results

## Section 6: Reference
1. H. Lakkaraju, J. J. McAuley, J. Leskovec What's in a name? Understanding the interplay between titles, content, and communities in social media. ICWSM, 2013.

2. Web data: Reddit Submissions, from https://snap.stanford.edu/data/web-Reddit.html retrieved on 28 May 17.
