#!/usr/bin/env python

#Copyright (c) 2014 Dongkeun Lee
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

from suds.client import Client
import suds
import logging
import sys
import time

#setting debugging output level
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.NOTSET)

#url of wsdl files of web of science
authenticateUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
queryUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'

#class for authenticating and closing session
class Authenticate (object):
	def __init__ (self):
		self.client = Client(authenticateUrl)
		self.SID = None
	def authenticateSession (self):
		try:
			self.SID = self.client.service.authenticate()
		except suds.WebFault, e:
			print e
			sys.exit()	
	def closeSession (self):
		try:
			self.client.service.closeSession()
		except suds.WebFault, e:
			print e

#class for query
class Query (object):
	def __init__ (self, SID):
		self.client = Client(queryUrl)
		self.client.set_options(headers={'Cookie':"SID=\""+str(SID)+"\""})
	def search (self, queryParameters, retrieveParameters):
		time.sleep(0.5)
		try:
			result = self.client.service.search(queryParameters,retrieveParameters)
			return result
		except suds.WebFault, e:
			print e
	def citingArticles (self, databaseId, uid, editions, timeSpan, language, retrieveParameters):
		time.sleep(0.5)
		try:
			result = self.client.service.citingArticles( databaseId, uid, editions, timeSpan, language, retrieveParameters)
			return result
		except suds.WebFault, e:
			print e
	def citedReferences (self, databaseId, uid, language, retrieveParameters):
		time.sleep(0.5)
		try:
			result = self.client.service.citedReferences(databaseId,uid,language,retrieveParameters)
			return result
		except suds.WebFault, e:
			print e

#functions
#Given input author, who is cocited with him
def cocitation_with (	query, 		#queryClient 
						authorName, #name of the input author
						dbId, #database to search from
						editions, 	#edition to search from
						symbolicTimeSpan, #symbolic time span to search from
						timeSpan, 	#actual time span to search from (choose symbolic or actual)
						language, 	#queryLanguage
						count_s, 	#max num of work by input to be considered
						count_ca, 	#max num of work that cites work by input to be considered
						count_cr):	#max num of author that is cocited with input to be considered
									# count_** is maximum value, because repetition is usual
	pair_list = []
	userQuery = 'AU='+authorName #query that is used to search database
	fRecord = 1; #from which record the function should start searching from
	sortField = { 'name':'TC', 'sort':'D'} #how the result is sorted (TC=times cited, D= descending)
	option = { 'key':'RecordIDs', 'value':'On',} #what optional value should be included in result

	#search is called from query
	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': [editions,], 'symbolicTimeSpan': sTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': count_s, 'sortField': sortField, 'viewField': None, 'option': [option,],})

	#citingAriticles is called from query
	for x in search_result.optionValue[0].value:
		citing_result = query.citingArticles( dbId, x, [editions,], [timeSpan,], language, { 'firstRecord': fRecord, 'count': count_ca, 'sortField': [sortField,], 'viewField': None, 'option': [option,],})
		
		#citedReferences is called from query
		for y in citing_result.optionValue[0].value:
			cited_result = query.citedReferences( dbId, y, language, { 'firstRecord': fRecord, 'count': count_cr, 'sortField': [sortField,],	'viewField': None, 'option': None, })
			
			for z in cited_result.references:
				pair_list.append({'input':authorName.upper(), 'output':z.citedAuthor.upper()})

	#if output and input is the same, remove it as that is unnecessary tuple
	for x in pair_list:
		if x['input'] == x['output']:
			pair_list.remove({'input':x['input'], 'output':x['output']})
	return pair_list

#--------------------
#MAIN STARTS HERE

#VARIABLES
authorName = "Chomczynski, P"

#instance of Authenticate created and authenticateSession is called
authentication = Authenticate()
authentication.authenticateSession()

#instance of Query created
query = Query(authentication.SID)

databaseId = 'WOS'
editions = { 'collection':'WOS', 'edition':'SCI', }
sTimeSpan = None
timeSpan = { 'begin':'1980-01-01', 'end':'2013-12-31', }
language = 'en'
count_search = 2
count_ca = 5
count_cr = 2

#explanation of arguments are done in the actual function itself
pair_list = cocitation_with(query, authorName, databaseId, editions, sTimeSpan, timeSpan, language, count_search, count_ca, count_cr)

#closing session before program exits
authentication.closeSession()

#print output
for x in pair_list:
	print x['input'] + " :  " + x['output']
