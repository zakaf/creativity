#!/usr/bin/env python

# Copyright (c) 2014 Dongkeun Lee
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from bs4 import BeautifulSoup
from collections import deque
from collections import Counter
from datetime import datetime, date
from peewee import *
from suds.client import Client
import csv, codecs, cStringIO
import logging
import operator
import time
import suds
import sys
import re

#setting debugging output level
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.NOTSET)

#url of wsdl files of web of science
authenticateUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
queryUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'

#database configuration
DATABASE = 'database_creativity.db'
database = SqliteDatabase(DATABASE)

#database using peewee
#model defintion of database
class BaseModel(Model):
	class Meta:
		database = database

class Author(BaseModel):
	name = CharField()
	num_of_work = IntegerField(default = 0)

class Email(BaseModel):
	author = ForeignKeyField(Author, related_name='authorEmail')
	email = CharField()
	date = DateField()

class Work(BaseModel):
	title = CharField()

class AuthorWork(BaseModel):
	author = ForeignKeyField(Author, related_name='authorWork')
	work = ForeignKeyField(Work, related_name='authorWork')

class Address(BaseModel):
	author = ForeignKeyField(Author, related_name='authorAddress')
	city = CharField()
	state = CharField()
	country = CharField()
	date = DateField()

class Cocitation(BaseModel):
	inputRelationship = ForeignKeyField(AuthorWork, related_name='inputRelationship')
	citingWork = ForeignKeyField(Work, related_name='citingWork')
	citedRelationship = ForeignKeyField(AuthorWork, related_name='citedRelationship')

class Queries(BaseModel):
	author = CharField()
	start = DateField()
	end = DateField()
	num_of_search = IntegerField()
	num_of_citing = IntegerField()
	num_of_cited = IntegerField()
	
#class for authenticating and closing session
class Authenticate (object):
	def __init__ (self):
		self.client = Client(authenticateUrl)
		self.SID = None
	def authenticateSession (self):
		try:
			time.sleep(0.5)
			self.SID = self.client.service.authenticate()
		except suds.WebFault, e:
			print e
			sys.exit()	
	def closeSession (self):
		try:	
			time.sleep(0.5)
			self.SID = self.client.service.authenticate()
			self.client.service.closeSession()
		except suds.WebFault, e:
			print e

#class for query
class Query (object):
	def __init__ (self, SID):
		self.client = Client(queryUrl)
		self.client.set_options(headers={'Cookie':"SID=\""+str(SID)+"\""})
	def search (self, queryParameters, retrieveParameters):
		try:
			result = self.client.service.search(queryParameters,retrieveParameters)
			return result
		except suds.WebFault, e:
			print e
			return self.search(queryParameters,retrieveParameters)

#return number of work an author has published
def num_of_work (query, authorName, symbolicTimeSpan, timeSpan, language):
	userQuery = 'AU='+authorName
	fRecord = 1;
	sortField = { 'name':'TC', 'sort':'D'}
	option = { 'key':'RecordIDs', 'value':'On',}
	dbId = 'WOS'
	complete_editions = [	{'collection':'WOS', 'edition':'SCI'},
							{'collection':'WOS', 'edition':'SSCI'},
							{'collection':'WOS', 'edition':'AHCI'},
							{'collection':'WOS', 'edition':'ISTP'},
							{'collection':'WOS', 'edition':'ISSHP'},
							{'collection':'WOS', 'edition':'IC'},
							{'collection':'WOS', 'edition':'CCR'},
							{'collection':'WOS', 'edition':'BSCI'},
							{'collection':'WOS', 'edition':'BHCI'}]
	
	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': complete_editions, 'symbolicTimeSpan': symbolicTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': "2", 'sortField': sortField, 'viewField': None, 'option': [option,],})
	return search_result.recordsFound
	
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "="*block + " "*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

#--------------------
#MAIN STARTS HERE
def main(argv):
	skipCount =0
	sTimeSpan = None
	timeSpan = { 'begin':'1980-01-01', 'end':'2014-12-31', }
	language = 'en'
	
	#instance of Authenticate created and authenticateSession is called
	authentication = Authenticate()
	authentication.authenticateSession()
	query = Query(authentication.SID)
	
	#database connection
	database.connect()

	#create required tables if it doesn't exist
	Author.create_table(fail_silently=True)
	Email.create_table(fail_silently=True)
	Work.create_table(fail_silently=True)
	AuthorWork.create_table(fail_silently=True)
	Address.create_table(fail_silently=True)
	Cocitation.create_table(fail_silently=True)
	Queries.create_table(fail_silently=True)
	
	#store author, work, author-work relationship and cocitation information
	author_count = 0
	total_count = Author.select().where(Author.num_of_work == 0).count()

	print "Processing",total_count,"authors"
	for x in Author.select().where(Author.num_of_work == 0):
		author_count = author_count + 1
		update_progress(author_count/float(total_count))
		#if x.name.find("NEAR,J") != -1:
		#	x.delete_instance()
		#	continue
		if x.name.find(",") == -1:
			x.delete_instance()
			continue
		#store author information
		number = num_of_work(query,x.name,sTimeSpan,timeSpan,language)
		x.num_of_work = number
		x.save()

	if total_count == Author.select().where(Author.num_of_work == 0).count():
		print "Deleting insignificant authors"
		Author.delete().where(Author.num_of_work == 0).execute()

	print "Processing AuthorWork"
	author_count = 0
	total_count = AuthorWork.select().count()
	for x in AuthorWork.select():
		author_count = author_count + 1
		update_progress(author_count/float(total_count))
		try:
			aa = Author.get(Author.id == x.author.id)
		except Author.DoesNotExist:
			x.delete_instance()
	print author_count,total_count
	print "Processing Cocitations"
	author_count = 0
	total_count = Cocitation.select().count()
	for x in Cocitation.select():
		author_count = author_count + 1
		update_progress(author_count/float(total_count))
		try:
			aa = AuthorWork.get(AuthorWork.id == x.inputRelationship.id)
			bb = AuthorWork.get(AuthorWork.id == x.citedRelationship.id)
		except AuthorWork.DoesNotExist:
			x.delete_instance()

	#database connection closed
	database.close()

	#closing session before program exits
	authentication.closeSession()

	print "Done"
	
if __name__ == "__main__":
	main(sys.argv[1:])
