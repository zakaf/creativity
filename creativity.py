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
import csv
from collections import deque
from bs4 import BeautifulSoup

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
	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': [editions,], 'symbolicTimeSpan': symbolicTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': count_s, 'sortField': sortField, 'viewField': None, 'option': [option,],})

	if search_result.recordsFound == 0:
		print "No Search Result for " + authorName
		return pair_list

	searchTitle = BeautifulSoup(search_result.records, "xml")

	title_list1 = deque()
	for t in searchTitle.find_all(type="item"):
		title_list1.append(t.string)

	#citingAriticles is called from query
	for x in search_result.optionValue[0].value:

		x_title = title_list1.popleft()

		citing_result = query.citingArticles( dbId, x, [editions,], [timeSpan,], language, { 'firstRecord': fRecord, 'count': count_ca, 'sortField': [sortField,], 'viewField': None, 'option': [option,],})
		
		if citing_result.recordsFound == 0:
			continue

		#citedReferences is called from query
		for y in citing_result.optionValue[0].value:
			cited_result = query.citedReferences( dbId, y, language, { 'firstRecord': fRecord, 'count': count_cr, 'sortField': [sortField,], 'viewField': None, 'option': None, })
			
			if len(cited_result.references) == 0:
				continue

			for z in cited_result.references:
				try:
					pair_list.append({'input':authorName.upper(), 'output':z.citedAuthor.upper().replace(" ",""), 'inputWork':str(x_title).upper(), 'citingWork':y, 'outputWork':z.citedTitle.upper()})
				except AttributeError:
					pass

	#if output and input is the same, remove it as that is unnecessary tuple
	for x in pair_list:
		if x['input'] == x['output']:
			pair_list.remove({'input':x['input'], 'output':x['output'], 'inputWork':x['inputWork'], 'citingWork':x['citingWork'],'outputWork':x['outputWork']})
	return pair_list

def list_count (pair_list):
	new_list = []
	for x in pair_list:
		if len(new_list) == 0:
			new_list.append({'input':x['input'], 'output':x['output'], 'count':1, 'reference':[{'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']},]})
			continue
		new = 1
		for y in new_list:
			if x['input'] == y['input'] and x['output'] == y['output']:
				y['count'] = y['count'] +1
				y['reference'].append({'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']})
				new = 0
				break
		if new == 1:
			new_list.append({'input':x['input'], 'output':x['output'], 'count':1, 'reference':[{'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']},]})
		new_list = sorted(new_list,key=lambda tuples: (tuples['count']*-1, tuples['output']))
	return new_list

def duplicate_check_prepare (pair_list):
	for x in pair_list:
		if cmp(x['input'],x['output']) > 0:
			y = x['input']
			x['input'] = x['output']
			x['output'] = y
	pair_list = sorted(pair_list,key=lambda tuples: (tuples['input'], tuples['output']))
	return pair_list

#--------------------
#MAIN STARTS HERE
def main(argv):
	authorNames = deque([])
	doneNames = []
	skipCount =0
	databaseId = 'WOS'
	editions = { 'collection':'WOS', 'edition':'SCI', }
	sTimeSpan = None
	timeSpan = { 'begin':'1980-01-01', 'end':'2013-12-31', }
	language = 'en'
	count_search = 2
	count_ca = 5
	count_cr = 2
	numAuthor = 1
	total_list = []
	
	
	if len(argv) != 3:
		print "Error: Not Enough Argument"
		sys.exit(2)
	
	authorNames.append(argv[0])
	inputfile =  argv[1]
	outputfile = argv[2]

	try:
		f = open(inputfile,'r')
		lines = f.readlines()
		f.close()
	except IOError as e:
		print "File I/O Eror"
		sys.exit(1)
	

	for line in lines:
		if line[0][0] == '#':
			skipCount = skipCount+1
		else:
			if skipCount == 1:
				databaseId = line.rstrip('\n')
			elif skipCount == 2:
				editions = { 'collection':databaseId, 'edition':line.rstrip('\n'), }
			elif skipCount == 3:
				timeSpan['begin'] = line.rstrip('\n')
			elif skipCount == 4:
				timeSpan['end'] = line.rstrip('\n')
			elif skipCount == 5:
				language = line.rstrip('\n')
			elif skipCount == 6:
				count_search = line.rstrip('\n')
			elif skipCount == 7:
				count_ca = line.rstrip('\n')
			elif skipCount == 8:
				count_cr = line.rstrip('\n')
			elif skipCount == 9:
				numAuthor = int(line.rstrip('\n'))
			else:
				break

	#instance of Authenticate created and authenticateSession is called
	authentication = Authenticate()
	authentication.authenticateSession()
	
	while True:	

		authorName = authorNames.popleft()

		print "AuthorName"	
		print authorName

		#instance of Query created
		query = Query(authentication.SID)
		
		#explanation of arguments are done in the actual function itself
		pair_list = cocitation_with(query, authorName, databaseId, editions, sTimeSpan, timeSpan, language, count_search, count_ca, count_cr)
		
		total_list = total_list + pair_list

		#print output
		count_list = list_count(pair_list)

		doneNames.append(authorName)

		for x in count_list:
			duplicate = False
			for y in authorNames:
				if y == x['output']:
					duplicate = True
					break
			for z in doneNames:
				if z == x['output']:
					duplicate = True
					break
			if duplicate == False:
				authorNames.append(x['output'])
			if len(doneNames) + len(authorNames) >= numAuthor:
				break

		if len(doneNames) == numAuthor:
			break

	#closing session before program exits
	authentication.closeSession()

	total_list = duplicate_check_prepare(total_list)
	for z in total_list:
		print z['input'] + " " + z['output'] + " " + z['inputWork'] + " " + z['citingWork'] + " " + z['outputWork']
	total_list = list_count(total_list)
	#duplicate removal needed based on the reference		

	with open(outputfile+".csv",'ab') as f:
		writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
		for row in total_list:
			writer.writerow([row['input'],row['output'],row['count']])

if __name__ == "__main__":
	main(sys.argv[1:])
