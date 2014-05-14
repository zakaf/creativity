Creativity Web Project Using Web of Science (under development)
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

For ease of use, create a command, "creativity", that will run creativity.py
* To make this command available to all users:

    <code>sudo ln -s $PWD/creativity.py /usr/local/bin/creativity</code>

* To make this command available only to current user (if you have ~/bin in your path):

    <code>ln -s $PWD/creativity.py ~/bin/creativity</code>

How to Use
-----------
Command should look like the following:

1) If you want to update the database and see the current query result
*	<code> creativity inputAuthor intputFileName outputFileName1 outputFileName2</code>
*	ex) <code> creativity Bilder,R sampleinputfile output1 output2</code>
*	.csv extension will be automatically added by the program for the outputFileNames

2) If you just want to update the database
*	<code> creativity inputAuthor intputFileName</code>
*	ex) <code> creativity Bilder,R sampleinputfile</code>

Input file should look like the below with values changed:
(For your reference, this repository has a sample file)

----------
\#databaseId:

WOS

\#editions:

SCI

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
*	databaseId 		= values specified in the web of science guide
*	editions 		= values specified in the web of science guide
*	timeSpan Begin	= YYYY-MM-DD
*	timeSpan End	= YYYY-MM-DD
*	language 		= values specified in the web of science guide
*	search limit 	= minimum of 1 and maximum of 100
*	citingArticles limit = minimum of 1 and maximum of 100
*	citiedReferences limit = minimum of 1 and maximum of 100
*	number of authors to recursively search for = minimum of 1

Function
----------
* With a given input author, the program will output a list of two authors who have been co-cited and the number of unique co-citations they received in the first file.
* Users can personalize the co-citation search through input settings file
*    - Number of maximum co-citation from each author
*    - NUmber of authors to recusively search co-citation for
*    - Different edition and collection of Web of Science
*    - Different time frame to choose from
* All duplicates are removed from the output, so only unique co-citations are considered
* The number of co-citation that each author is involved with is returned in the second file
* The output is in csv file, so the output is platform independent and easily readable.
* Query results are saved into a local database allowing for future use of the data

Progress
----------
Feb 14, 2014
* SOAP library called, 'SUDS' is used
* Started to use web of science api using soap approach
* Got authentication and closeSession to work

Feb 18, 2014
* Attached session id to the header of search request
* Input parameters for search request has been made
* search request can now be made, but response has to be formatted
* First search returns the single work with the most number of citations (currently author hardcoded as Chomczynski, P)
* citingArticels receive input from previous search result and returns 5 works that cited the work returned by previous function
* made code cleaner and more objected-oriented like by creating 'Authenticate' and 'Query' class.
* as of now, program prints session id, most highly cited work of Chomczynski, P, 5 most highly cited works that cites the previous work of Chomczynski, P

Feb 19, 2014
* co-cited authors can be returned
* input author can be returned, so i've removed tuples with same input and output author
* different arguments for cocitation with function have been documented
* program will output co-cited authors with input author
* Feb 14, 2014 ~ Feb 19, 2014 GOAL DONE

Feb 25, 2014
* now input author is not hard coded and accepts it as an arugment
* settings is not hard coded and the file name of the settings file is accepted as an argument
* the sample settings file is described above as well as how command should look like
Feb 25, 2014 GOAL DONE

March 30, 2014
* Possible Graphical Representation library is being reviewed.
* Error caused by a return with unknown citedAuthor is fixed 
* Repeated co-citation is now removed, instead the output now shows the count of the same co-citation next to the input and the output author

March 31, 2014
* The return will be sorted by the number of co-citation (high to low) then the alphabetical order.
* The program saves an information about how two authors are related (which works of them and others make them co-cited)
* The return is saved into a csv file

April 3, 2014
* Recursive author co-citation search has been implemented
* There is a need for the program to remove duplicate and co-citation from the same paper
* Removing co-citation from the same paper has been implemented, but not fully debugged due to internet disconnection
* After reference duplicate removal is implemented, there is a need for large sample debugging

April 4, 2014 ~ April 5, 2014
* Reference duplicate (two or more same co-citation getting counted more than once) is now removed, when counting co-citation.
* Program functionality is somewhat complete, but details have to be checked out.
* Number of co-citation that each author is involved with is printed out in the second file

April 6, 2014
* All the csv output is in UTF-8 to prevent any error rising from unicode to ascii conversion. (due to authors with their name written in their native language, not in english alphabet)

May 12, 2014
* Location data is collected from Web of Science and they are saved to a list
* Database implementation has started

May 13, 2014
* Everything is correctly imported into sqlite database from query (author, work, authorWork, Cocitation, Address)
* tables are relatively simple, but storing more information is a piece of cake

Known/Possible Bugs
----------
* (temporaily fixed, needs testing) When the request is blocked, becuase the program have requested too many queries within certain time frame, error returned by the server is not getting caught by try-except. It just says WebFault not defined. (request is only blocked for at most 5 minutes, so try after 5 mins and you will be fine)
* (Possible) There have been few irregularity in returned data, so there might be error arising due to a lack of debugging. So if there is an error with certain input data, please report it to me through email or github with the input that you've had the program run with
* (Possible) There might be problem, when reading irregular input, so please follow the instruction with input file
* (has to be considered) web of science has multiple notations of the name. ex) Bilder,R & Bilder,Robert & Bilder,RM. However, it is unable to detect that these names refer to the same person.

Future Goal
----------
* database query using previosuly saved data

Contact
----------
* For bugs or feature requests please create a [creativity github issue](https://github.com/ldkz2524/creativity/issues).
* Contact Dongkeun Lee (ldkz2524@ucla.edu)


