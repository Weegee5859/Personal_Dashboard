from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
from difflib import SequenceMatcher
import os
import numpy as np
import pandas as pd
import pickle
from random import random, choice, randrange
import re, requests
import shutil, sys
import tabula, threading
from PIL import Image
from time import sleep

def hi():
	return "hi"

def getWeatherData():
	#return "weather update"
	# Enter your API key here
	try:
		weatherKeyFile = open('myData/weatherKey', 'rb')
	except FileNotFoundError:
		return 'Error: Weather Key File Not Found!'

	try:  
		api_key = pickle.load(weatherKeyFile)
	except FileNotFoundError:
		weatherKeyFile.close()
		return 'Error: Weather Key File Not Found!'
	weatherKeyFile.close()
	
	# base_url variable to store url 
	base_url = "http://api.openweathermap.org/data/2.5/weather?"
	# Give city name 
	city_name = "Florida"
	# complete url address 
	complete_url = base_url + "appid=" + api_key + "&q=" + city_name + '&units=imperial'  
	# return response object and convert json format to python format
	response = requests.get(complete_url).json()  
	# if error
	if response["cod"] == "404":
		return False
	# weather data dict
	weather_data = {}
	# now
	weather_data['temp'] = round(response['main']['temp'])
	# high
	weather_data['high'] = round(response['main']['temp_max'])
	# low
	weather_data['low'] = round(response['main']['temp_min'])
	# pressure
	weather_data['pressure'] = response['main']["pressure"] 
	# humidty 
	weather_data['humidity'] = response['main']["humidity"] 
	# icon
	weather_data['icon'] = response['weather'][0]['icon']
	# forecast
	weather_data['forecast'] = response['weather'][0]["description"].title()
	# simple_forecast
	weather_data['simple_forecast'] = response['weather'][0]['main']
	return weather_data
	

def getWeatherWeekData():
	
	def day_suffix(day):
		if (3 < day < 21) or (23 < day < 31):
			day = str(day) + 'th'
		else:
			suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
			day = str(day) + suffixes[day % 10]
		return day

	try:
		# Enter your API key here 
		weatherKeyFile = open('myData/weatherKey', 'rb')
		try:  
			api_key = pickle.load(weatherKeyFile)
		except FileNotFoundError:
			weatherKeyFile.close()
			return 'Error: Weather Key File Not Found!'
		weatherKeyFile.close()
		full_url = "https://api.openweathermap.org/data/2.5/onecall?lat=27.66&lon=-81.51&units=imperial&exclude=hourly,minutely,current&appid=" + api_key
		# return response object and convert json format to python format
		response = requests.get(full_url).json() 
		weather_week_data = []
		weather_day_data = {}
		# iterate through data data
		for index, y in enumerate(response['daily']):
			#current iterated weathers date
			weather_date = datetime.now()+timedelta(days=index+1)
			weather_day_data['day'] =  str( weather_date.strftime("%A") )
			weather_day_data['date'] =  str( weather_date.strftime("%B ") + day_suffix(weather_date.day) )
			weather_day_data['high'] = round(y['temp']['max'])
			weather_day_data['low'] = round(y['temp']['min'])
			weather_icon = y['weather'][0]['icon']
			weather_day_data['forecast'] = y['weather'][0]['main']
			# append weather day data to weather week data
			weather_week_data.append(weather_day_data.copy())
	except Exception as e:
		print("WEATHER_WEEK_DATA: " + e)
	return weather_week_data


def getWordData():
	word_of_day = {}
	date = datetime.now()
	URL = 'https://www.wordgenius.com/'
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	# Word Title
	title = soup.find("h1", {'class': 'WordHeader__title'})
	word_of_day['title'] = title.text
	# Word Pronunciation
	result = soup.find('p', {'class': 'WordHeader__paragraph WordHeader__paragraph--pronunciation'})
	word_of_day['pronunciation'] = result.text
	# Word Type (adjective,verb, etc.)
	result = soup.find('div', {'class': 'WordHeader__row WordHeader__row--part'})
	word_of_day['type'] = par = result.findChild("p").text
	# Word Definition
	result = soup.find('div', {'class': 'WordHeader__row WordHeader__row--definition'})
	definition_para = result.findAll('p', {'class': 'WordHeader__paragraph'})
	# There can be multiple definitions, make definitions a list
	word_of_day['definitions'] = []
	# Iterate through definitions list and add valid items
	for index, item in enumerate(definition_para):
		word_of_day['definitions'].append("{0}. {1}".format(index+1,item.text))
	# Word Example Sentences
	example_para = soup.findAll('p', {'class': 'WordHeader__example'})
	# There can be multiple examples, make definitions a list
	word_of_day['examples'] = []
	# Iterate through examples list and add valid items
	for index, item in enumerate(example_para):
		word_of_day['examples'].append("{0}. {1}".format(index+1,item.text))
	return word_of_day

def getPrayerData():	
	prayer_of_day = {}
	URL = 'https://www.verseoftheday.com/'
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	# Prayer Data
	result = soup.find('div', {'class': 'bilingual-left'})
	# Prayer
	prayer_of_day['prayer'] = soup.find('div', {"class": 'bilingual-left'}).text
	# Verse
	prayer_of_day['verse'] = soup.find('div', {"class": 'reference'}).text
	return prayer_of_day


def getPlantingData():
	# File directory for plant_data file (if exist)
	file_dir = 'static/resources/planting/plant_data.npy'
	# Image file directory
	img_file_dir = 'static/resources/planting/images/'
	# If plant_data file doesn't exist, create it
	if not os.path.exists(file_dir):
		# Define site with plant info pdf file
		site = "https://www.burpee.com/on/demandware.static/-/Sites-BURPEE-Library/default/dw1a482b33/Images/Content/PDF/Zones9-10.pdf"
		# Load the tables from the site pdf file
		tables = tabula.read_pdf(site, pages="all", multiple_tables = True)
		# Holds every plants data
		plant_data = []
		# Dict to contain the plant info for each iteration
		plant = {}
		for sheet in tables:
			for index,row in sheet.iterrows():
				# Skip the first three rows (0-2), has invalid data
				if index < 2: continue
				try:
					# Skip if classification is None or sow type is 'NOT RECOMMENDED'
					if pd.isna( row['Unnamed: 0'] ) or row['Unnamed: 2'] == 'NOT RECOMMENDED': continue
					# Add plant information
					plant['classification'] = row['Unnamed: 0'] #Classification
					plant['name'] = row['Unnamed: 1'] #Planet Name
					plant['sow'] = row['Unnamed: 2'] # Sow Type
					plant['spring_indoor_sow'] = row['Spring Indoor Sow Date']
					plant['summer_transplant'] = row['Summer Transplant']
					plant['spring_summer_transplant'] = row['Spring/Summer Direct']
					plant['fall_indoor_sow'] = row['Fall Indoor Sow Date']
					plant['fall_transplant'] = row['Fall Transplant Date']
					plant['fall_direct_sow'] = row['Fall Direct Sow Date']
					plant['succession'] = row['Succession']
					plant['image'] = img_file_dir+plant['name'].lower()+".jpg"
					# Make all plant data strings
					for index in plant:
						plant[index] = str( plant[index] )
					# Append current plants data to plant_data
					plant_data.append(plant.copy())
				except Exception as e:
					print(e)
		# Get images for plants
		getPlantingImages(img_file_dir)
		#save file
		np.save(file=file_dir, arr=plant_data,allow_pickle=True)
	#load file as data
	data = np.load(file=file_dir,allow_pickle=True)

	return data[randrange(0,len(data))]

# Use only within getPlantingData to get download the images
def getPlantingImages(img_file_dir):
	if not os.path.exists(img_file_dir): return None
	file_dir = img_file_dir
	categories = ['vegetables','annual-flowers','perennials','herbs','fruit']
	#base_url = 'https://www.burpee.com/gardenadvicecenter/areas-of-interest/'
	base_url = 'https://www.burpee.com/gardenadvicecenter/encyclopedia/'
	# Iterate through categories
	for category in categories:
		page = requests.get(base_url+category+"/")
		soup = BeautifulSoup(page.content, 'html.parser')
		# Find all required images on the page
		image_list = soup.findAll('img', {'class': 'b-encyclopedia_asset_tile-image'})
		for image in image_list:
			# Images with CATID in filename is invalid, continue
			if 'CATID' not in image['src']: continue
			# Path variable goes unused, filename is the images' filename
			path,filename=os.path.split(image['src'])
			# [11:] removes "CATID-12345" from each filename
			filename = filename[11:].lower()
			# If exist continue
			if os.path.exists( file_dir+filename ): continue
			# Load saved image via request
			saved_image = Image.open(requests.get('https://www.burpee.com'+image['src'], stream = True).raw)
			# Save image to valid directory
			saved_image.save( file_dir+filename )

def getRecipeData():
	recipe = {}
	img_dir = 'static/resources/recipes/images/'
	recipe_urls_dir = 'static/resources/recipes/allrecipes_urls.npy'
	filename = 'recipe_image.jpg'
	# Get Recipe type urls and save
	# 'allrecipe_category_url_list' contains all the available food categories for allrecipes.com
	# Each category will have a sub category or even a sub-sub-category...
	# Examples...
	"""  
		'https://www.allrecipes.com/recipes/455/everyday-cooking/more-meal-ideas/30-minute-meals/'
		'https://www.allrecipes.com/recipes/456/everyday-cooking/more-meal-ideas/45-minute-meals/'
		'https://www.allrecipes.com/recipes/15103/salad/vegetable-salads/broccoli-salad/'
		'https://www.allrecipes.com/recipes/649/meat-and-poultry/chicken/chicken-salad/'
 	"""
	allrecipe_category_url_list = []
	# if allrecipe_category_url_list doesn't exist it will create a new list
	# this may be broken as the website may have updated by now
	if not os.path.exists(recipe_urls_dir):
		print("NEW RECIPE URLS")
		URL = 'https://www.allrecipes.com/'
		soup = BeautifulSoup( requests.get(URL).content, 'html.parser' )
		for recipe_type in soup.findAll('a', {'class': 'carouselNav__link recipeCarousel__link'}):
			soup = BeautifulSoup( requests.get(recipe_type['href']).content, 'html.parser' )
			recipe_sub_types = soup.findAll('a', {'class': 'carouselNav__link recipeCarousel__link'})
			for recipe_sub_type in recipe_sub_types:
				allrecipe_category_url_list.append(recipe_sub_type['href'])
		np.save(file=recipe_urls_dir, arr=allrecipe_category_url_list, allow_pickle=True)
	# Load allrecipe_category_url_list type urls
	allrecipe_category_url_list = np.load(file=recipe_urls_dir, allow_pickle=True)
	print(allrecipe_category_url_list)
	# Pick a random recipe category and scrape it
	# From their, iterate through all recipes from within that category
	# and select a random recipe. Finally, locate this random recipes href. 
	soup = BeautifulSoup(requests.get(choice(allrecipe_category_url_list)).content, 'html.parser')
	recipe_card_list = soup.findAll('a', {'class': 'comp mntl-card-list-items mntl-document-card mntl-card card card--no-image'}, href=True)
	#print(recipe_card_list)
	random_recipe_card = choice(recipe_card_list)

	random_recipe = BeautifulSoup(requests.get(random_recipe_card['href']).content, 'html.parser')
	print(random_recipe)
	print(random_recipe_card['href'])

	#print(random_recipe)

	print(random_recipe)
	print("===========================================")
	print(random_recipe_card['href'])

	# Add Recipe Info to dictionary
	recipe['name'] = random_recipe.find('h1', {'id': 'article-heading_1-0'}).text
	recipe['review'] = random_recipe.find('div', {'id': 'mntl-recipe-review-bar__rating_1-0'})
	if not recipe['review'] == None:
		#recipe['review'] = recipe['review'].text
		recipe['review'] = float( re.sub("[^0-9^.]", "", recipe['review'].text) )
		#round to nearest .5 decimal
		recipe['review'] = round( recipe['review'] * 2 ) / 2;
	#recipe['summary'] = random_recipe.find('div', {'class': 'card__summary'}).text
	#recipe['author'] = random_recipe.find('div', {'class': 'card__author'}).text
	try:
		recipe['link'] = random_recipe_card['href']
		#recipe['link'] = random_recipe.find('a', {'class': 'card__titleLink manual-link-behavior'})['href']
	except TypeError:
		recipe['link'] = "None"
		#return False
	# Define recipe Image
	recipe['image'] = None
	# Load saved image via request
	print("------------")
	#print(random_recipe.find('img')['src'])
	
	print(random_recipe_card.find('img')['data-src'])
	print("------------")

	saved_image = Image.open( requests.get(random_recipe_card.find('img')['data-src'], stream = True).raw )
	# Save image to valid directory
	saved_image.save( img_dir+filename )
	# if file was created successfully, recipe['image'] will equal image directory
	if os.path.exists(img_dir+filename):
		recipe['image'] = img_dir+filename
	#Format Returned Recipe data within dict
	for index in recipe:
		#review is a number, skip to avoid turning into string
		if index == 'review': continue
		recipe[index] = " ".join( str(recipe[index]).split() )
	return recipe

def getWeatherIcon(forecast,day_or_night):
	#SET WEATHER ICON
	if any(x in forecast.lower() for x in ['partly cloudy','mostly cloudy','fair']):
		icon = '02'		
	elif any(x in forecast.lower() for x in ['mostly sunny','sunny','clear']):
		icon = '01'	
	elif any(x in forecast.lower() for x in ['thunderstorm','storm']):
		icon = '11'
	elif any(x in forecast.lower() for x in ['shower','rain']):
		icon = '10'
	elif any(x in forecast.lower() for x in ['partly','cloudy']):
		icon = '50'
	else:
		icon = 'unknown'
	return icon+day_or_night

def getWeatherWeek2(days_to_iterate=6):
	# Define scope variables
	weather_week_data={}
	weather_week_data['data'] = []
	days_to_iterate = days_to_iterate
	count = 0
	def contains_digit(string):
		for char in string:
			if char.isdigit():
				return True
		return False
	def day_suffix(day):
		if (3 < day < 21) or (23 < day < 31):
			day = str(day) + 'th'
		else:
			suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
			day = str(day) + suffixes[day % 10]
		return day
	# Request Page
	page = requests.get("https://weather.com/weather/tenday/l/79f6fb29af620c9526982fdb41749e4287887eae35ac3bb491192ccd22bfd0c2")
	soup=BeautifulSoup(page.content,"html.parser")
	#forecast_container=soup.find("div",{"class":"DailyForecast--DisclosureList--350ZO"})
	forecast=soup.find_all("details",{"data-track-string":"detailsExpand"})
	# iterate through days
	for day in forecast:
		if count>=days_to_iterate: break
		day_data = {}
		# the listed day can return as 'tonight' or 'today' instead of a date (e.g. 'thur 15')
		listed_day = "N/A"
		try:
			listed_day = day.find("h2",{"data-testid":"daypartName"}).text
		except:
			print("no today")
		print(listed_day)
		# day or night suffic to load correct icon filename, d is daytime icon and n is nightime icon
		# default is day or 'd'
		day_or_night_suffix = 'd'
		# if listed_day contains a digit then its a valid date add to count
		# Otherwise it contains the str 'tonight'/'today', do not add to count
		if not contains_digit(listed_day) and listed_day.lower() != 'tonight':
			continue
		if contains_digit(listed_day):
			count=count+1
			day_data['day'] =  str( ( datetime.now()+timedelta(days=count) ).strftime("%A") )
		if listed_day.lower() == 'tonight':
			day_data['day'] =  listed_day.capitalize()
			day_or_night_suffix = 'n'
		# weather date must be formatted
		weather_date = datetime.now()+timedelta(days=count)
		day_data['date'] =  str( weather_date.strftime("%B ") + day_suffix(weather_date.day) )	
		# Define additional day data
		temperatures = day.findAll("span",{"data-testid":"TemperatureValue"})
		day_data['high'] = temperatures[0]
		day_data['low'] = temperatures[1]
		day_data['rain'] = day.find("span",{"data-testid":"PercentageValue"})
		day_data['forecast'] = day.find("div",{"data-testid":"wxIcon"}).find("span")
		# Turn data into text content / if .text was set when defined, program will crash if tag isnt found
		for value in day_data:
			# if day_data is invalid or is already a string continue
			if day_data[value] == None or isinstance(day_data[value], str): continue
			#Convert into text
			day_data[value] = day_data[value].text
			# forecast does not need formatting, if not forecast then format
			if not value == 'forecast':
				day_data[value] = ''.join(e for e in day_data[value] if e.isalnum())
			# if data ends up empty, make it hold "--"
			if day_data[value] == "": day_data[value] = "--"
		day_data['icon'] = getWeatherIcon(forecast=day_data['forecast'],day_or_night=day_or_night_suffix)
		#append to week
		weather_week_data['data'].append(day_data)
	return weather_week_data

def getWeather2():
	# suffix used for weather icon
	# if current time is between start and end time return 'd' for day otherwise return 'n' for night
	def getDayNightSuffix():
		start = time(7,0,0)
		end = time(19,0,0)
		now = datetime.now().time()
		if start <= now < end:
			return 'd'
		return 'n'
	# Get page request
	page = requests.get("https://weather.com/weather/today/l/79f6fb29af620c9526982fdb41749e4287887eae35ac3bb491192ccd22bfd0c2")
	soup=BeautifulSoup(page.content,"html.parser")
	# day data to return
	day_data = {}
	# gather day wweather data
	day_data['temp'] = soup.find("span",{"class":"CurrentConditions--tempValue--3KcTQ"})
	day_data['forecast'] = soup.find("div",{"class":"CurrentConditions--phraseValue--2xXSr"})
	high_and_low = soup.find("div",{"class":"CurrentConditions--tempHiLoValue--A4RQE"}).findAll("span")
	day_data['high'] = high_and_low[0]
	day_data['low'] = high_and_low[1]
	day_data['rain'] = soup.findAll("ul",{"class":"WeatherTable--columns--3q5Nx"})[2].find("span",{"class":"Column--precip--2H5Iw"})
	day_data['humidity'] = soup.find("span",{"data-testid":"PercentageValue"})
	# Turn data into text content / if .text was set above when defined, program will crash if tag isnt found
	for value in day_data:
		if day_data[value] == None: continue
		#Convert into text
		day_data[value] = day_data[value].text
		# remove all symbols and letters
		if not value == 'forecast':
			day_data[value] = ''.join(e for e in day_data[value] if e.isalnum())
		# remove all strings from rain data
		if value == 'rain':
			day_data[value] = ''.join(filter(str.isdigit, day_data[value]))
		# if data ends up empty, make it hold "--"
		if day_data[value] == "": day_data[value] = "--"
	#set Icon
	day_data['icon'] = getWeatherIcon(day_data['forecast'],getDayNightSuffix())
	return day_data

def getWeather3():
	# suffix used for weather icon
	# if current time is between start and end time return 'd' for day otherwise return 'n' for night
	def getDayNightSuffix():
		start = time(7,0,0)
		end = time(19,0,0)
		now = datetime.now().time()
		if start <= now < end:
			return 'd'
		return 'n'
	# Get page request
	page = requests.get("https://weather.com/weather/today/l/79f6fb29af620c9526982fdb41749e4287887eae35ac3bb491192ccd22bfd0c2")
	soup=BeautifulSoup(page.content,"html.parser")
	# day data to return
	day_data = {}
	#List of all Temperatures (current,high,low)
	temperatures = soup.findAll("span",{"data-testid":"TemperatureValue"})
	# gather day wweather data
	day_data['temp'] = temperatures[0]
	day_data['forecast'] = soup.findAll("div",{"data-testid":"wxPhrase"})[0]
	day_data['high'] = temperatures[1]
	day_data['low'] = temperatures[2]
	day_data['rain'] = soup.findAll("div",{"data-testid":"SegmentPrecipPercentage"})[4].find("span")
	day_data['humidity'] = soup.find("span",{"data-testid":"PercentageValue"})
	#return day_data
	# Turn data into text content / if .text was set above when defined, program will crash if tag isnt found
	for value in day_data:
		#print(day_data[value])
		if day_data[value] == None: continue
		#Convert into text
		day_data[value] = day_data[value].text
		# remove all symbols and letters
		if not value == 'forecast':
			day_data[value] = ''.join(e for e in day_data[value] if e.isalnum())
		# remove all strings from rain data
		if value == 'rain':
			day_data[value] = ''.join(filter(str.isdigit, day_data[value]))
		# if data ends up empty, make it hold "--"
		if day_data[value] == "": day_data[value] = "--"
	#set Icon
	day_data['icon'] = getWeatherIcon(day_data['forecast'],getDayNightSuffix())
	return day_data
#print( getWeather3() )
#print( getWeatherWeek2() )
#print (getRecipeData())
#print(getPlantingData())