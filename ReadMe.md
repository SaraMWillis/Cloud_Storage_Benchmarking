# Google Drive Speed Test Scripts

### About

This repository contains all the scripts I have used to test upload/download speeds when transferring files to/from Google Drive.

The tests in this repository all use various Google Drive CLI software packages to transfer dummy files. A transfer can either be completed as an upload or a download. It is designed so that the user can either complete these transfers from their personal computer or on University of Arizona's HPC filexfer node. As a result, these scripts can either be run using python 2 or python 3 (as a result of a personal preference for python3 ((also, (python 2 is being sunsetted)[https://www.python.org/doc/sunset-python-2/,] FYI)), and because the filexfer node has only python 2 installed). 

The transfer programs that have scripts currently available or are soon-to-be available are:
* rclone
* cyberduck
* gdrive

Additional information on this testing can be viewed on an available [Overleaf Document](https://www.overleaf.com/read/cnbzpsmbdbqp) which is currently a work-in-progress.
