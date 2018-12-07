# SI507-FINALPROJECT-JINGWANG

Jing Wang 
WJINGCC

## 1. Overview

The goal of the project is to get data from TripAdvisor and Yelp on Ann Arbor's restaurant information by using the Python skills including website scraping and crawling, API using, Database usage, Flask and so on. The original data are from TripAdvisor and Yelp Fusion API. Then data are stored into a database for query and data visualization. A Flask app is used to construct the interaction with end users. In this app, end users can sort the data by different items, view the maps for restaurants' location, check the prices distribution and get ratings comparision.

## 2. Data Source

2.1 TripAdvisor is an America-based website providing hotel and restaurant reviews. This project only focuses on the restaurants in Ann Arbor. Multiple level web pages have been scraped and crawled (including restaurant list page and each restaurant's details page) by using BeautifulSoup. The information of the top 100 restaurants based on ratings has been cached in a JSON file named "cache_tripa.json". https://www.tripadvisor.com/RestaurantSearch-g29556-Ann_Arbor_Michigan.html#EATERY_LIST_CONTENT

2.2 Yelp is a platform that provides restaurants' information/reviews. Users can get relevant information by inputting keywords (like a restaurant's name), location, category, price level, etc. Tool to get the data: Yelp Fusion API, which requires API key. ** API documentation homepage: https://www.yelp.com/developers/documentation/v3 ** Search API documentation: https://www.yelp.com/developers/documentation/v3/business_search The information of 100 restaurants has been cached in a JSON file named "cache_yelp.json".

## 3. Instructions

To successfully run this program, you need to do the following things:

3.1 IMPORTANT: get a client id and API key from Yelp. You can apply for authentication from Yelp API using the link below or find my secret data in the file that I submitted through Canvas. "https://www.yelp.com/developers/v3/manage_app"
3.2 Create a "secrets.py" file and put your client id and API key into it. The content format is like this: client_id = "" api_key = ""
3.3 Use python3 to run 'SI507F17_finalproject.py'
3.4 Refer to the requirements.txt file and get all the required modules ready
3.5 To see the visualized results and launch the predefined graphs, you may also need a Plotly account, here is the link to get started with Plotly: https://plot.ly/python/getting-started/

## 4. Project Structure
My project consists of three Python files. The flask codes are in "app.py", the main class and functions codes are in "module.py", and "test.py" is created to test if the data access, storage, and processing can work correctly.

A class "Restaurant" has been defined to facilitate the web scraping function and database creation.
A function "get_info_tripa(page="")" is defined for crawling and scraping the web pages of TripAdvisor. The returned results is a list of Restaurant instances.
A function "get_info_yelp(name)" is defined to get a restaurant's information using Yelp Fusion API based on the restaurant's name.
A database named "Final_Project.db" with three tables ("Restaurants", "Ratings" and "Detailinformation") has been created to present the data gotten from TripAdvisor and Yelp.
A website has been created using Flask. A web form has been created to present the top50 restaurants in Ann Arbor and end users can sort the data by different items and sequence. Five graphs created by Plotly offline (including a scatter map, a grouped bar chart, a pie chart, a map chart and a table chart) integrated into webpages are defined to visualize data.
Two JSON files ("cache_tripa.json" and "cache_tripa.json") should be created to cache data. A CSV file will display the information regarding ratings and reviews for 100+ restaurants in Ann Arbor.

## 5. Interactions

Web page is used to present the data.

Link "Ann Arbor Top50 Restaurants" is presenting the TOP50 restaurants ranked by TripAdvisor. The restaurant name, address, phone number, ranking, rating, category, review number are listed inside. Users can sort the data by selecting different items and sequence. 

Link "Map for Ann Arbor Top50 Restaurants" is showing the locations for the TOP50 restaurants.

Link "Top50 Restaurants Categories Pie Chart" indicates the categories distribution and we can see the variety of the cuisines.

Link "Ratings Distribution Comparison" provides the comparison between TripAdvisor and Yelp for ratings. You can see different ratings provided by different organizations for the same restaurant.

Link "Price Range Status" gives the view for the price distribution of the restaurants. Most of them are in middle level.

Link "Ann Arbor Top50 Restaurants Table" is a table view to check the detail information of the TOP50 restaurants.
