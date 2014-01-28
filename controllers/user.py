#!/usr/bin/python
from distutils.log import info

import constants
from gluon.validators import CRYPT, LazyCrypt

######################################################################################################################

def get_event_by_id(event_id):
	return db(db.events.id == event_id).select()[0]

def get_action_by_id(action_id):
	return db(db.actions.id == action_id).select()[0]

def get_all_blink_details():
	"""
	Returns all the user blinks
	"""
	records = db(db.blinks.user_id == session.user_id).select()
	for row in records:
		event = get_event_by_id(row.event_id)
		action = get_action_by_id(row.action_id)
		row['event'] = event
		row['action'] = action
	return records.json()

def signup():
	error = ""

	#crypt = CRYPT(digest_alg=constants.DIGEST_ALG , key=constants.DIGEST_KEY , salt=True)
	#str(LazyCrypt(crypt, pwd))

	if session.name != None:
		redirect(URL('sharedo' , 'user' , 'index'))
		return;

	if request.vars.email_id and request.vars.pwd and request.vars.pass_c and request.vars.name:
		"""If signup request made"""

		username = request.vars.email_id
		pwd = request.vars.pwd
		name = request.vars.name

		# Number of records should be zero
		records = db( (db.auth_user.email == username) | (db.auth_user.first_name == username) ).select()
		if len(records) == 0:
			db.auth_user.insert(email = username , password = pwd , first_name = name)
			redirect(URL('sharedo' , 'user' , 'index'))
		else:
			error = username + " already registered."

	return dict(error=error)

def login():
	"""Called when login.html is loaded"""

	error = ""

	if session.name != None:
		redirect(URL('sharedo' , 'user' , 'index'))
		return;

	if request.vars.email_id and request.vars.pass_c:
		"""If login request is made"""

		username = request.vars.email_id
		pwd = request.vars.pass_c

		# Number of records must be 1 as the username is unique
		records = db((db.auth_user.email == username) | (db.auth_user.first_name == username)).select()
		if len(records) == 1:
			row = records[0]
			#if db.auth_user.password.validate(pwd) == (db(db.auth_user.email == username).select().first().password, None):
			if row.password == pwd:
				session.user_id = row.id
				session.name = row.first_name
				session.username = row.email
				redirect(URL('sharedo', 'user', 'index'))
			else:
				error = constants.ERR_INVALID_USER
		elif len(records) > 1:
			"""This condition should never occur. If occurs we are doomed!"""
			error = constants.ERR_FATAL
		else:
			error = constants.ERR_INVALID_USER
	
	return dict(error=error)

def profile():

	profile_info = {}

	records = db((db.auth_user.first_name == session.name)).select(
		db.auth_user.first_name ,
		db.auth_user.email)

	for i in records:
		profile_info['name'] = i.first_name
		profile_info['email_id'] = i.email

	return profile_info

def index():
	if session.name == None:
		redirect(URL('sharedo' , 'default' , 'index'))

	a = get_all_blink_details()
	import simplejson as json

	return dict(blink_details = json.loads(a))


def under_construction():
	return dict()