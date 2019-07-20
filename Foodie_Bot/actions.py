from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_core.events import Restarted
from collections import OrderedDict
import zomatopy
import json
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

result = ""

class ActionValidateLocation(Action):
    def name(self):
        return 'action_validate_location'
        
    def run(self, dispatcher, tracker, domain):
        cities = ["Bangalore","Chennai","Delhi","Hyderabad","Kolkata","Mumbai","Agra","Ajmer","Aligarh","Amravati","Amritsar","Asansol","Aurangabad","Ahmedabad","Bareilly","Belgaum","Bhavnagar","Bhiwandi","Bhopal","Bhubaneswar","Bikaner","Bokaro Steel City","Chandigarh","Coimbatore","Nagpur","Cuttack","Dehradun","Dhanbad","Durg-Bhilai Nagar","Durgapur","Erode","Faridabad","Firozabad","Ghaziabad","Gorakhpur","Gulbarga","Guntur","Gwalior","Gurgaon","Guwahati","Hubli-Dharwad","Indore","Jabalpur","Jaipur","Jalandhar","Jammu","Jamnagar","Jamshedpur","Jhansi","Jodhpur","Kakinada","Kannur","Kanpur","Kochi","Kottayam","Kolhapur","Kollam","Kota","Kozhikode","Kurnool","Lucknow","Ludhiana","Madurai","Malappuram","Mathura","Goa","Mangalore","Meerut","Moradabad","Mysore","Nanded","Nashik","Nellore","Noida","Palakkad","Patna","Pondicherry","Prayagraj","Pune","Raipur","Rajkot","Rajahmundry","Ranchi","Rourkela","Salem","Sangli","Siliguri","Solapur","Srinagar","Sultanpur","Surat","Thiruvananthapuram","Thrissur","Tiruchirappalli","Tirunelveli","Tiruppur","Tiruvannamalai","Ujjain","Bijapur","Vadodara","Varanasi","Vasai-Virar City","Vijayawada","Visakhapatnam","Vellore","Warangal"]
        cities_list = [x.lower() for x in cities]
        loc = tracker.get_slot('location')
        if loc is not None:
            if loc in cities_list:
                return[SlotSet('location', loc)]
            else:
                dispatcher.utter_message("Foodie Bot doesn't operate in the provided location!")
                return[SlotSet('location', None)]
        else:
            dispatcher.utter_message("Please enter a valid location.")
            return[SlotSet('location', None)]

class ActionValidateCuisine(Action):
    def name(self):
        return 'action_validate_cuisine'
    
    def run(self, dispatcher, tracker, domain):
        cuisine_list = ["chinese", "mexican", "italian", "american", "south indian", "north indian"]
        cuisine = tracker.get_slot('cuisine')
        if cuisine is not None:
            if cuisine.lower() in cuisine_list:
                return[SlotSet('cuisine',cuisine)]
            else:
                dispatcher.utter_message("Sorry, Foodie Bot doesn't provide services for the provided cuisine.")
                return[SlotSet('cuisine', None)]
        else:
            dispatcher.utter_message("Please enter a valid Cuisine.")
            return[SlotSet('cuisine', None)]
            
class ActionValidateBudget(Action):
    def name(self):
        return 'action_validate_budget'
        
    def run(self, dispatcher, tracker, domain):
        cost = tracker.get_slot('budget')
        if cost == 'less than 300' or cost == 'lesser than 300' or cost == '< 300' or cost == '<300' or ("cheap" in cost):
            return[SlotSet('budget', 'low')]
        elif cost == 'more than 700' or cost == 'greater than 700' or cost == '< 700' or cost == '<700' or ("expensive" in cost) or ("costly" in cost):
            return[SlotSet('budget', 'high')]
        else:
            return[SlotSet('budget', 'mid')]

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"5c563a0005023c9de39b0719f1e15f13"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		loc = loc.lower()
		cuisine = tracker.get_slot('cuisine')
		cuisine = cuisine.lower()
		budget = tracker.get_slot('budget')
		if budget == 'low':
		    cost_min = 0
		    cost_max = 300
		elif budget == 'mid':
		    cost_min = 301
		    cost_max = 700
		elif budget == 'high':
		    cost_min = 701
		    cost_max = 9999
		cols = ['restaurant name', 'restaurant address', 'avgbudget for two', 'rating']
		res_df = pd.DataFrame(columns = cols)
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		cuisines_dict={
		'american':1,
		'mexican':73,
		'bakery':5,
		'chinese':25,
		'cafe':30,
		'italian':55,
		'biryani':7,
		'north indian':50,
		'south indian':85
		}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 20)
		response=""
		d = json.loads(results)
		if d['results_found'] != 0:
		    for restaurant in d['restaurants']:
		        res = {"rating":restaurant['restaurant']["user_rating"]["aggregate_rating"], "restaurant name":restaurant['restaurant']['name'], "restaurant address": restaurant['restaurant']['location']['address'], "avgbudget for two": restaurant['restaurant']['average_cost_for_two']}
		        if (res['avgbudget for two'] >= cost_min) and (res['avgbudget for two'] <= cost_max):
		            res_df.loc[len(res_df)] = res
		
		res_df = res_df.sort_values(['rating', 'avgbudget for two'], ascending=[False,True])
		res_df_top10 = res_df.head(10)
		res_df = res_df.head(5)
		res_df = res_df.reset_index(drop=True)
		res_df.index = res_df.index.map(str)		                
		
		if len(res_df) != 0:
		    for index, row in res_df.iterrows():
		        response = response+ index + ". Found \""+ row['restaurant name']+ "\" in "+ row['restaurant address']+" has been rated "+ row['rating']+"\n"
		else:
		    response = 'Found 0 restaurants in given price range'
		    
		dispatcher.utter_message(response)
		return [SlotSet('budget',budget)]


class ActionValidateEmail(Action):
	def name(self):
		return 'action_validate_email'
		
	def run(self, dispatcher, tracker, domain):
	    import re
	    user_email = tracker.get_slot('email')
	    if user_email is not None:
	        if re.search("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",user_email):
	            return[SlotSet('email',user_email)]
	        else:
	            dispatcher.utter_message("Please enter a valid email address.")
	            return[SlotSet('email',None)]
	    else:
	        dispatcher.utter_message("Please enter an email address.")
	        return[SlotSet('email', None)]

class ActionSendEmail(Action):
    def name(self):
        return 'action_email'
    
    def run(self, dispatcher, tracker, domain):
        config={ "user_key":"5c563a0005023c9de39b0719f1e15f13"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        loc = loc.lower()
        cuisine = tracker.get_slot('cuisine')
        cuisine = cuisine.lower()
        budget = tracker.get_slot('budget')
        if budget == 'low':
            cost_min = 0
            cost_max = 300
        elif budget == 'mid':
            cost_min = 301
            cost_max = 700
        elif budget == 'high':
            cost_min = 701
            cost_max = 9999
        cols = ['restaurant name', 'restaurant address', 'avgbudget for two', 'rating']
        res_df = pd.DataFrame(columns = cols)
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={
        'american':1,
        'mexican':73,
        'bakery':5,
        'chinese':25,
        'cafe':30,
        'italian':55,
        'biryani':7,
        'north indian':50,
        'south indian':85
        }
        results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 20)
        response=""
        d = json.loads(results)
        if d['results_found'] != 0:
            for restaurant in d['restaurants']:
                res = {"rating":restaurant['restaurant']["user_rating"]["aggregate_rating"], "restaurant name":restaurant['restaurant']['name'], "restaurant address": restaurant['restaurant']['location']['address'], "avgbudget for two": restaurant['restaurant']['average_cost_for_two']}
                if (res['avgbudget for two'] >= cost_min) and (res['avgbudget for two'] <= cost_max):
                    res_df.loc[len(res_df)] = res
                    
        res_df = res_df.sort_values(['rating', 'avgbudget for two'], ascending=[False,True])
        
        email = tracker.get_slot('email')
        gmail_user = 'foodie.sssm@gmail.com'
        gmail_password = 'Rasa@2019'
        sent_from = gmail_user
        to = str(email)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Restaurant Details"
        msg['From'] = gmail_user
        msg['To'] = to
        if len(res_df) == 0:
            html = """
            <html>
            <head>
            <style>
            table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }
            
            td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            
            tr:nth-child(even) {
                background-color: #dddddd;
            }
            
            </style>
            </head>
            <body>
            <p>Hi!</p>
            <p>Thanks for using Foodie, the restaurant chatbot.</p>
            <p>Sorry, we could not find restaurant that meet your criteria.</p>
			"""
		else:
		    res_df_top10 = res_df.head(10)
		    res_df_top10 = res_df_top10.reset_index(drop=True)
		    res_df_top10.index = res_df_top10.index.map(str)
		    html = """
		    <html>
		    <head>
		    <style>
		    table {
		        font-family: arial, sans-serif;
		        border-collapse: collapse;
		        width: 100%;
		    }
		    
		    td, th {
		        border: 1px solid #dddddd;
		        text-align: left;
		        padding: 8px;
		    }
		    
		    tr:nth-child(even) {
		        background-color: #dddddd;
		    }
		    </style>
		    </head>
		    <body>
		    <p>Hi!</p>
		    <p>Thanks for using Foodie, the restaurant chatbot. Please find the requested list of restaurants below.</p>
		    <p>Enjoy the food!</p>
		    """
		    html = html+res_df_top10.to_html()
		html = html+"<p> based on your query...</p>"+cuisine+" restaurants "+budget+" budget at "+loc+"</body></html>"
		part2 = MIMEText(html, 'html')
		msg.attach(part2)
		server = smtplib.SMTP_SSL('smtp.gmail.com',465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, msg.as_string())
		server.close()
		dispatcher.utter_message("Email Sent")
		return [SlotSet('email',email)]
        
class ActionRestarted(Action):
    def name(self):
        return 'action_restarted'
        
    def run(self, dispatcher, tracker, domain):
        return[Restarted()]
