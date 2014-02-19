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
		try:
			search_result = self.client.service.search(queryParameters,retrieveParameters)
		except suds.WebFault, e:
			print e
		return search_result
	def citingArticles (self, queryParameters, uid, retrieveParameters):
		try:
			citing_result = self.client.service.citingArticles(
					queryParameters['databaseId'],
					uid,
					queryParameters['editions'],
					queryParameters['timeSpan'],
					queryParameters['queryLanguage'],
					retrieveParameters)
		except suds.WebFault, e:
			print e
		return citing_result

#VARIABLES
#Author name hard coded for the purpose of programming later to be changed as input
AuthorName = "Chomczynski, P"

#instance of Authenticate created and authenticateSession is called
authentication = Authenticate()
authentication.authenticateSession()
print '\n'+"Current Session ID "
print authentication.SID
print "-----------"

#instance of Query created
query = Query(authentication.SID)

#queryParameters (#1 input)
databaseId = 'WOS'
query = 'AU='+AuthorName
editions = { 'collection':'WOS', 'edition':'SCI', }
sTimeSpan = None
timeSpan = { 'begin':'1980-01-01', 'end':'2013-12-31', }
language = 'en'
queryParameters_S = { 	'databaseId': databaseId, 'userQuery': query, 'editions': [editions,],
						'symbolicTimeSpan': sTimeSpan, 'timeSpan': [timeSpan,], 
						'queryLanguage': language, }

#retrieveParameters (#2 input)
firstRecord = 1
count = 1
sortField = { 'name':'TC', 'sort':'D' }
viewField = None
option = { 'key':'RecordIDs', 'value':'On', }
retrieveParameters_S = {	'firstRecord': firstRecord, 'count': count, 'sortField': sortField,
							'viewField': viewField, 'option': [option,], }

#search is called from query
search_result = query.search(queryParameters_S,retrieveParameters_S)
rid = search_result.optionValue[0].value[0]

#printing result
print '\n'+"Most higly cited work of "+AuthorName
print rid
print "-----------"

#input parameter for citingArticles
firstRecord = 1
count = 5
retrieveParameters_CA = { 'firstRecord': firstRecord, 'count': count, 'sortField': [sortField,],
							'viewField': viewField, 'option': [option,], }

#citingAriticles is called from query
citing_result = query.citingArticles(queryParameters_S,rid,retrieveParameters_CA)
rid_list = citing_result.optionValue[0].value

#printing result
print '\n'+"5 works that cited the most highly cited workd of "+AuthorName+" (in descending order)"
print rid_list
print "----------"

#closing session before program exits
authentication.closeSession()


