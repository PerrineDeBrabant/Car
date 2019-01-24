#Imports
import datetime as dt
import argparse
import time
import json
import os

#def wait(_time):
#	time.sleep(_time)

#Used in  Traindata to save your pictures as pkl file (name)
def epoch():
    return str(int(time.time()))

#used in CarCamera to safe frames
def ms_epoch():
    return int((dt.datetime.utcnow() - dt.datetime(1970,1,1)).total_seconds() * 1000)

#this is used in our webserver to as the name says get the root
def get_root():
	return os.path.normpath(os.path.dirname(__file__))

#This is used in the file Webserver to print in our dialog screen
def print_log(_msg,_identation=0,_time=0):
	ident = '	'*_identation
	if (_time != 0):
		t = time.time() - _time
		if(t > 60):
			t = round(t/60,2)
			unit = 'm'
		elif(t > 3600):
			t = round(t/3600,2)
			unit = 'h'
		else:
			unit = 's'
		print(('%s %s. Time: %s %s')%(ident,_msg,t,unit))
		return time.time()
	else:
		print(('%s %s')%(ident,_msg))

#Set de default mode on True if you want to change to train mode
### CHANGE TO GO IN TRAIN MODE
def get_args():
	parser = argparse.ArgumentParser(prog='drive')
	parser.add_argument('--train', help='Set for train mode', action="store_true", default=False
)
	parsed_args = parser.parse_args()
	return parsed_args

#Here we get all the parameters from the json file that we have defined, make sure you use the correct path!
def get_params(_train):
	with open('static/config/config.json') as f:
		data = json.load(f)
	params = {
		'car_params': {
			 'width': data['width']
			,'height': data['height']
			,'name': data['title']
			,'pigame': data['pigame']
			,'verbose': data['verbose']
			,'channels': data['channels']
			,'car_config': data['car_config']
		}

		,'camera_params':{
			 'path': data['train_data_storage']
			,'width': data['width']
			,'height': data['height']
		}
		,'webserver_params':{
			 'require_login': data['required_login']
			,'port': data['port']
			,'cookie': data['cookie']
			,'car': None

		}
	}
	print(params)
	if(_train):
		print("I'm loading the train parameters")
		params['train_data_params'] = {
				 'path': data['train_data_storage']
				,'width': data['width']
				,'height': data['height']
				,'channels': data['channels']
			}
	else:
		print("I'm loading my model")
		print(data["model"])
		params['brain_params'] = {
				'model': data['model']
			}
	return params
