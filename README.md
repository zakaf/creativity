Creativity Web Project (under development)
==========

Creativity Web targets to develop a network of creative scientists in different areas

Requirement
----------
IP address has to be registered at the web of science server and granted accessed to their premium service, not lite service
* server will not grant an authentication, if not registered
* If your computer is connrected to UCLA network or UCLA VPN, it has already been pre-registered

SUDS - python library for SOAP
* In order to use SUDS, you need python-setuptools installed (<code>sudo apt-get install python-setuptools</code>)
* Download 0.4GA version from [SUDS](http://fedorahosted.org/suds/)
* <code>cd "directory with downloaded file"</code> (remove quotation mark and replace it with actual name)
* <code>tar -xzvf "file-name.tar.gz"</code> (remove quotation mark and replace it with actual name)
* <code>cd "directory with untarred content"</code> (remove quotation mark and replace it with actual name)
* <code>sudo python setup.py install</code>

For ease of use, create a command that will run creativity.py
* To make this command available to all users:

    <code>sudo ln -s $PWD/creativity.py /usr/local/bin/creativity</code>
* To make this command available only to current user (if you have ~/bin in your path):

    <code>ln -s $PWD/creativity.py ~/bin/creativity</code>

Goal
----------
Feb 14, 2014 ~ Feb 19, 2014

Summary: 
* input one scientist and return 5 scientists that has been co-cited with him in a scientific paper

Steps:
* Input one scientist and get one most highly cited work of his
* Get 5 works that have cited the above work (the most highly cited works)
* Get a most higly cited work that the above work has cited for all 5 works (other than the work from input scientist)
* choose one author of the work that has been chosen in for all 5 works.(author with highest h-index score)
* output 5 authors and their work that previous step chooses


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
* different arguments for cocitation_with function have been documented
* program will output co-cited authors with input author
* Feb 14, 2014 ~ Feb 19, 2014 GOAL DONE

Known/Possible Bugs
----------
* (temporaily fixed, needs testing) When the request is blocked, becuase the program have requested too many queries within certain time frame, error returned by the server is not getting caught by try-except. It just says WebFault not defined. (request is only blocked for at most 5 minutes, so try after 5 mins and you will be fine)
* (Possible) There have been few irregularity in returned data, so there might be error arising due to lack of debugging. Therefore if there is an error with certain input data, please report it to me through email or github with the input that you've had the program run with

Issues
----------
* Every query request automatically pauses 0.5 seconds before requesting result from server (2 queries per second limit set by server) (program takes care of this)
* User should run this program maximum of 5 times in 5 minutes period. (5 authentication requests per 5 minutes limit set by server) (user have to take care of this, but the worst thing that can happen is error popping up and user waiting for 5 minutes or until the time shown in the error)


Contact
----------
* For bugs or feature requests please create a [creativity github issue](https://github.com/ldkz2524/creativity/issues).
* Contact Dongkeun Lee (ldkz2524@ucla.edu)


