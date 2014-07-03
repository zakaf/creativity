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

from peewee import *
import time

#db = SqliteDatabase('biology/biology_database.db')
#db = SqliteDatabase('chemistry/chemistry_database.db')
#db = SqliteDatabase('engineering/engineering_database.db')
#db = SqliteDatabase('economics/economics_database.db')
#db = SqliteDatabase('medicine/medicine_database.db')
db = SqliteDatabase('social/social_database.db')

db2 = SqliteDatabase('merged_database.db')

#model defintion of database
class BaseModel(Model):
	class Meta:
		database = db

class BaseModel2(Model):
	class Meta:
		database = db2

class Author(BaseModel):
	name = CharField()
	num_of_work = IntegerField(default=0)

class Author2(BaseModel2):
	name = CharField()
	num_of_work = IntegerField(default=0)

class Email(BaseModel):
	author = ForeignKeyField(Author, related_name='authorEmail')
	email = CharField()
	date = DateField()
	
class Email2(BaseModel2):
	author = ForeignKeyField(Author2, related_name='authorEmail2')
	email = CharField()
	date = DateField()

class Work(BaseModel):
	title = CharField()

class Work2(BaseModel2):
	title = CharField()

class AuthorWork(BaseModel):
	author = ForeignKeyField(Author, related_name='authorWork')
	work = ForeignKeyField(Work, related_name='authorWork')

class AuthorWork2(BaseModel2):
	author = ForeignKeyField(Author2, related_name='authorWork2')
	work = ForeignKeyField(Work2, related_name='authorWork2')

class Address(BaseModel):
	author = ForeignKeyField(Author, related_name='authorAddress')
	city = CharField()
	state = CharField()
	country = CharField()
	date = DateField()

class Address2(BaseModel2):
	author = ForeignKeyField(Author2, related_name='authorAddress2')
	city = CharField()
	state = CharField()
	country = CharField()
	date = DateField()

class Cocitation(BaseModel):
	inputRelationship = ForeignKeyField(AuthorWork, related_name='inputRelationship')
	citingWork = ForeignKeyField(Work, related_name='citingWork')
	citedRelationship = ForeignKeyField(AuthorWork, related_name='citedRelationship')

class Cocitation2(BaseModel2):
	inputRelationship = ForeignKeyField(AuthorWork2, related_name='inputRelationship2')
	citingWork = ForeignKeyField(Work2, related_name='citingWork2')
	citedRelationship = ForeignKeyField(AuthorWork2, related_name='citedRelationship2')

class Queries(BaseModel):
	author = CharField()
	start = DateField()
	end = DateField()
	num_of_search = IntegerField()
	num_of_citing = IntegerField()
	num_of_cited = IntegerField()

class Queries2(BaseModel2):
	author = CharField()
	start = DateField()
	end = DateField()
	num_of_search = IntegerField()
	num_of_citing = IntegerField()
	num_of_cited = IntegerField()

#--------------------
#MAIN STARTS HERE
def main():

	#database connection
	db.connect()
	db2.connect()

	#create required tables if it doesn't exist
	Author2.create_table(fail_silently=True)
	Email2.create_table(fail_silently=True)
	Work2.create_table(fail_silently=True)
	AuthorWork2.create_table(fail_silently=True)
	Address2.create_table(fail_silently=True)
	Cocitation2.create_table(fail_silently=True)
	Queries2.create_table(fail_silently=True)

	t0 = time.time()
	for x in Author.select():
		if Author2.select().where(Author2.name==x.name).exists() == False:
			Author2.create(name=x.name,num_of_work=x.num_of_work)
	print "Author",time.time()-t0,Author.select().count(),Author2.select().count()

	t1 = time.time()
	for x in Email.select():
		try:
			past_author = Author.get(Author.id == x.author.id)
			curr_author = Author2.get(Author2.name==past_author.name)
			if Email2.select().where(Email2.author==curr_author,Email2.email==x.email,Email2.date==x.date).exists() == False:
				Email2.create(author=curr_author,email=x.email,date=x.date)
		except Author.DoesNotExist:
			continue
	print "Email",time.time()-t1,Email.select().count(),Email2.select().count()

	t2 = time.time()
	for x in Address.select():
		try:
			past_author = Author.get(Author.id == x.author.id)
			curr_author = Author2.get(Author2.name==past_author.name)
			if Address2.select().where(Address2.author==curr_author,Address2.city==x.city,Address2.state==x.state,Address2.country==x.country,Address2.date==x.date).exists() == False:
				Address2.create(author=curr_author,city=x.city,state=x.state,country=x.country,date=x.date)
		except Author.DoesNotExist:
			continue
	print "Address",time.time()-t2,Address.select().count(),Address2.select().count()

	t3 = time.time()
	for x in Work.select():
		if Work2.select().where(Work2.title==x.title).exists() == False:
			Work2.create(title=x.title)
	print "Work",time.time()-t3,Work.select().count(),Work2.select().count()

	t4 = time.time()
	for x in AuthorWork.select():
		try:
			past_author = Author.get(Author.id == x.author.id)
			curr_author = Author2.get(Author2.name==past_author.name)
			past_work = Work.get(Work.id == x.work.id)
			curr_work = Work2.get(Work2.title==past_work.title)
			if AuthorWork2.select().where(AuthorWork2.author==curr_author,AuthorWork2.work==curr_work).exists() == False:
				AuthorWork2.create(author=curr_author,work=curr_work)
		except Author.DoesNotExist:
			continue
	print "AuthorWork",time.time()-t4,AuthorWork.select().count(),AuthorWork2.select().count()

	t5 = time.time()
	for x in Cocitation.select():
		inputR = AuthorWork.get(AuthorWork.id == x.inputRelationship.id)
		past_author1 = Author.get(Author.id == inputR.author.id)
		curr_author1 = Author2.get(Author2.name==past_author1.name)
		past_work1 = Work.get(Work.id == inputR.work.id)
		curr_work1 = Work2.get(Work2.title==past_work1.title)
		inputR_new = AuthorWork2.get(AuthorWork2.author == curr_author1, AuthorWork2.work == curr_work1)
		
		citingW_new = Work2.get(Work2.id == x.citingWork)
		
		outputR = AuthorWork.get(AuthorWork.id == x.citedRelationship.id)
		past_author2 = Author.get(Author.id == outputR.author.id)
		curr_author2 = Author2.get(Author2.name==past_author2.name)
		past_work2 = Work.get(Work.id == outputR.work.id)
		curr_work2 = Work2.get(Work2.title==past_work2.title)
		outputR_new = AuthorWork2.get(AuthorWork2.author == curr_author2, AuthorWork2.work == curr_work2)

		if Cocitation2.select().where(Cocitation2.inputRelationship == inputR_new, Cocitation2.citingWork == citingW_new, Cocitation2.citedRelationship == outputR_new).exists() == False:
			Cocitation2.create(inputRelationship = inputR_new, citingWork = citingW_new, citedRelationship = outputR_new)
	print "Cocitation",time.time()-t5,Cocitation.select().count(),Cocitation2.select().count()

	t6 = time.time()
	for x in Queries.select():
		if Queries2.select().where(Queries2.author==x.author,Queries2.start==x.start,Queries2.end==x.end,Queries2.num_of_search==x.num_of_search,Queries2.num_of_citing==x.num_of_citing,Queries2.num_of_cited==x.num_of_cited).exists() == False:
			Queries2.create(author=x.author,start=x.start,end=x.end,num_of_search=x.num_of_search,num_of_citing=x.num_of_citing,num_of_cited=x.num_of_cited)
			
	print "Queries",time.time()-t6,Queries.select().count(),Queries2.select().count()

	#database connection closed
	db.close()
	db2.close()

if __name__ == "__main__":
	main()
