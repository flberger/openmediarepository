"""OpenMediaRepository - a web based open media repository framework.

   Copyright (c) 2015 Florian Berger <florian.berger@posteo.de>


   ## Basic Data Structures

   The basic data structures are the Repository and the Accounts.

   >>> import openmediarepository as omr
   >>> r = omr.Repository()
   >>> a = omr.Accounts()
   >>>


   ## Items

   Media repository items are key-value storages with a mandatory set
   of keys. They can either be represented by a dict or by an object
   who responds accordingly to attribute queries.

   The identifier of an item is the hex digest of the Whirlpool hash
   of its content.

   >>> import hashlib
   >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 1 --></svg>", encoding = "utf8"))
   >>> test_item_1 = {"identifier" : hash.hexdigest()}
   >>> class TestItem:
   ...     pass
   >>> test_item_2 = TestItem()
   >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 2 --></svg>", encoding = "utf8"))
   >>> test_item_2.identifier = hash.hexdigest()

   For convenience, there is an item class.

   >>> import io
   >>> test_item_3 = omr.Item(io.BytesIO(bytes("<svg><!-- Test 3 --></svg>", encoding = "utf8")))


   ## Repository API

   >>> r.add(test_item_1)
   >>> r.add(test_item_2)
   >>> r.add(test_item_3)

   Invalid items will be rejected.

   >>> r.add({"not" : "valid"})
   Traceback (most recent call last):
   ...
   RuntimeError: Can not add invalid item to repository: '{'not': 'valid'}'

   Repository.items allows for listing and enumerating items.

   >>> l = list(r.items.keys())
   >>> l.sort()

   Let's display the identifiers shortened, for reading convenience.

   >>> [identifier[:8] for identifier in l]
   ['6f847d12', '9d71ca42', 'aac73176']


   ## Accounts API

   Accounts are represented by an email address.

   >>> a.add("alice@some.domain")
   >>> a.add('"Bob" <bob@some.domain>')
   >>> a.add('Eve <eve@some.domain>')

   The email address serves as an unique identifier.
   Duplicates will be rejected.

   >>> a.add("bob@some.domain")
   Traceback (most recent call last):
   ...
   ValueError: Address already exists: 'bob@some.domain'

   Adresses and possible names are available in the Accounts.accounts
   dict.

   >>> emails = list(a.accounts.keys())
   >>> emails.sort()
   >>> ["<{0}>: '{1}'".format(email, a.accounts[email]) for email in emails]
   ["<alice@some.domain>: ''", "<bob@some.domain>: 'Bob'", "<eve@some.domain>: 'Eve'"]

   Accounts can be dumped for later reconstruction.

   >>> a.dump()
   >>> a = omr.Accounts()
   >>> list(a.accounts.keys())
   []
   >>> a.load()
   >>> emails = list(a.accounts.keys())
   >>> emails.sort()
   >>> ["<{0}>: '{1}'".format(email, a.accounts[email]) for email in emails]
   ["<alice@some.domain>: ''", "<bob@some.domain>: 'Bob'", "<eve@some.domain>: 'Eve'"]
"""

# This file is part of OpenMediaRepository.
#
# OpenMediaRepository is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenMediaRepository is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenMediaRepository.  If not, see <http://www.gnu.org/licenses/>.

# Work started on 31. Dec 2015.

import logging
import hashlib
import cherrypy

VERSION = "0.1.0"

LOGGER = logging.getLogger("OpenMediaRepository")
LOGGER.setLevel(logging.DEBUG)
STDERR_FORMATTER = logging.Formatter("OpenMediaRepository [{levelname}] {funcName}(): {message} (l.{lineno})", style = "{")
STDERR_HANDLER = logging.StreamHandler()
STDERR_HANDLER.setFormatter(STDERR_FORMATTER)
LOGGER.addHandler(STDERR_HANDLER)

PORT = 8000
THREADS = 10
AUTORELOAD = False

class Item:
    """Convenience class, representing a repository item.
    """

    def __init__(self, fp):
        """Initialise.
           fp is a binary mode filepointer pointing to the media file
           to be represented.
        """

        self.identifier = hashlib.new("whirlpool", fp.read()).hexdigest()

        return
        
class Repository:
    """Represent media items, and provide access.

       Attributes:

       Repository.items
           A dict, mapping Whirlpool hex digest strings to Item instances
           or an equivalent dict.
    """

    def __init__(self):
        """Initialise.
        """

        self.items = {}

        return

    def add(self, item):
        """Add an item to the repository.
           item is either a dictionary or returns fitting values
           on __getattr__() calls.
        """

        try:
            self.items[item["identifier"]] = item
            
        except:

            # May be TypeError, KeyError, ...
            
            try:
                self.items[item.identifier] = item
                
            except AttributeError:
                
                raise RuntimeError("Can not add invalid item to repository: '{0}'".format(repr(item)))

        return

class Accounts:
    """Represent accounts, and provide access.

       Attributes:

       Accounts.accounts
           A dict, mapping email addresses to strings with names,
           or empty strings if no name is given.
    """

    def __init__(self):
        """Initialise.
        """

        self.accounts = {}

        return

    def add(self, email):
        """Add the email address as an account.
           email can be a plain email address, or a string '"Firstname Lastname" <email@address>'.
        """

        email = email.strip()

        # Default: treating as plain email address

        email_part = email

        name_part = ""

        if email.find("<") > -1:

            name_part, email_part = email.split(sep = "<", maxsplit = 1)

            email_part = email_part.strip(">")

            name_part = name_part.strip().strip('"')

        if email_part in self.accounts.keys():

            raise ValueError("Address already exists: '{0}'".format(email_part))

        self.accounts[email_part] = name_part

        return

    def dump(self):
        """Serialise current data to storage.
           The default implementation writes the data to a plain text file in CWD.
        """

        with open("accounts.txt", "wt", encoding = "utf8") as fp:

            for email_part in self.accounts.keys():

                fp.write('"{0}" <{1}>\n'.format(self.accounts[email_part], email_part))

        return

    def load(self):
        """Read account data from storage.
           The default implementation reads the data from a plain text file in CWD,
           using Accounts.add() for parsing.
        """

        with open("accounts.txt", "rt", encoding = "utf8") as fp:

            for line in fp.readlines():

                self.add(line)

        return

class WebApp:
    """Web application main class, suitable as cherrypy root.
    """

    def __init__(self):
        """Initialise WebApp.
        """

        # Make self.__call__ visible to cherrypy
        #
        self.exposed = True

        return

    def __call__(self):
        """Called by cherrypy for the / root page.
        """

        return '<html><head><title>Hello World</title></head><body><h1>Hello World</h1><p><a href="/subpage">Go to subpage</a></p></body></html>'

    def subpage(self):

        return '<html><head><title>Hello World Subpage</title></head><body><h1>Hello World Subpage</h1><p><a href="/">Go to main page</a></p></body></html>'

    subpage.exposed = True

def main():
    """Main function, for IDE convenience.
    """

    root = WebApp()

    config_dict = {"/" : {"tools.sessions.on" : True,
                          "tools.sessions.timeout" : 60},
                   "global" : {"server.socket_host" : "0.0.0.0",
                               "server.socket_port" : PORT,
                               "server.thread_pool" : THREADS}}

    # Conditionally turn off Autoreloader
    #
    if not AUTORELOAD:

        cherrypy.engine.autoreload.unsubscribe()

    cherrypy.quickstart(root, config = config_dict)

    return

if __name__ == "__main__":

    main()
