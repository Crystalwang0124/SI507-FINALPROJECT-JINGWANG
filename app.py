from flask import Flask, render_template, url_for
import requests
from secrets import *
import json
from module import *
#from plotly.offline import plot
from flask import Flask, render_template, request

app = Flask(__name__)

# init_tables()
# insert_data_restaurants()
# insert_data_ratings(ListFile)
# insert_data_detail(ListFile)
# update_data_detail()
#plot_map_top50()
#plot_map_tripa()
#plot_category_pei()
#plot_rating_line()
#plot_price_bar()
#get_top100_list()

@app.route('/')
def home_page():
    html = '''
        <link rel="stylesheet" href="/static/style.css">
        <h1 align='center'>Welcome to my site!</h1>
        <h3 align='center'><a href='/form'>Ann Arbor Top50 Restaurants</a></h3>
        <h3 align='center'><a href='/map50'>Map for Ann Arbor Top50 Restaurants</a></h3>
        <h3 align='center'><a href='/category'>Top50 Restaurants Categories Pie Chart</a></h3>        
        <h3 align='center'><a href='/rating_compare'>Ratings Distribution Comparison</a></h3>
        <h3 align='center'><a href='/price'>Price Range Status</a></h3>
        <h3 align='center'><a href='/AAtop50'>Ann Arbor Top50 Restaurants Table</a></h3>
        
        <h1 align='center'>Have a nice day!</h1>
    '''
    return html

@app.route('/form', methods=['GET', 'POST'])
def Restaurants_top():
    if request.method == 'POST':
        if'sortby' in request.form:
            sortby = request.form['sortby']
        else:
            sortby="top"
        if "sortorder" in request.form:
            sortorder = request.form['sortorder']
        else:
            sortorder="desc"
        seasons = get_restaurants_sorted(sortby, sortorder)
    else:
        seasons = get_restaurants_sorted()
        
    return render_template("seasons.html", seasons=seasons)

@app.route('/AAtop50')
def AA_top50_list():
    html = '<div id="plot_top50">'
    html = "<h2 align='center'>The List of Top50 Restaurants in Ann Arbor</h2>"
    html += get_top50_list()
    html += '</div>'
    return html

@app.route('/map50')
def map50():
    html = '<div id="plot_map50">'
    html += plot_map_top50()
    html += '</div>'
    return html

@app.route('/category')
def category():
    html = '<div id="plot_category">'
    html += "<h2 align='center'>Pie Chart for Top50 Restaurants Categories Distribution</h2>"
    html += plot_category_pei()
    html += '</div>'
    return html

@app.route('/rating_compare')
def rating_compare():
    html = '<div id="plot_rating_line">'
    html += "<h2 align='center'>Line Chart for Ratings Comparison between TripAdvisor and Yelp</h2>"
    html += plot_rating_line()
    html += '</div>'    
    return html

@app.route('/price')
def price():
    html = '<div id="plot_price">'
    html += "<h2 align='center'>Bar Chart for Price Range Status for Top50 Restaurants</h2>"
    html += plot_price_bar()
    html += '</div>'
    return html

if __name__ == '__main__':
    app.run(debug=True)