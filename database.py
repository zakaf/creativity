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

DATABASE = 'database_creativity.db'
database = SqliteDatabase(DATABASE)
#model defintion of database
class BaseModel(Model):
	class Meta:
		database = database

class Author(BaseModel):
	name = CharField()

	def cocitation_with(self):
		AW1 = AuthorWork.alias()
		AW2 = AuthorWork.alias()
		return Cocitation.select().join(AW1, on=(Cocitation.inputRelationship == AW1.id)).switch(Cocitation).join(AW2,on=(Cocitation.citedRelationship == AW2.id)).where((AW2.author == self) | (AW1.author == self))

	def count_cocitation_with(self):
		AW1 = AuthorWork.alias()
		AW2 = AuthorWork.alias()
		return Cocitation.select().join(AW1, on=(Cocitation.inputRelationship == AW1.id)).switch(Cocitation).join(AW2,on=(Cocitation.citedRelationship == AW2.id)).where((AW2.author == self) | (AW1.author == self)).count()

	def cocitation_together(self,second):
		AW1 = AuthorWork.alias()
		AW2 = AuthorWork.alias()
		return Cocitation.select().join(AW1, on=(Cocitation.inputRelationship == AW1.id)).switch(Cocitation).join(AW2,on=(Cocitation.citedRelationship == AW2.id)).where(((AW2.author == self) & (AW1.author == second)) | ((AW2.author == second) & (AW1.author == self)))
	
	def count_cocitation_together(self,second):
		AW1 = AuthorWork.alias()
		AW2 = AuthorWork.alias()
		return Cocitation.select().join(AW1, on=(Cocitation.inputRelationship == AW1.id)).switch(Cocitation).join(AW2,on=(Cocitation.citedRelationship == AW2.id)).where(((AW2.author == self) & (AW1.author == second)) | ((AW2.author == second) & (AW1.author == self))).count()
		
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
	zipcode = CharField()

class Cocitation(BaseModel):
	inputRelationship = ForeignKeyField(AuthorWork, related_name='inputRelationship')
	citingWork = ForeignKeyField(Work, related_name='citingWork')
	citedRelationship = ForeignKeyField(AuthorWork, related_name='citedRelationship')

#--------------------
#MAIN STARTS HERE
def main():

	t0 = time.time()
	#database connection
	database.connect()

	#create required tables if it doesn't exist
	Author.create_table(fail_silently=True)
	Work.create_table(fail_silently=True)
	AuthorWork.create_table(fail_silently=True)
	Address.create_table(fail_silently=True)
	Cocitation.create_table(fail_silently=True)
	
#	for x in Author.select():
#		print x.name
#	for x in Work.select():
#		print x.title
#	for x in AuthorWork.select():
#		print x.author.name,x.work.title
#	for x in Cocitation.select():
#		print x.inputRelationship.author.name,x.citingWork.title,x.citedRelationship.author.name
#	for x in Address.select():
#		print x.author.name,x.city,x.state,x.country,x.zipcode
	print "-------------------------"
	for x in Author.get(Author.name == "KAY,SR").cocitation_with():
		print x.inputRelationship.author.name, x.citedRelationship.author.name
	print Author.get(Author.name == "KAY,SR").count_cocitation_with()
	for x in Author.get(Author.name == "KAY,SR").cocitation_together(Author.get(Author.name == "KANE,J")):
		print x.inputRelationship.author.name, x.citedRelationship.author.name
	print Author.get(Author.name == "KAY,SR").count_cocitation_together(Author.get(Author.name == "KANE,J"))

	#database connection closed
	database.close()
	
	t1 = time.time()
	print "---------TIME----------"
	print "Calculation time"
	print t1-t0

if __name__ == "__main__":
	main()
