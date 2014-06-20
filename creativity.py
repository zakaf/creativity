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
						symbolicTimeSpan, #symbolic time span to search from
						timeSpan, 	#actual time span to search from (choose symbolic or actual)
						language, 	#queryLanguage
						count_s, 	#max num of work by input to be considered
						count_ca, 	#max num of work that cites work by input to be considered
						count_cr):	#max num of author that is cocited with input to be considered
									# count_** is maximum value, because repetition is usual
	pair_list = []
	location_list = []
	email_list = []
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

	#search is called from query
	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': complete_editions, 'symbolicTimeSpan': symbolicTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': count_s, 'sortField': sortField, 'viewField': None, 'option': [option,],})

	if search_result.recordsFound == 0:
		print "No Search Result for " + authorName
		return pair_list

	#BeautifulSoup is used to retrieve the title of the work from full records text
	searchTitle = BeautifulSoup(search_result.records, "xml")
	title_list1 = deque()

	for t in searchTitle.find_all(type="item"):
		title_list1.append(t.string)

	for x in searchTitle("REC"):
		date_published = datetime.strptime(((x('pub_info'))[0])['sortdate'],"%Y-%m-%d").date()

		for t in x.find_all("name"):
			if (t.find_all("email_addr") != []):
				ename = (t("wos_standard"))[0].string.upper().replace(", ",",")
				eemail = (t("email_addr"))[0].string
				email_list.append({'name': trim_name(ename), 'email': eemail, 'date': date_published})
	
		for t in x.find_all("reprint_contact"):
			if t("wos_standard") != []:
				lname = trim_name((t("wos_standard"))[0].string.upper().replace(", ",","))
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
				if lcity == "" and lstate == "" and lcountry == "":
					continue
				location_list.append({'name': lname, 'city': lcity.upper(), 'state': lstate.upper(), 'country': lcountry.upper(), 'date': date_published})

	#citingAriticles is called from query
	for x in search_result.optionValue[0].value:

		x_title = title_list1.popleft()

		citing_result = query.citingArticles( dbId, x, complete_editions, [timeSpan,], language, { 'firstRecord': fRecord, 'count': count_ca, 'sortField': [sortField,], 'viewField': None, 'option': [option,],})
		
		if citing_result.recordsFound == 0:
			continue

		citingTitle = BeautifulSoup(citing_result.records, "xml")
		title_list2 = deque()

		for t in citingTitle.find_all(type="item"):
			title_list2.append(t.string)
		
		for x in citingTitle("REC"):
			date_published = datetime.strptime(((x('pub_info'))[0])['sortdate'],"%Y-%m-%d").date()
	
			for t in x.find_all("name"):
				if (t.find_all("email_addr") != []):
					ename = (t("wos_standard"))[0].string.upper().replace(", ",",")
					eemail = (t("email_addr"))[0].string
					email_list.append({'name': trim_name(ename), 'email': eemail, 'date': date_published})
		
			for t in x.find_all("reprint_contact"):
				if t("wos_standard") != []:
					lname = trim_name((t("wos_standard"))[0].string.upper().replace(", ",","))
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
					if lcity == "" and lstate == "" and lcountry == "":
						continue
					location_list.append({'name': lname, 'city': lcity.upper(), 'state': lstate.upper(), 'country': lcountry.upper(), 'date': date_published})

		#citedReferences is called from query
		for y in citing_result.optionValue[0].value:
			
			y_title = title_list2.popleft()

			cited_result = query.citedReferences( dbId, y, language, { 'firstRecord': fRecord, 'count': count_cr, 'sortField': [sortField,], 'viewField': None, 'option': None, })
			
			if len(cited_result.references) == 0:
				continue
		
			for z in cited_result.references:
				try:
					author1_trimmed = authorName.upper()
					author2_trimmed = trim_name(z.citedAuthor.upper().replace(", ",","))
					#if inputWork and outputWork is the same, skip
					if cmp(unicode(x_title).encode('utf-8').upper(),z.citedTitle.upper()) == 0:
						continue
					#first author should be alphabetically before the second author
					elif cmp(author1_trimmed, author2_trimmed) < 0:
						pair_list.append({'input': author1_trimmed, 'output': author2_trimmed, 'inputWork':unicode(x_title).encode('utf-8').upper(), 'citingWork':unicode(y_title).encode('utf-8').upper(), 'outputWork':z.citedTitle.upper()})
					elif cmp(author1_trimmed, author2_trimmed) > 0:
						pair_list.append({'output': author1_trimmed, 'input': author2_trimmed, 'outputWork':unicode(x_title).encode('utf-8').upper(), 'citingWork':unicode(y_title).encode('utf-8').upper(), 'inputWork':z.citedTitle.upper()})
				except AttributeError:
					pass

	return (pair_list,location_list,email_list)

#return number of work an author has published
def num_of_work (query, authorName, symbolicTimeSpan, timeSpan, language, count_s, count_ca, count_cr):	
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

	search_result = query.search({ 'databaseId': dbId, 'userQuery': userQuery, 'editions': complete_editions, 'symbolicTimeSpan': symbolicTimeSpan, 'timeSpan': [timeSpan,], 'queryLanguage': language, }, { 'firstRecord': fRecord, 'count': count_s, 'sortField': sortField, 'viewField': None, 'option': [option,],})

	return search_result.recordsFound
	
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
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

def trim_name(name):
	comma_location = name.find(',')
	if comma_location == -1:
		return name
	return name[:(comma_location+2)]
		

#--------------------
#MAIN STARTS HERE
def main(argv):
	authorNames = deque([])
	doneNames = []
	skipCount =0
	sTimeSpan = None
	timeSpan = { 'begin':'1980-01-01', 'end':'2013-12-31', }
	language = 'en'
	count_search = 2
	count_ca = 5
	count_cr = 2
	numAuthor = 1
	total_list = []
	total_location_list = []
	total_email_list = []
	searched_author = []
	
	if len(argv) < 2:
		print "Sample Usage: creativity inputAuthor inputSettingFileName ?outputFileName1 ?outputFileName2"
		sys.exit(2)
	
	authorNames.append(argv[0])
	inputfile =  argv[1]
	if len(argv) >= 3:
		outputfile1 = argv[2]
	else:
		outputfile1 = ""
	if len(argv) >= 4:
		outputfile2 = argv[3]
	else:
		outputfile2 = ""

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
				timeSpan['begin'] = line.rstrip('\n')
			elif skipCount == 2:
				timeSpan['end'] = line.rstrip('\n')
			elif skipCount == 3:
				language = line.rstrip('\n')
			elif skipCount == 4:
				count_search = line.rstrip('\n')
			elif skipCount == 5:
				count_ca = line.rstrip('\n')
			elif skipCount == 6:
				count_cr = line.rstrip('\n')
			elif skipCount == 7:
				numAuthor = int(line.rstrip('\n'))
			else:
				break

	#instance of Authenticate created and authenticateSession is called
	authentication = Authenticate()
	authentication.authenticateSession()
	
	while True:	
		authorName = authorNames.popleft()
		searched_author.append(authorName)

		#instance of Query created
		query = Query(authentication.SID)
		
		#explanation of arguments are done in the actual function itself
		pair_list,location_list,email_list = cocitation_with(query, authorName, sTimeSpan, timeSpan, language, count_search, count_ca, count_cr)
		
		#complete list of co-citation and location
		total_list = total_list + pair_list
		total_location_list = total_location_list + location_list
		total_email_list = total_email_list + email_list

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


	t0 = time.time()

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

	if outputfile2 != "":
		with open(outputfile2+".csv",'ab') as f:
			writer = UnicodeWriter(f, quoting=csv.QUOTE_NONNUMERIC)
			for key, value in alc_sorted:
				writer.writerow([key.decode('utf-8'),str(value)])

	if outputfile1 != "":
		with open(outputfile1+".csv",'ab') as g:
			writer1 = UnicodeWriter(g, quoting=csv.QUOTE_NONNUMERIC)
			for row in total_list:
				writer1.writerow([row['input'],row['output'],str(row['count'])])

	t1 = time.time()

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
	for x in total_list:
		#store author information
		try:
			Author.get(Author.name==x['input'])
		except Author.DoesNotExist:
			Author.create(name=x['input'], num_of_work=num_of_work(query, x['input'], sTimeSpan, timeSpan, language, count_search, count_ca, count_cr))
		try:
			Author.get(Author.name==x['output'])
		except Author.DoesNotExist:
			Author.create(name=x['output'], num_of_work=num_of_work(query, x['output'], sTimeSpan, timeSpan, language, count_search, count_ca, count_cr))
		#store work information
		for y in x['reference']:
			try:
				Work.get(Work.title==y['inputWork'])
			except Work.DoesNotExist:
				Work.create(title=y['inputWork'])
			try:
				Work.get(Work.title==y['citingWork'])
			except Work.DoesNotExist:
				Work.create(title=y['citingWork'])
			try:
				Work.get(Work.title==y['outputWork'])
			except Work.DoesNotExist:
				Work.create(title=y['outputWork'])

			#store author-work information 
			#i was trying to retreive author/work item using get() in the creation part, but a lot of errors are rising, so i'm using get again here
			#i think it has to do with local variable scope, but assigning local variables outside of try/except still causes error, but different one.
			#if large database causes a great time delay with such duplicate get, i will try to debug it.
			try:
				AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['input']), AuthorWork.work==Work.get(Work.title==y['inputWork']))
			except AuthorWork.DoesNotExist:
				AuthorWork.create(author=Author.get(Author.name==x['input']), work=Work.get(Work.title==y['inputWork']))
			try:
				AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['output']), AuthorWork.work==Work.get(Work.title==y['outputWork']))
			except AuthorWork.DoesNotExist:
				AuthorWork.create(author=Author.get(Author.name==x['output']), work=Work.get(Work.title==y['outputWork']))

			#store cocitation information
			try:
				Cocitation.get(	Cocitation.inputRelationship==AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['input']), AuthorWork.work==Work.get(Work.title==y['inputWork'])), Cocitation.citingWork==Work.get(Work.title==y['citingWork']), Cocitation.citedRelationship==AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['output']), AuthorWork.work==Work.get(Work.title==y['outputWork'])))
			except Cocitation.DoesNotExist:
				Cocitation.create(	inputRelationship=AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['input']), AuthorWork.work==Work.get(Work.title==y['inputWork'])), citingWork=Work.get(Work.title==y['citingWork']), citedRelationship=AuthorWork.get(AuthorWork.author==Author.get(Author.name==x['output']), AuthorWork.work==Work.get(Work.title==y['outputWork'])))
	
	for x in total_location_list:
		try:
			Address.get(Address.author==Author.get(Author.name==x['name']), Address.city==x['city'], Address.state==x['state'], Address.country==x['country'], Address.date==x['date'])
		except Address.DoesNotExist:
			Address.create(author=Author.get(Author.name==x['name']), city=x['city'], state=x['state'], country=x['country'], date=x['date'])
		except Author.DoesNotExist:
			curr_author = Author.create(name=x['name'], num_of_work=num_of_work(query, x['name'], sTimeSpan, timeSpan, language, count_search, count_ca, count_cr))
			Address.create(author=curr_author, city=x['city'], state=x['state'], country=x['country'], date=x['date'])
	
	for x in total_email_list:
		try:
			Email.get(Email.author==Author.get(Author.name==x['name']), Email.email==x['email'], Email.date==x['date'])
		except Email.DoesNotExist:
			Email.create(author=Author.get(Author.name==x['name']), email=x['email'], date=x['date'])
		except Author.DoesNotExist:
			curr_author = Author.create(name=x['name'], num_of_work=num_of_work(query, x['name'], sTimeSpan, timeSpan, language, count_search, count_ca, count_cr))
			Email.create(author=curr_author, email=x['email'], date=x['date'])

	for x in searched_author:
		try:
			Queries.get(Queries.author == x, Queries.start == datetime.strptime(timeSpan['begin'],"%Y-%m-%d").date(), Queries.end == datetime.strptime(timeSpan['end'],"%Y-%m-%d").date(), Queries.num_of_search == count_search, Queries.num_of_citing == count_ca, Queries.num_of_cited == count_cr)
		except Queries.DoesNotExist:
			Queries.create(author = x, start = datetime.strptime(timeSpan['begin'],"%Y-%m-%d").date(), end = datetime.strptime(timeSpan['end'],"%Y-%m-%d").date(), num_of_search = count_search, num_of_citing = count_ca, num_of_cited = count_cr)
			

	#instance of Authenticate created and authenticateSession is called
	authentication = Authenticate()
			
			
	#database connection closed
	database.close()

	#closing session before program exits
	authentication.closeSession()

	t2 = time.time()
	# measures time for performance measure
	print "---------TIME----------"
	print "Calculation time"
	print t1-t0
	print "Database time (Including number of work query search time)"
	print t2-t1
	
if __name__ == "__main__":
	main(sys.argv[1:])
