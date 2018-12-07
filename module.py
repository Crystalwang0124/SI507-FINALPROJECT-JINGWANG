import requests
import webbrowser
import secrets
import sqlite3
import json
import csv
#import plotly.plotly as py
import plotly.graph_objs as go
from bs4 import BeautifulSoup
import numpy as np
from plotly.offline import plot

# import Yelp Fusion API keys
CLIENT_ID = secrets.Client_ID
API_KEY = secrets.API_Key

############### Build Class Object ############################
class Restaurant():
    def __init__(self, name, rating1="0", price="0", url=None):
        self.name = name
        self.rating1 = rating1
        self.price = price
        self.url = url

        self.category = ""
        self.reviews = "0"
        self.rating2 = "0"
        self.street = "123 South St."
        self.city = "Ann Arbor"
        self.state = "MI"
        self.zip = "48111"
        self.lat = "0"
        self.lng = "0"

    def __str__(self):
        r_str = "{}: {}, {}, {}({})".format(self.name, self.street, self.city, self.state, self.zip)
        return r_str


############ Set Up Cache Files #############
CACHE_TRIPA = "cache_tripa.json"
CACHE_YELP = "cache_yelp.json"


############ Using Cache to Scrape & Crawl Data ############
try:
    cache_tripa_file = open(CACHE_TRIPA, "r")
    cache_tripa_contents = cache_tripa_file.read()
    TRIPA_DICTION = json.loads(cache_tripa_contents)
    cache_tripa_file.close()
except:
    TRIPA_DICTION = {}

def get_unique_key(url):
    return url

def make_request_using_cache_crawl(url):
    unique_ident = get_unique_key(url)

    if unique_ident in TRIPA_DICTION:
        return TRIPA_DICTION[unique_ident]
    else:
        resp = requests.get(url)
        TRIPA_DICTION[unique_ident] = resp.text 
        dumped_json_cache_crawl = json.dumps(TRIPA_DICTION,indent=4)
        fw = open(CACHE_TRIPA,"w")
        fw.write(dumped_json_cache_crawl)
        fw.close() 
        return TRIPA_DICTION[unique_ident]


### Yelp API caching setup
try:
    cache_yelp_file = open(CACHE_YELP, "r")
    cache_yelp_contents = cache_yelp_file.read()
    YELP_DICTION = json.loads(cache_yelp_contents)
    cache_yelp_file.close()
except:
    YELP_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

###### Get Data from TripAdvisor #################
def get_info_tripa(page=""):
    baseurl = "https://www.tripadvisor.com/RestaurantSearch-g29556-{}-Ann_Arbor_Michigan.html#EATERY_LIST_CONTENTS".format(page)
    page_text = make_request_using_cache_crawl(baseurl)
    page_soup = BeautifulSoup(page_text, "html.parser")

    results_list = page_soup.find_all(class_="listing")
    restaurants_list = [] 
    for i in results_list:
        try:
            rest_name = i.find(class_="property_title").text.replace("\n", "")
            rest_rating = i.find(class_="ui_bubble_rating")["alt"].replace(" of 5 bubbles", "")
            rest_price = i.find(class_="item price").string
            detail_url = "https://www.tripadvisor.com" + i.find("a")["href"]

            restaurant_ins = Restaurant(rest_name, rest_rating, rest_price, detail_url)

            ###scrape second level pages
            details_page_text = make_request_using_cache_crawl(detail_url)
            details_page_soup = BeautifulSoup(details_page_text, "html.parser")
            street_info = details_page_soup.find(class_ = "street-address").text
            zip_info = details_page_soup.find(class_ = "locality").text.split(", ")[1][3:8]
            rest_reviews = details_page_soup.find(property = "count").text.replace(",", "")

            restaurant_ins.street = street_info
            restaurant_ins.zip = zip_info
            restaurant_ins.reviews = rest_reviews
            restaurants_list.append(restaurant_ins)
        except:
            continue


    return restaurants_list


##################### Get Information from Yelp API ###########################
def get_info_yelp(name):
    base_url = "https://api.yelp.com/v3/businesses/search"
    headers = {'Authorization': "Bearer {}".format(API_KEY)}
    parameters = {}
    parameters["term"] = name
    parameters["location"] = "ann arbor"
    parameters["limit"] = 1
    unique_id = params_unique_combination(base_url, parameters)
    if unique_id in YELP_DICTION:
        return YELP_DICTION[unique_id]
    else:
        response = requests.get(base_url, params=parameters, headers=headers)
        YELP_DICTION[unique_id] = json.loads(response.text)
        write_file = open(CACHE_YELP, "w+")
        write_file.write(json.dumps(YELP_DICTION,indent=4))
        write_file.close()
        return YELP_DICTION[unique_id]

################# Get information from Yelp API based on the restaurants' names from TripAdvisor ####################
top100 = get_info_tripa()+get_info_tripa("oa60")+get_info_tripa("oa90")+get_info_tripa("oa120")
yelp_list = []
yelp_list.append(("Restaurant", "Category", "TripA_Rating", "TripA_ReviewCount", "Yelp_Rating", "Yelp_ReviewCount", "Phone", "Latitude", "longitude"))
for rest in top100:
    try:
        yelp_info = get_info_yelp(rest.name)["businesses"][0]
        yelp_list.append((rest.name, yelp_info["categories"][0]["title"], rest.rating1, rest.reviews, yelp_info["rating"], yelp_info["review_count"], yelp_info["phone"], yelp_info["coordinates"]["latitude"], yelp_info["coordinates"]["longitude"]))
    except:
        continue

with open("top100.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerows(yelp_list)

################ Construct Database ############################
DBNAME = "Final_Project.db"

def init_tables():
    # Create db
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the database.")

    # Drop tables if they exist
    statement = '''
        DROP TABLE IF EXISTS 'Restaurants';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Ratings';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'DetailInformation';
    '''
    cur.execute(statement)
    conn.commit()

################# Create tables: Bars ####################
    statement = '''
        CREATE TABLE 'Restaurants' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'RestaurantName' TEXT NOT NULL
        );
    '''
    try:
        cur.execute(statement)
    except:
        print("Fail to create table.")
    conn.commit()

    statement = '''
        CREATE TABLE 'DetailInformation' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'RestaurantId' INTEGER,
            'PriceRange' TEXT,
            'PageURL' TEXT,
            'Street' TEXT,
            'City' TEXT,
            'State' TEXT,
            'Zipcode' TEXT,
            'Phone' TEXT,
            'Latitude' INTEGER,
            'Longitude' INTEGER,
            'Categories' TEXT

        );
    '''
    try:
        cur.execute(statement)
    except:
        print("Fail to create table.")


    statement = '''
        CREATE TABLE 'Ratings' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'RestaurantId' INTEGER,
            'TripA_Rating' INTEGER,
            'TripA_ReviewCount' INTEGER,
            'Yelp_Rating' INTEGER,
            'Yelp_ReviewCount' INTEGER

        );
    '''
    try:
        cur.execute(statement)
    except:
        print("Fail to create table.")
    conn.commit()
    conn.close()

############ Insert Data into Restaurants Table ################
def insert_data_restaurants():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    for i in top100:
        statement = '''
            INSERT INTO "Restaurants"
            VALUES (?, ?)
        '''
        #values = (None, i.name, i.price, i.url, i.street, i.city, i.state, i.zip)
        values = (None, i.name)

        cur.execute(statement, values)
        conn.commit()
        #conn.close()

def insert_data_ratings(FILENAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    with open(FILENAME, "r") as f:
        csv_data = csv.reader(f)

        next(csv_data)

        for row in csv_data:
            insert_statement = '''
                INSERT INTO "Ratings"
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            try:
                statement = 'SELECT Id FROM Restaurants WHERE RestaurantName = "{}"'.format(row[0])
                #print(row[8])
                cur.execute(statement)
                res = cur.fetchall()
                #print(res2)
                res = res[0][0]
            except:
                res = "unknow"
            values = (None, res, row[2], row[3], row[4], row[5])

            cur.execute(insert_statement, values)
            conn.commit()

def insert_data_detail(FILENAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    with open(FILENAME, "r") as f:
        csv_data = csv.reader(f)

        next(csv_data)

        for row in csv_data:
            insert_statement = '''
                INSERT INTO "DetailInformation"
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            try:
                statement = 'SELECT Id FROM Restaurants WHERE RestaurantName = "{}"'.format(row[0])
                #print(row[8])
                cur.execute(statement)
                res = cur.fetchall()
                #print(res2)
                res = res[0][0]
            except:
                res = "unknow"
            values = (None, res, None, None, None, None, None, None, row[6], row[7], row[8], row[1])

            cur.execute(insert_statement, values)
            conn.commit()

def update_data_detail():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    n = 1
    for i in top100:
        #print(i.price)
        statement = 'UPDATE DetailInformation '
        statement += 'SET PriceRange = "{}", PageURL = "{}", Street = "{}", City = "{}", State = "{}", Zipcode = "{}"'.format(i.price,i.url,i.street,i.city,i.state,i.zip)
        statement += 'WHERE Id = {}'.format(n)
        #print(statement)
        n += 1
        cur.execute(statement)
        conn.commit()


###################### Presentation Data #########################
# res_list = []

def get_top50_form():
    # global res_list
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = 'SELECT d.Id, r.RestaurantName, d.Street, d.City, d.State, d.Zipcode, d.Phone, d.Categories, t.Yelp_Rating, t.Yelp_ReviewCount FROM DetailInformation d '
    statement += 'JOIN Restaurants r ON r.Id = d.RestaurantId '
    statement += 'JOIN Ratings t on r.Id = t.RestaurantId ORDER BY d.Id LIMIT 50'

    cur.execute(statement)
    results = cur.fetchall()
    # top_lt = []
    # name_lt = []
    # address_lt = []
    # phone_lt = []
    # category_lt = []
    # rating_lt = []
    # review_lt = []
    res_list = []
    for i in results:
        res_list.append([i[0],i[1],'{}, {}, {}{}'.format(i[2],i[3],i[4],i[5]),i[6],i[7],int(i[8]),int(i[9])])

    # for i in results:
    #     #top_list.append('{}, {}, {}, {} {}, Phone:{}, Category:{}'.format(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
    #     top_lt.append(i[0])
    #     name_lt.append(i[1])
    #     address_lt.append('{}, {}, {}{}'.format(i[2],i[3],i[4],i[5]))
    #     phone_lt.append(i[6])
    #     category_lt.append(i[7])


    # trace = go.Table(
    #     header=dict(values=['Top', 'Name', 'Address', 'Phone', 'Category']),
    #     cells=dict(values= [top_lt,name_lt,address_lt,phone_lt,category_lt]))

    # data = [trace] 
    # div = plot(data, filename = 'basic_table', output_type='div')

    conn.commit()
    conn.close()

    return res_list

def get_restaurants_sorted(sortby='ratings', sortorder='desc'):
    if sortby == 'ratings':
        sortcol = 5
    elif sortby == 'reviews':
        sortcol = 6
    elif sortby == 'top':
        sortcol = 0
    else:
        sortcol = 0

    rev = (sortorder == 'desc')
    results = get_top50_form()
    sorted_list = sorted(results, key=lambda row: row[sortcol], reverse=rev)
    print(results[0])
    print(sorted_list[0])
    return sorted_list


def get_top50_list():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = 'SELECT d.Id, r.RestaurantName, d.Street, d.City, d.State, d.Zipcode, d.Phone, d.Categories FROM DetailInformation d '
    statement += 'JOIN Restaurants r ON r.Id = d.RestaurantId ORDER BY d.Id LIMIT 50'

    cur.execute(statement)
    results = cur.fetchall()
    top_lt = []
    name_lt = []
    address_lt = []
    phone_lt = []
    category_lt = []
    for i in results:
        #top_list.append('{}, {}, {}, {} {}, Phone:{}, Category:{}'.format(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
        top_lt.append(i[0])
        name_lt.append(i[1])
        address_lt.append('{}, {}, {}{}'.format(i[2],i[3],i[4],i[5]))
        phone_lt.append(i[6])
        category_lt.append(i[7])

    trace = go.Table(
        header=dict(values=['Top', 'Name', 'Address', 'Phone', 'Category']),
        cells=dict(values= [top_lt,name_lt,address_lt,phone_lt,category_lt]))

    data = [trace] 
    div = plot(data, filename = 'basic_table', output_type='div')

    conn.commit()
    conn.close()

    return div


def plot_map_yelp():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = '''
        SELECT d.Latitude, d.Longitude, r.RestaurantName, d.Categories, d.Phone, a.Yelp_Rating From DetailInformation d 
        JOIN Restaurants r on d.RestaurantId = r.Id
        JOIN Ratings a on a.RestaurantId = r.Id
        ORDER BY a.Yelp_Rating DESC
        LIMIT 50
    '''
    cur.execute(statement)
    res = cur.fetchall()
    lat_vals = []
    lon_vals = []
    text_vals = []
    for i in res:
        lat_vals.append(i[0])
        lon_vals.append(i[1])
        text_vals.append('Name:{}, Category:{}, Phone:{}, Rating:{}'.format(i[2],i[3],i[4],i[5]))

    conn.commit()
    conn.close()

    # create data object
    data = [dict(
              type = 'scattermapbox',
              lon = lon_vals,
              lat = lat_vals,
              text = text_vals,
              mode = 'markers',
              marker = dict(
                   size = 15,
                   symbol = 'circle',
                   color = 'green',
                   opacity = 0.6
        ))]

    # # centering the map
    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    # #  padding 
    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    # # create the layout object
    layout = dict(
                title = 'Yelp Rating Top 50 Restaurants in Ann Arbor<br>(Hover for restaurant name and other information)',
                autosize = True,
                showlegend = False,
                mapbox = dict(
                    accesstoken = secrets.MAPBOX_TOKEN,
                    bearing = 0,
                    center = dict(
                        lat=center_lat,
                        lon=center_lon
                    ),
                    pitch = 0,
                    zoom = 12,
                ),
    )

    fig = dict(data=data, layout=layout)
    div = plot(fig, validate=False, filename='Ann Arbor - Yelp Rating top50 restaurants', output_type='div')
    return div

def plot_map_top50():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = '''
        SELECT d.Latitude, d.Longitude, r.RestaurantName, d.Categories, d.Phone, a.TripA_Rating From DetailInformation d 
        JOIN Restaurants r on d.RestaurantId = r.Id
        JOIN Ratings a on a.RestaurantId = r.Id
        ORDER BY a.TripA_Rating DESC
        LIMIT 50
    '''
    cur.execute(statement)
    res = cur.fetchall()
    lat_vals = []
    lon_vals = []
    text_vals = []
    for i in res:
        lat_vals.append(i[0])
        lon_vals.append(i[1])
        text_vals.append('Name:{}, Category:{}, Phone:{}, Rating:{}'.format(i[2],i[3],i[4],i[5]))

    conn.commit()

    conn.close()

    # create data object
    data = [dict(
              type = 'scattermapbox',
              lon = lon_vals,
              lat = lat_vals,
              text = text_vals,
              mode = 'markers',
              marker = dict(
                   size = 15,
                   symbol = 'circle',
                   color = 'green',
                   opacity = 0.6
        ))]

    # # scaling and centering the map
    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    # # fix padding problem
    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    # # create the layout object
    layout = dict(
                title = 'TripAdvisor Rating Top 50 Restaurants in Ann Arbor<br>(Hover for restaurant name and other information)',
                autosize = True,
                showlegend = False,
                mapbox = dict(
                    accesstoken = secrets.MAPBOX_TOKEN,
                    bearing = 0,
                    center = dict(
                        lat=center_lat,
                        lon=center_lon
                    ),
                    pitch = 0,
                    zoom = 12,
                ),
    )

    fig = dict(data=data, layout=layout)
    div = plot(fig, validate=False, filename='Ann Arbor - TripAdvisor Rating Top50 Restaurants', output_type='div')
    return div

def plot_category_pei():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = 'SELECT Categories, COUNT(*) FROM DetailInformation GROUP BY Categories'
    statement += ' ORDER BY COUNT(*) DESC LIMIT 50'
    cur.execute(statement)
    result = cur.fetchall()
    labels = []
    values = []
    for i in result:
        labels.append(i[0])
        values.append(i[1])

    conn.commit()
    conn.close()

    trace = go.Pie(labels=labels, values=values)

    div = plot([trace], filename='categories_pie_chart', output_type='div')
    return div


def plot_rating_line():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = 'SELECT TripA_Rating, COUNT(*) FROM Ratings'
    statement += ' GROUP BY TripA_Rating'
    statement += ' ORDER BY TripA_Rating DESC LIMIT 100'
    cur.execute(statement)
    resultT = cur.fetchall()
    #tname = []
    trating = []
    trating_count = []
    for i in resultT:
        #print(i)
        #tname.append(i[0])
        trating.append(i[0])
        trating_count.append(i[1])

    statement = 'SELECT Yelp_Rating, COUNT(*) FROM Ratings'
    statement += ' GROUP BY Yelp_Rating'
    statement += ' ORDER BY Yelp_Rating DESC LIMIT 100'
    cur.execute(statement)
    resulty = cur.fetchall()
    #yname = []
    yrating = []
    yrating_count = []
    for i in resulty:
        #print(i)
        #yname.append(i[0])
        yrating.append(i[0])
        yrating_count.append(i[1])

    conn.commit()
    conn.close()    

    trace0 = go.Scatter(
        x = trating,
        y = trating_count,
        mode = 'lines+markers',
        name = 'TripAdvisor Ratings Distribution'
        )

    trace1 = go.Scatter(
        x = yrating,
        y = yrating_count,
        mode = 'lines+markers',
        name = 'Yelp Ratings Distribution'
        )
    data = [trace0,trace1]
    div = plot(data, filename='rating line chart', output_type='div')

    return div

     

def plot_price_bar():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Fail to connect to the initial database.")

    statement = 'SELECT PriceRange, COUNT(*) FROM DetailInformation WHERE Id <51 GROUP BY PriceRange'
    cur.execute(statement)
    result = cur.fetchall()
    price = []
    p_count = []
    for i in result:
        #print(i)
        price.append(i[0])
        p_count.append(i[1])

    conn.commit()
    conn.close()

    data = [go.Bar(
        x = ['low($)','medium($$-$$$)','high($$$$)'],
        y = p_count
        )]

    div = plot(data, filename='price_bar_chart', output_type='div')
    return div

ListFile = "top100.csv"

init_tables()
insert_data_restaurants()
insert_data_ratings(ListFile)
insert_data_detail(ListFile)
update_data_detail()
