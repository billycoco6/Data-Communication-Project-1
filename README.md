# Data-Communication-Project-1
Possathorn Wittayaprechapol
5680353

Library Utilization
------------------------------
sys, socket, os, asyncore, urlparse

General Usage Note
------------------------------
  - Downloading with single connection
  1.  Downloadble
  2.  Resumable
  3.  Able to check the current version of the downloaded file
  4.  Error handling
  
  - Donwloading with multiple connection
  1. Downloadable
  2. Able to check the current version of the downloaded file
  3. Error handling

Features Supported
------------------------------
  1. Downloading file with/ without content length
  2. Downloading file with/ without Etags or Date-Last-Modified
  3. URL redirection

Input format: ./srget -o <output file> [-c [<numConn>]] http://someurl.domain[:port]/path/to/file

Sample input: ./srget -o "test.jpg" -c 1 images.clipartpanda.com/lion-clipart-4Tb5XEETg.png

notes: not support https://

========================================================================================================================
