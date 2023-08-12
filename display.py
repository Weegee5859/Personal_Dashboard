# Imports
from difflib import SequenceMatcher
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
# Libraries made for this Project
from routines import *
from getdata import *

# Define Routine
routine = Routine()
# Add Routines
routine.addTask(name="weather",function=getWeather3,update_per_min=2)
routine.addTask(name="weather_week",function=getWeatherWeek2,update_per_min=15)
routine.addTask(name="word",function=getWordData,update_per_min=90)
routine.addTask(name="prayer",function=getPrayerData,update_per_min=90)
routine.addTask(name="recipe",function=getRecipeData,update_per_min=5)
routine.addTask(name="planting",function=getPlantingData,update_per_min=5)
routine.runRoutine()
# Print Routine Data one by one
for key, item in routine.getRoutineData().items():
	print(key, '->', item)

# Define Flask and SocketIO Server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# Socket IO Functions
# Upon Inital Connect force update the page
@socketio.on('connect')
def test():
	socketio.emit('update_display_on_connect', routine.getRoutineData())
# Update Page
@socketio.on('update_me')
def test():
	routine.runRoutine()
	socketio.emit('update_display', routine.getRoutineData())	
# Flask Functions
@app.route('/')
def home():
	return render_template('home.html')

if __name__ == '__main__':
	#socketio.disconnect()
	socketio.run(app,host='0.0.0.0',port='5000',allow_unsafe_werkzeug=True)