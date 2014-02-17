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

authenticateUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
queryUrl = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'

authenticateClient = Client(authenticateUrl)
SID = authenticateClient.service.authenticate()
print SID
queryClient = Client(queryUrl)
queryParameters = queryClient.factory.create('queryParameters')
queryParameters.databaseId = 'WOS'
queryParameters.userQuery = 'TS=(cadmium OR lead)'
queryParameters.queryLanguage = 'en'
editions = {
	'collection':'WOS',
	'edition':'SCI',
}
queryParameters.editions = [editions,]
timeSpan = {
	'begin':'2000-01-01',
	'end':'2013-12-31',
}
queryParameters.timeSpan = [timeSpan,]


retrieveParameters = queryClient.factory.create('retrieveParameters')
retrieveParameters.firstRecord=1
retrieveParameters.count=5
option = {
	'key':'RecordIDs',
	'value':'On',
}
retrieveParameters.option=[option,]


queryClient.set_options(headers={'Cookie':SID})
search_result = queryClient.service.search(queryParameters,retrieveParameters)
result = authenticateClient.service.closeSession()
print result




