Nirvanix Downloader
###################
:date: 2013-09-18 09:51
:tags: Nirvanix, Download, Local, Cloud Storage, Rackspace, Cloud Files
:category: \*nix

Download Objects from your Nirvanix Account
===========================================

General Overview
----------------

This is a VERY Simple tool that will download files from your Nirvanix Account to your local System.

The tool was created in haste as Nirvanix seems to no longer want to do business. As such this tool has been created to allow you, the end user to download your data onto some local system.

Additionally I am going to build this tool such that it will allow you to upload all your objects from Nrivanix to Rackspace Cloud Files.

Stay tuned, check back regularly for updates.


Overview
--------

1. The tool Authenticates against the Nirvanix API
2. Stores a Session Token
3. Builds a list of all files in all Containers with a max page view of 500
4. As the tool Cycles through the list of Folders it builds a longer list of all files.
5. Once the list of files is complete, The tool Builds the needed local directory structure.
6. Using the power of multi-processing the tool beings to download objects.


How to
------

* Download this repo
* You MUST have Python 2.6, or 2.7 installed
* Make the script executable ``chmod +x nirvanix-downloader.py``
* Run Script.

Note: You will need to have your **Nirvanix Application Key**, **Username**, and **Password** Handy as the script requires them as arguments.


License
^^^^^^^

Copyright [2013] [Kevin Carter]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.