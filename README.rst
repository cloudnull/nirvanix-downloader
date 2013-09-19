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

Presently the tool is Serial, this means that the downloads could take a long time as they all have to be process ONE AT A TIME. However, soon I hope to have a multiprocessing downloader available.

Additionally I am going to build this tool such that it will allow you to upload all your objects from Nrivanix to Rackspace Cloud Files.

Stay tuned, check back regularly for updates.


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