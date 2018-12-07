import unittest
import json
import csv
import sqlite3
from module import *

class TestDatabase(unittest.TestCase):
	def test_restaurants_table(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statment = '''
			SELECT RestaurantName
			FROM Restaurants
			ORDER BY Id
		'''

		result1 = cur.execute(statment)
		result1_list = result1.fetchall()
		self.assertEqual(len(result1_list), 106)
		self.assertTrue(("The Lunch Room",) in result1_list)


		conn.close()

	def test_ratings_table(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statment1 = '''
	        SELECT RestaurantId
			FROM Ratings
		'''

		result1 = cur.execute(statment1)
		result1_list = result1.fetchall()
		self.assertEqual(len(result1_list), 105)

		statment2 = '''
		    SELECT TripA_Rating, Yelp_ReviewCount
			FROM Ratings
			WHERE TripA_Rating == Yelp_Rating
		'''

		result2 = cur.execute(statment2)
		result2_list = result2.fetchall()
		self.assertEqual(len(result2_list), 24)
		for item in result2_list:
			self.assertNotEqual(type(item[0]), str)
			self.assertEqual(type(item[1]), int)

		conn.close()

	def test_joins(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statment = '''
            SELECT RestaurantName FROM Restaurants JOIN Ratings ON Restaurants.Id = Ratings.RestaurantId WHERE TripA_Rating>4 AND Yelp_Rating > 4
		'''

		results = cur.execute(statment)
		result_list = results.fetchall()
		self.assertEqual(len(result_list), 11)
		self.assertIn(('NeoPapalis',), result_list)

		conn.close()



class TestGetData(unittest.TestCase):
    def setUp(self):
        self.tripa = open("cache_tripa.json", "r", encoding='utf-8')
        self.yelp = open("cache_yelp.json", "r", encoding='utf-8')
        self.top100 = open("top100.csv", "r")

    def test_tripa_json_exist(self):
        self.assertTrue(self.tripa.read())

    def test_yelp_json_exist(self):
        self.assertTrue(self.yelp.read())

    def test_top30_csv_exist(self):
        self.assertTrue(self.top100.read())

    def tearDown(self):
        self.tripa.close()
        self.yelp.close()
        self.top100.close()


class TestClass(unittest.TestCase):
    def test_restaurant_class(self):
        sample = Restaurant("The Lunch Room", 4.5, "$", "https://www.tripadvisor.com/Restaurant_Review-g29556-d4982890-Reviews-The_Lunch_Room-Ann_Arbor_Michigan.html")
        self.assertEqual(sample.street, "123 South St.")
        self.assertEqual(sample.rating2, "0")
        self.assertEqual(sample.__str__(), "The Lunch Room: 123 South St., Ann Arbor, MI(48111)")



class TestWebCrawling(unittest.TestCase):
    def test_get_rest_info(self):
        result_ls = get_info_tripa("")
        self.assertEqual(len(result_ls), 29)
        self.assertEqual(type(result_ls[0]), Restaurant)



class TestPlot(unittest.TestCase):
    def test_plot_top50_map(self):
        try:
            plot_map_top50()
        except:
            self.fail()

    def test_plot_category_pei(self):
        try:
            plot_category_pei()
        except:
            self.fail()

    def test_plot_rating_line(self):
        try:
            plot_rating_line()
        except:
            self.fail()

    def test_plot_price_bar(self):
        try:
            plot_price_bar()
        except:
            self.fail()

    def test_plot_top50_table(self):
        try:
            get_top50_list()
        except:
            self.fail()



if __name__ == "__main__":
	unittest.main(verbosity=2)
