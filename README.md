Creativity Web Project Developement
==========

Creativity Web targets to develop a network of creative scientists in different areas

Requirement
----------
SUDS - python library for SOAP (access to web of science)
	* In order to install SUDS, you need python-setuptools installed,
		sudo apt-get install python-setuptools
	* Download 0.4GA version from [suds](http://fedorahosted.org/suds/)
	* tar -xzvf "file-name.tar.gz" (remove quotation mark and replace it with actual name)
	* cd "directory with untarred content" (remove quotation mark and replace it with actual name)
	* sudo python setup.py install

For ease of use, create a command that will run creativity.py
	* To make this command available to all users:
		sudo ln -s $PWD/creativity.py /usr/local/bin/creativity
	* To make this command available only to current user (if you have ~/bin in your path):
		ln -s $PWD/creativity.py ~/bin/creativity

Temporary
BeautifulSoup
<code>sudo easy_install beautifulsoup4</code>


Goal
----------
Feb 14, 2014 ~
Summary: 
	input one scientist and return 5 scientists that has been co-cited with him in a scientific paper
Steps:
	1. Input one scientist and get one most highly cited work of his
	2. Get 5 works that have cited the above work (the most highly cited works)
	3. Get a most higly cited work that the above work has cited for all 5 works 
		(other than the work from input scientist)
	4. choose one author of the work that has been chosen in for all 5 works.
		(author with highest h-index score)
	5. output 5 authors and their work that previous step chooses


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

Contact
----------
* For bugs or feature requests please create a [creativity github issue](https://github.com/ldkz2524/creativity/issues).
* Contact Dongkeun Lee (ldkz2524@ucla.edu)


