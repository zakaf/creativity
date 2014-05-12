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

from bs4 import BeautifulSoup
from collections import deque
from collections import Counter
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
	location_list = []
	userQuery = 'AU='+authorName
	fRecord = 1;
	sortField = { 'name':'TC', 'sort':'D'}
	option = { 'key':'RecordIDs', 'value':'On',}

	#search is called from query
	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': [editions,], 'symbolicTimeSpan': symbolicTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': count_s, 'sortField': sortField, 'viewField': None, 'option': [option,],})
	if search_result.recordsFound == 0:
		print "No Search Result for " + authorName
		return pair_list

	#BeautifulSoup is used to retrieve the title of the work from full records text
	searchTitle = BeautifulSoup(search_result.records, "xml")
	title_list1 = deque()

	for t in searchTitle.find_all(type="item"):
		title_list1.append(t.string)

	for t in searchTitle.find_all("reprint_contact"):
		if t("wos_standard") == []:
			continue
		else:
			lname = (t("wos_standard"))[0].string
			if t("city") == []:
				lcity = ""
			else:
				lcity = (t("city"))[0].string
			if t("state") == []:
				lstate = ""
			else:
				lstate = (t("state"))[0].string
			if t("country") == []:
				lcountry = ""
			else:
				lcountry = (t("country"))[0].string
			if t("zip") == []:
				lzip = ""
			else:
				lzip = (t("zip"))[0].string
			if lcity == "" and lstate == "" and lcountry == "" and lzip == "":
				continue
			location_list.append({'name': lname, 'city': lcity, 'state': lstate, 'country': lcountry, 'zip': lzip})

	#citingAriticles is called from query
	for x in search_result.optionValue[0].value:

		x_title = title_list1.popleft()

		citing_result = query.citingArticles( dbId, x, [editions,], [timeSpan,], language, { 'firstRecord': fRecord, 'count': count_ca, 'sortField': [sortField,], 'viewField': None, 'option': [option,],})
		
		if citing_result.recordsFound == 0:
			continue

		citingTitle = BeautifulSoup(citing_result.records, "xml")
		title_list2 = deque()
		for t in citingTitle.find_all(type="item"):
			title_list2.append(t.string)

		for t in citingTitle.find_all("reprint_contact"):
			if t("wos_standard") == []:
				continue
			else:
				lname = (t("wos_standard"))[0].string
				if t("city") == []:
					lcity = ""
				else:
					lcity = (t("city"))[0].string
				if t("state") == []:
					lstate = ""
				else:
					lstate = (t("state"))[0].string
				if t("country") == []:
					lcountry = ""
				else:
					lcountry = (t("country"))[0].string
				if t("zip") == []:
					lzip = ""
				else:
					lzip = (t("zip"))[0].string
				if lcity == "" and lstate == "" and lcountry == "" and lzip == "":
					continue
				location_list.append({'name': lname, 'city': lcity, 'state': lstate, 'country': lcountry, 'zip': lzip})

		#citedReferences is called from query
		for y in citing_result.optionValue[0].value:
			
			y_title = title_list2.popleft()

			cited_result = query.citedReferences( dbId, y, language, { 'firstRecord': fRecord, 'count': count_cr, 'sortField': [sortField,], 'viewField': None, 'option': None, })
			
			if len(cited_result.references) == 0:
				continue
		
			for z in cited_result.references:
				try:
					#if inputWork and outputWork is the same, skip
					if cmp(unicode(x_title).encode('utf-8').upper(),z.citedTitle.upper()) == 0:
						continue
					#first author should be alphabetically before the second author
					elif cmp(authorName.upper(), z.citedAuthor.upper().replace(", ",",")) < 0:
						pair_list.append({'input':authorName.upper(), 'output':z.citedAuthor.upper().replace(", ",","), 'inputWork':unicode(x_title).encode('utf-8').upper(), 'citingWork':unicode(y_title).encode('utf-8').upper(), 'outputWork':z.citedTitle.upper()})
					elif cmp(authorName.upper(), z.citedAuthor.upper().replace(", ",",")) > 0:
						pair_list.append({'input':z.citedAuthor.upper().replace(", ",","), 'output':authorName.upper(), 'inputWork':unicode(x_title).encode('utf-8').upper(), 'citingWork':unicode(y_title).encode('utf-8').upper(), 'outputWork':z.citedTitle.upper()})
				except AttributeError:
					pass

	print location_list
	return pair_list

#count the number of the co-citation between the two authors
def list_count (pair_list):
	new_list = []
	for x in pair_list:
		if len(new_list) == 0:
			new_list.append({'input':x['input'], 'output':x['output'], 'count':1, 'reference':[{'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']},]})
			continue
		new = 1
		for y in new_list:
			if cmp(x['input'],y['input']) == 0 and cmp(x['output'],y['output']) == 0:
				y['count'] = y['count'] +1
				y['reference'].append({'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']})
				new = 0
				break
		if new == 1:
			new_list.append({'input':x['input'], 'output':x['output'], 'count':1, 'reference':[{'inputWork':x['inputWork'],'citingWork':x['citingWork'],'outputWork':x['outputWork']},]})
	new_list = sorted(new_list,key=lambda tuples: (tuples['count']*-1, tuples['input'], tuples['output']))
	return new_list

#remove any duplicate from the list before counting
def duplicate_reference (pair_list):
	pair_list = sorted(pair_list,key=lambda tuples: (tuples['input'], tuples['output'],tuples['inputWork'],tuples['citingWork'],tuples['outputWork']))
	new_list = []
	for x in pair_list:
		if len(new_list) == 0:
			last = x
			new_list.append(last)
			continue
		if x == last:
			continue
		last = x
		new_list.append(last)
	return new_list

class UnicodeWriter:

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

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
	
	
	if len(argv) != 4:
		print "Sample Usage: creativity inputAuthor inputSettingFileName outputFileName1 outputFileName2"
		sys.exit(2)
	
	authorNames.append(argv[0])
	inputfile =  argv[1]
	outputfile1 = argv[2]
	outputfile2 = argv[3]

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

		#instance of Query created
		query = Query(authentication.SID)
		
		#explanation of arguments are done in the actual function itself
		pair_list = cocitation_with(query, authorName, databaseId, editions, sTimeSpan, timeSpan, language, count_search, count_ca, count_cr)
		
		#complete list of co-citation
		total_list = total_list + pair_list

		#to find the next author to search co-citation for
		pair_list = duplicate_reference(pair_list)
		count_list = list_count(pair_list)

		doneNames.append(authorName)

		#find next possible author for search based on the number of co-citation they have from current search
		for x in count_list:
			induplicate = False
			outduplicate = False
			for y in authorNames:
				if y == x['input']:
					induplicate = True
				if y == x['output']:
					outduplicate = True
				if induplicate == True and outduplicate == True:
					break
			for z in doneNames:
				if z == x['input']:
					induplicate = True
				if z == x['output']:
					outduplicate = True
				if induplicate == True and outduplicate == True:
					break
			if induplicate == False:
				authorNames.append(x['input'])
			if outduplicate == False:
				authorNames.append(x['output'])
			if len(doneNames) + len(authorNames) >= numAuthor:
				break

		if len(doneNames) == numAuthor:
			break

	#closing session before program exits
	authentication.closeSession()

	#duplicate removal needed based on the reference		
	total_list = duplicate_reference(total_list)
	#counting the number of co-citation for the final statistics
	total_list = list_count(total_list)

	authorList=[]
	kcount = 0
	for k in total_list:
		for x in range(0,k['count']):
			authorList.append(unicode(k['input']).encode('utf-8'))
			authorList.append(unicode(k['output']).encode('utf-8'))
		kcount = kcount + k['count']
	
	print "Total Number of Co-citations Recorded: " + str(kcount)
	alc = Counter(authorList)
	alc_sorted = sorted(alc.items(),key=lambda(k,v):(-v,k))

	with open(outputfile2+".csv",'ab') as f:
		writer = UnicodeWriter(f, quoting=csv.QUOTE_NONNUMERIC)
		for key, value in alc_sorted:
			writer.writerow([key.decode('utf-8'),str(value)])

	with open(outputfile1+".csv",'ab') as g:
		writer1 = UnicodeWriter(g, quoting=csv.QUOTE_NONNUMERIC)
		for row in total_list:
			writer1.writerow([row['input'],row['output'],str(row['count'])])
	
if __name__ == "__main__":
	main(sys.argv[1:])
