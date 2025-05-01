# forum-crawler

This script scrapes data from the website `https://forum.alzheimers.org.uk/` and stores the data into a csv file.

This forum consists of several categories, each sub-forum belongs to a category.  
Each sub-forum has a list of threads where discussions take place.  
Each thread contains the posts of the users in chronological order.  
A post contains a message from a user.
A post can reference or quote another post.

The web scraping python library called BeautifulSoup was used to get and parse the html of the website and then extract the relevant data.
