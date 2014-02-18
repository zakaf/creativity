Creativity Web Project Developement
==========

Creativity Web targets to develop a network of creative scientists in different areas

Requirement
----------
SUDS - python library for SOAP (access to web of science)


Goal
----------
Feb 14, 2014
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
SOAP library called, 'SUDS' is used

Contact
----------
* For bugs or feature requests please create a [creativity github issue](https://github.com/ldkz2524/creativity/issues)/


