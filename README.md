Creativity Web Project Using Web of Science (under testing)
==========

Creativity Web targets to investigate a network of creative scientists in different areas under the supervision of Dr. Robert M. Bilder and Kendra Knudsen

Before Using the Program
----------
IP address has to be registered to the web of science server and granted access to its premium service, not its lite service
* If your computer is connected to UCLA network or UCLA VPN, it has already been pre-registered
* access can be requested through [web of science](http://wokinfo.com/scientific/info/terms-ws/), but its premium service is not guranteed

SUDS - python library for SOAP
* In order to use SUDS, you need python-setuptools installed (<code>sudo apt-get install python-setuptools</code>)
* Download 0.4GA version from [SUDS](http://fedorahosted.org/suds/)
* <code>cd "directory with downloaded file"</code> (remove quotation mark and replace it with actual name)
* <code>tar -xzvf "file-name.tar.gz"</code> (remove quotation mark and replace it with actual name)
* <code>cd "directory with untarred content"</code> (remove quotation mark and replace it with actual name)
* <code>sudo python setup.py install</code>

BeautifulSoup4 - python library for XML/HTML
* In order to use BeautifulSoup4, <code>apt-get install python-bs4</code>

Peewee - database orm for python
* In order to ues peewee, <code>pip install peewee</code>

How to Use
-----------
Command should look like the following:

1) If you want to update the database and see the current query result
*	<code> ./creativity.py inputAuthor intputFileName outputFileName1 outputFileName2</code>
*	ex) <code> ./creativity.py Bilder,R sampleinputfile output1 output2</code>
*	.csv extension will be automatically added by the program for the outputFileNames

2) If you just want to update the database
*	<code> ./creativity inputAuthor intputFileName</code>
*	ex) <code> ./creativity Bilder,R sampleinputfile</code>

3) To update the number of publication each author has published
*	<code> ./fillup.py

4) To create the output files from database
*	<code> ./sample_data/database.py
*	This prints cocitation information and author information

Input file should look like the below with values changed:
(For your reference, this repository has a sample file)

----------
\#timeSpan Begin

1980-01-01

\#timeSpan End

2013-12-31

\#language

en

\#search limit

2

\#citingArticles limit

5

\#citedReference limit

2

\#number of authors to recursively search for

2

----------

What each line means
* Lines starting with '#' means that it is an explanation to the value below
* You can change the explanation, but do not remove '#' or the line itself
* The lines starting without '#' means that these are values

Format and possible values:
*	timeSpan Begin	= YYYY-MM-DD
*	timeSpan End	= YYYY-MM-DD
*	language 		= values specified in the web of science guide
*	search limit 	= minimum of 1 and maximum of 100
*	citingArticles limit = minimum of 1 and maximum of 100
*	citiedReferences limit = minimum of 1 and maximum of 100
*	number of authors to recursively search for = minimum of 1

Function
----------
* With a given input author, the creativity will output a list of two authors who have been co-cited and the number of unique co-citations they received in the first file.
* The number of co-citation that each author is involved with is returned in the second file
* Users can personalize the co-citation search through input settings file
*    - Number of maximum co-citation from each author
*    - NUmber of authors to recusively search co-citation for
*    - Different edition and collection of Web of Science
*    - Different time frame to choose from
* The output is in csv file, so the output is platform independent and easily readable.
* Query results are saved into a local database allowing for future use of the data
* Local database allows retrieval operations including, but not limited to who the author has cocited with
* fillup fills up the number of publications each author has published in a given time frame.
* database prints the cocitation and author information that is currently stored in the database

Known/Possible Bugs
----------
* (Possible) There have been few irregularity in returned data, so there might be error arising due to a lack of debugging. So if there is an error with certain input data, please report it to me through email or github with the input that you've had the program run with
* (Is this necessary to be fixed?) not all authors are going to have address and email address

Contact
----------
* For bugs or feature requests please create a [creativity github issue](https://github.com/ldkz2524/creativity/issues).
* Contact Dongkeun Lee (ldkz2524@ucla.edu)
