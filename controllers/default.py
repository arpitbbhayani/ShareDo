#!/usr/bin/python

def index():
	if session.name != None:
		redirect(URL('sharedo' , 'user' , 'index'))
	return dict()