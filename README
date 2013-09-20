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

This tool was made so that you have an option to rapidy retrieve files from your Nirvanix account.
The tool also has the ability to stream files from your Nirvanix Account to a Rackspace Cloud Files Container.


Overview
--------

1. The tool Authenticates against the Nirvanix API
2. Stores a Session Token
3. Builds a list of all files in all Containers with a max page view of 500
4. As the tool Cycles through the list of Folders it builds a longer list of all files.
5. Once the list of files is complete, The tool Builds the needed local directory structure.
6. Using the power of multi-processing the tool beings to download objects/stream them.


How to
------

* Download this repo
* You MUST have Python 2.6, or 2.7 installed
* Install the application with the setup file that was included and or use the local script found in the bin directory.

Note: You will need to have your **Nirvanix Application Key**, **Username**, and **Password** Handy as the script requires them as arguments.
Note: If you are wanting to migrate your content from Nirvanix to Rackspace Cloud Files you will need to have a cloud account setup and your **username**, **apikey** and **region** on hand.


Example of Simple Download Command :

.. code-block:: shell

    ntorax --remote-path <nirvanix-remote-path> --appkey <your-appkey> --username <your-username> --password <your-password> --work-dir <place-to-save-files> download



Example of Stream to Rackspace Command :

.. code-block:: shell

    ntorax --remote-path <nirvanix-remote-path> --appkey <your-appkey> --username <your-username> --password <your-password> --work-dir <place-to-save-files> to-rax --os-user <rax-username> --os-apikey <rax-api-key> --os-rax-auth <rax-region> --container <container-to-save-files>


Please see ``ntorax --help`` for more information on all of the available options and arguments.

License
^^^^^^^

Copyright [2013] [Kevin Carter]
License Information :
This software has no warranty, it is provided 'as is'. It is your
responsibility to validate the behavior of the routines and its accuracy
using the code provided. Consult the GNU General Public license for further
details (see GNU General Public License).
http://www.gnu.org/licenses/gpl.html
