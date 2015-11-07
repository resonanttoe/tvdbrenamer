# tvdbrenamer

Simple script that will append the name of a TV show episode to the filename.

The input file must be in the form of

Show - SxxExx -.mp4
(If you work in other file format, change Line 60 in renamer.py)

Includes simple unit tests for known good cases. 

#Dependancies
Requests module.
OS X & Linux

pip install requests

#To Install
Clone repo, Add username and password to Authentication.py (Needs to be fixed/handled better).

#To Run
./renamer.py <PATHTOFILES>

Will run across the entire directory searching anything that ends in -.mp4


