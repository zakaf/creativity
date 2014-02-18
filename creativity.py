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
#from bs4 import BeautifulSoup
import logging

#setting debugging output level
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.NOTSET)

#input parameters for first search
#queryParameters (#1 input)
databaseId = 'WOS'
query = 'AU=Chomczynski, P'
editions = {
	'collection':'WOS',
	'edition':'SCI',
}
sTimeSpan = None
timeSpan = {
	'begin':'1980-01-01',
	'end':'2013-12-31',
}
language = 'en'
queryParameters = { 'databaseId': databaseId, 'userQuery': query, 'editions': [editions,],
					'symbolicTimeSpan': sTimeSpan, 'timeSpan':[timeSpan,], 'queryLanguage':language, }

#retrieveParameters (#2 input)
firstRecord = 1
count = 2
sortField = {
	'name':'TC',
	'sort':'D'
}
viewField = None
option = { 
	'key':'RecordIDs',
	'value':'On',
}
retrieveParameters = { 	'firstRecord': firstRecord, 'count': count, 'sortField': sortField,
						'viewField': viewField, 'option': [option,], }

#url of wsdl files of web of science
authenticateUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
queryUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'

#creating suds clients and retrieving session id
authenticateClient = Client(authenticateUrl)
queryClient = Client(queryUrl)
try:
	#getting session id through authentication
	SID = authenticateClient.service.authenticate()
except WebFault, e:
	print e

#setting session id to the header of the search request
queryClient.set_options(headers={'Cookie':"SID=\""+SID+"\""})
try:
	search_result = queryClient.service.search(queryParameters,retrieveParameters)
except WebFault, e:
	print e

#print search_result
#search_result is a complex structure
#queryId, recordsFound, recordsSearched
#optionValue (contains option value specified in input parameter)

#records (actual records)
#soup = BeautifulSoup(search_result.records)
#print(soup.prettify())

# record id of the work with the most number of citations
highly_cited_rid = search_result.optionValue[0].value[0]
print search_result.optionValue[0].value[0]


try:
	authenticateClient.service.closeSession()
except WebFault, e:
	print e




