#!/usr/bin/python

from constants import *
import simplejson as json

#################################################################
						#Generic Methods#
#################################################################

def get_user():
	records = db((db.auth_user.first_name == session.name) | (db.auth_user.email == session.name)).select()
	if len(records) > 1 or len(records) == 0:
		raise HTTP(HTTP_SERVER_ERROR)

	return records[0]

def get_auth_token(user_id, provider_name):
	records = db((db.auth_tokens.user_id == user_id) & (db.auth_tokens.provider == provider_name)).select()
	if len(records) > 1 or len(records) == 0:
		return None

	return records[0]

def new_token():
	"""
	Adds new token to the auth_tokens table.
	If it already exists then updates the token.
	"""
	if request.env.request_method.upper() != REQ_METHOD_POST:
		raise HTTP(HTTP_METHOD_NOT_ALLOWED)

	if request.env.http_provider not in PROVIDER_LIST:
		raise HTTP(HTTP_NOT_ACCEPTABLE)

	user = get_user()
	auth_token = get_auth_token(user.id, request.env.http_provider)

	if auth_token:
		# Update the existing auth tokens
		auth_token.token = request.env.http_oauth_token
		auth_token.secret = request.env.http_oauth_token_secret
		auth_token.update_record()
	else:
		# insert new record
		db.auth_tokens.insert(user_id=user.id, provider=request.env.http_provider, token=request.env.http_oauth_token, secret=request.env.http_oauth_token_secret)

		auth_token = get_auth_token(user.id, request.env.http_provider)
		if request.env.http_provider == PROVIDER_TWITTER:
			twitter = twitter_init(auth_token)
			get_tweets_since(twitter, user.id, auth_token, 1)

		elif request.env.http_provider == PROVIDER_TWITTER:
			instagr = instagr_init(auth_token)
			get_instagr_posts(instagr, user.id, auth_token, 1)

	return

def logout():
	"""Logsout a user"""
	session.user_id = None
	session.name = None
	session.username = None

def user_present():
	""" Checks if a user with registered Nickname is present in the database """
	val = request.env.http_val
	records = db((db.auth_user.first_name == val)).select()

	if len(records) == 1:
		return True
	return False

def email_present():
	""" Checks if a user with registered email is present in the database """
	val = request.env.http_val
	records = db((db.auth_user.email == val)).select()

	if len(records) == 1:
		return True
	return False

def events():
	dict_ = dict()
	dict_['events'] = str(db(db.events.provider == request.env.http_provider).select().json())
	return json.dumps(dict_)

def actions():
	dict_ = dict()
	dict_['actions'] = str(db(db.actions.provider == request.env.http_provider).select().json())
	import simplejson as json
	return json.dumps(dict_)

def add_blink():
	user = get_user();
	records = db((db.blinks.user_id == session.user_id) & (db.blinks.event_id == int(request.env.http_event_id)) & (db.blinks.action_id == int(request.env.http_action_id))).select()
	if len(records) == 0:
		db.blinks.insert(user_id=user.id, event_id= int(request.env.http_event_id) , in_data=request.env.http_in_data, action_id= int(request.env.http_action_id))
	pass;

def is_user_authorized():
	records = db((db.auth_tokens.user_id == session.user_id) & (db.auth_tokens.provider == request.env.http_provider)).select()
	if len(records) == 0:
		return False
	else:
		return True

def send_email():
	subject = request.env.http_from + ' - ' + request.env.http_subject
	message = request.env.http_body
	print subject
	print message
	mail.send(to = 'contact.share.do@gmail.com' , subject = subject , message= message)
	pass

########################################################################
							#Twitter#
########################################################################
from twython import Twython

TWITTER_CONS_KEY = "rGmgLbYUw2Au7UUrQAjnfQ"
TWITTER_CONS_SEC = "yXIPMf6PHoaAgZZnhBQV7AhJG40kpXgif1V3hejqo"

def twitter_init(auth_token):
	twitter = Twython(TWITTER_CONS_KEY, TWITTER_CONS_SEC, auth_token.token , auth_token.secret)
	return twitter

def set_user_twitter():
	user = get_user()
	auth_token = get_auth_token(user.id, PROVIDER_TWITTER)

	twitter = twitter_init(auth_token)
	a = twitter.verify_credentials()
	screen_name = a[u'screen_name']
	last_pro = int(twitter.get_user_timeline(screen_name = screen_name , count = 1)[0][u'id'])

	auth_token.screen_name = screen_name
	auth_token.last_pro = last_pro
	auth_token.update_record()

def get_tweets_since(twitter, user_id, auth_token = None, count = 100):
	if not auth_token:
		auth_token = get_auth_token(user_id, PROVIDER_TWITTER)

	since_id = auth_token.last_pro
	while True:
		tweets = twitter.get_user_timeline(screen_name = auth_token.screen_name, count = count, since_id = since_id)

		if len(tweets) > 0:
			since_id = tweets[0][u'id']

		# break if this is the first scan
		if not auth_token.last_pro:
			break

		length = len(tweets)
		if length < count:
			break

	# Updating the since_id for tweets after fetching the required number of tweets
	if since_id != auth_token.last_pro:
		auth_token.last_pro = since_id
		auth_token.update_record()

	return tweets

#def get_tweets():
#	auth_token = get_auth_token(session.user_id, PROVIDER_TWITTER)
#	twitter = twitter_init(auth_token)
#	print get_tweets_since(twitter, session.user_id, auth_token)


########################################################################
							#Facebook#
########################################################################
import facebook
def fb_init(auth_token):
	fb = facebook.GraphAPI(auth_token.token)
	return fb

#def fb_profile():
#	user = get_user()
#	auth_token = get_auth_token(user.id, PROVIDER_FB)
#	fb = fb_init(auth_token)
#	return fb.get_object('me')

#def fb_posts():
#	user = get_user()
#	auth_token = get_auth_token(user.id, PROVIDER_FB)
#	fb = fb_init(auth_token)
#	return fb.request('me/posts')

########################################################################
							#Instagram#
########################################################################
from instagram.client import InstagramAPI

def instagr_init(auth_token):
	instagr = InstagramAPI(access_token = auth_token.token)
	return instagr

def get_instagr_posts(instagr, user_id, auth_token = None, count = 1):
	if not auth_token:
		auth_token = get_auth_token(user_id, PROVIDER_INSTAGRAM)

	since_id = auth_token.last_pro
	user = instagr.user()


	recent_media, next = instagr.user_recent_media(user_id = user.id, count = count)

	length = len(recent_media)
	if length > 0:
		since_id = recent_media[0].id.split('_')[0]

	# break if this is the first scan
	#if not auth_token.last_pro:
	#	break

	#if length < count:
	#	break

	# Updating the since_id for tweets after fetching the required number of tweets
	#print "since id", since_id
	#print "auth", auth_token.last_pro
	if since_id != auth_token.last_pro:
		#print 'Updating...'
		auth_token.last_pro = str(since_id)
		auth_token.update_record()

	return recent_media


########################################################################
							#Blinks#
########################################################################

providers_dict = {PROVIDER_TWITTER: twitter_init, PROVIDER_FB: fb_init, PROVIDER_INSTAGRAM: instagr_init}

def get_provider_object(user_id, provider):
	try:
		auth_token = get_auth_token(user_id, provider)
		return providers_dict[provider](auth_token)
	except KeyError as err:
		return None

def get_event_by_id(event_id):
	return db(db.events.id == event_id).select()[0]

def get_action_by_id(action_id):
	return db(db.actions.id == action_id).select()[0]

def get_blinks(user_id):
	return db((db.blinks.id > 0) & (db.blinks.user_id == user_id)).select()

def take_fb_actions(blink, data_records, event, action_provider):
	print 'fb', data_records
	print 'something', event.in_type
	for data in data_records:
		if event.in_type == 'copy':
			if event.provider == PROVIDER_TWITTER:
				msg = data[u'text']
			elif event.provider == PROVIDER_INSTAGRAM:
				msg = data.caption.text + ' ' + data.link

			action_provider.put_object('me', 'feed', message = msg)

		elif event.in_type == 'hash':
			if event.provider == PROVIDER_TWITTER:
				hashtags = data[u'entities'][u'hashtags']
				for tag in hashtags:
					if tag[u'text'] == blink.in_data:
						action_provider.put_object('me', 'feed', message = data[u'text'])
						break

			elif event.provider == PROVIDER_INSTAGRAM:
				if blink.in_data in data.tags:
					msg = data.caption.text + ' ' + data.link
					action_provider.put_object('me', 'feed', message = msg)

		elif event.in_type == 'link':
			if event.provider == PROVIDER_TWITTER:
				try:
					urls = data[u'entities'][u'urls']
					if len(urls) > 0 or len(media) > 0:
						action_provider.put_object('me', 'feed', message = data[u'text'])
						break;
				except KeyError as err:
					pass

def take_twitter_actions(blink, data_records, event, action_provider):
	for data in data_records:

		if event.in_type == 'copy':
			if event.provider == PROVIDER_INSTAGRAM:
				msg = ''
				if data.caption:
					msg = data.caption.text
				msg += ' ' + data.link

			action_provider.update_status(status = msg)
		elif event.in_type == 'hash':
			print 'tags', data.tags[0].name
			if event.provider == PROVIDER_INSTAGRAM:
				for tag in data.tags:
					if blink.in_data == tag.name:
						msg = ''
						if data.caption:
							msg = data.caption.text
						msg += ' ' + data.link
						action_provider.update_status(status = msg)
		elif event.in_type == 'link':
			pass


def apply_all_blinks():
	"""
	Scan and execute all the blinks of the calling user.
	"""
	records = get_blinks(session.user_id)
	tweets = None
	instagr_posts = None
	data_records = None

	for blink in records:
		event = get_event_by_id(blink.event_id)
		action = get_action_by_id(blink.action_id)

		event_provider = get_provider_object(session.user_id, event.provider)
		action_provider = get_provider_object(session.user_id, action.provider)

		if type(event_provider) is Twython and not tweets:
			tweets = get_tweets_since(event_provider, session.user_id)
			data_records = tweets
		elif type(event_provider) is InstagramAPI and not instagr_posts:
			instagr_posts = get_instagr_posts(event_provider, session.user_id)
			data_records = instagr_posts

		if type(action_provider) is facebook.GraphAPI:
			take_fb_actions(blink, data_records, event, action_provider)

		elif type(action_provider) is Twython:
			take_twitter_actions(blink, data_records, event, action_provider)

def delete_blink():
	"""
	Delete an existing blink. Takes a blink_id parameter in headers
	"""
	blink_id = request.env.http_blink_id
	db(db.blinks.id == blink_id).delete()
	return

def apply_blink():
	"""
	Applies a particular blink. Expects a blink_id in headers
	"""
	tweets = None
	instagr_posts = None
	data_records = None
	blink_id = request.env.http_blink_id
	records = db(db.blinks.id == blink_id).select()
	if len(records) > 0:
		blink = records[0]
		event = get_event_by_id(blink.event_id)
		action = get_action_by_id(blink.action_id)

		print 'event', event
		event_provider = get_provider_object(session.user_id, event.provider)
		action_provider = get_provider_object(session.user_id, action.provider)

		if type(event_provider) is Twython and not tweets:
			tweets = get_tweets_since(event_provider, session.user_id)
			data_records = tweets
		elif type(event_provider) is InstagramAPI and not instagr_posts:
			instagr_posts = get_instagr_posts(event_provider, session.user_id)
			data_records = instagr_posts

		if type(action_provider) is facebook.GraphAPI:
			take_fb_actions(blink, data_records, event, action_provider)

		elif type(action_provider) is Twython:
			take_twitter_actions(blink, data_records, event, action_provider)