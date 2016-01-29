"""OpenMediaRepository - a web based open media repository framework.

   Copyright (c) 2015 Florian Berger <florian.berger@posteo.de>


   ## Basic Data Structures

   The basic data structures are the Repository and the Accounts.

       >>> import openmediarepository as omr
       >>> repository= omr.Repository()
       >>> accounts = omr.Accounts()
       >>>


   ## Accounts API

   Accounts are represented by an email address.

       >>> accounts.add("alice@some.domain")
       >>> accounts.add('"Bob" <bob@some.domain>')
       >>> accounts.add('Eve <eve@some.domain>')

   The email address serves as an unique identifier.
   Duplicates will be rejected.

       >>> accounts.add("bob@some.domain")
       Traceback (most recent call last):
       ...
       ValueError: Address already exists: 'bob@some.domain'

   Adresses and possible names are available in the Accounts.accounts
   dict.

       >>> emails = list(accounts.accounts.keys())
       >>> emails.sort()
       >>> ["<{0}>: '{1}'".format(email, accounts.accounts[email]) for email in emails]
       ["<alice@some.domain>: ''", "<bob@some.domain>: 'Bob'", "<eve@some.domain>: 'Eve'"]

   Accounts can be dumped for later reconstruction.

       >>> accounts.dump()
       >>> accounts = omr.Accounts()
       >>> list(accounts.accounts.keys())
       []
       >>> accounts.load()
       >>> emails = list(accounts.accounts.keys())
       >>> emails.sort()
       >>> ["<{0}>: '{1}'".format(email, accounts.accounts[email]) for email in emails]
       ["<alice@some.domain>: ''", "<bob@some.domain>: 'Bob'", "<eve@some.domain>: 'Eve'"]


   ## Items

   Media repository items are key-value storages with a mandatory set
   of keys. They can either be represented by a dict or by an object
   who responds accordingly to attribute queries.

   The identifier of an item is the hex digest of the Whirlpool hash
   of its content.

   Items may posess additional attributes, as defined in the Dublin
   Core Metadata standard.

       >>> import hashlib
       >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 1 --></svg>", encoding="utf8"))
       >>> test_item_1 = {"identifier" : hash.hexdigest()}
       >>> test_item_1["creator"] = emails[0]
       >>> test_item_1["title"] = "Test 1 SVG image"

       >>> class TestItem:
       ...     pass
       >>> test_item_2 = TestItem()
       >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 2 --></svg>", encoding="utf8"))
       >>> test_item_2.identifier = hash.hexdigest()
       >>> test_item_2.creator = emails[1]
       >>> test_item_2.format = "image/svg"

   For convenience, there is an item class.

       >>> import io
       >>> test_item_3 = omr.Item(io.BytesIO(bytes("<svg><!-- Test 3 --></svg>", encoding="utf8")), creator=emails[2], description="Test 3 SVG image.")

   Access to mandatory properties of an Item which are not defined
   will return an empty string.

       >>> test_item_3.date
       ''

   Arbitrary attributes will not.

       >>> test_item_3.arbitrary
       Traceback (most recent call last):
       ...
       AttributeError: 'Item' object has no attribute 'arbitrary'


   ## Repository API

       >>> repository.add(test_item_1)
       >>> repository.add(test_item_2)
       >>> repository.add(test_item_3)

   Invalid items will be rejected.

       >>> repository.add({"not" : "valid"})
       Traceback (most recent call last):
       ...
       RuntimeError: Can not add invalid item to repository: '{'not': 'valid'}'

   Repository.items allows for listing and enumerating items.

       >>> identifiers = list(repository.items.keys())
       >>> identifiers.sort()

   Let's display the identifiers shortened, for reading convenience.

       >>> [identifier[:8] for identifier in identifiers]
       ['6f847d12', '9d71ca42', 'aac73176']

   The repository can be dumped for later reconstruction.

       >>> def print_items(identifiers):
       ...     attributes = list(omr.DUBLIN_CORE_PROPERTIES.keys())
       ...     attributes.sort()
       ...     for identifier in identifiers:
       ...         print(identifier[:8])
       ...         for attribute in attributes:
       ...             value = None
       ...             try:
       ...                 value = repository.items[identifier][attribute]
       ...             except KeyError:
       ...                 # It's a dict, but the key is missing
       ...                 value = ""
       ...             except:
       ...                 try:
       ...                     value = repository.items[identifier].__getattr__(attribute)
       ...                 except:
       ...                     try:
       ...                         value = repository.items[identifier].__dict__[attribute]
       ...                     except:
       ...                         # Giving up
       ...                         value = ""
       ...             if value != "":
       ...                 value = " " + value[:32]
       ...             print("    {0}:{1}".format(attribute, value))
       ...     return
       >>> print_items(identifiers)
       6f847d12
           creator: bob@some.domain
           date:
           description:
           format: image/svg
           identifier: 6f847d125a850a71cb1aed36ee680be6
           rights:
           title:
       9d71ca42
           creator: alice@some.domain
           date:
           description:
           format:
           identifier: 9d71ca42166e88aa759331b6b82de5b1
           rights:
           title: Test 1 SVG image
       aac73176
           creator: eve@some.domain
           date:
           description: Test 3 SVG image.
           format:
           identifier: aac73176dd0aa26ecfad7e7263c60572
           rights:
           title:
       >>> repository.dump()
       >>> repository = omr.Repository()
       >>> repository.items
       {}
       >>> repository.load()
       >>> identifiers = list(repository.items.keys())
       >>> identifiers.sort()
       >>> print_items(identifiers)
       6f847d12
           creator: bob@some.domain
           date:
           description:
           format: image/svg
           identifier: 6f847d125a850a71cb1aed36ee680be6
           rights:
           title:
       9d71ca42
           creator: alice@some.domain
           date:
           description:
           format:
           identifier: 9d71ca42166e88aa759331b6b82de5b1
           rights:
           title: Test 1 SVG image
       aac73176
           creator: eve@some.domain
           date:
           description: Test 3 SVG image.
           format:
           identifier: aac73176dd0aa26ecfad7e7263c60572
           rights:
           title:


   ## HTTP API

   The CherryPy framework handles the HTTP API by means of translating
   URIs to instance methods of the WebApp class.

       >>> webapp = WebApp()

   ### Get a form to add an item

   /item/add

       >>> html_response = webapp.items.add()
       >>> html_response.startswith("<!DOCTYPE") or html_response.startswith("<html")
       True
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
import json
import cherrypy
import simple.html

VERSION = "0.1.0"

LOGGER = logging.getLogger("OpenMediaRepository")
LOGGER.setLevel(logging.DEBUG)
STDERR_FORMATTER = logging.Formatter("OpenMediaRepository [{levelname}] {funcName}(): {message} (l.{lineno})", style="{")
STDERR_HANDLER = logging.StreamHandler()
STDERR_HANDLER.setFormatter(STDERR_FORMATTER)
LOGGER.addHandler(STDERR_HANDLER)

PORT = 8006
THREADS = 10
AUTORELOAD = True

# http://www.dublincore.org/documents/dcmi-terms/#H3
#
DUBLIN_CORE_PROPERTIES = {
    "creator": "An entity primarily responsible for making the resource.",
    "date": "A point or period of time associated with an event in the lifecycle of the resource.",
    "description": "An account of the resource.",
    "format": "The file format, physical medium, or dimensions of the resource.",
    "identifier": "An unambiguous reference to the resource within a given context.",
    "rights": "Information about rights held in and over the resource.",
    "title": "A name given to the resource."}

class Item:
    """Convenience class, representing a repository item.

       Item instances may posess these attributes, as defined in the
       Dublin Core Metadata standard:

       Item.creator
           An entity primarily responsible for making the resource.

       Item.date
           A point or period of time associated with an event in the lifecycle of the resource.

       Item.description
           An account of the resource.

       Item.format
           The file format, physical medium, or dimensions of the resource.

       Item.identifier
           An unambiguous reference to the resource within a given context.

       Item.rights
           Information about rights held in and over the resource.

       Item.title
           A name given to the resource.
    """

    def __init__(self, fp, **kwargs):
        """Initialise.
           fp is a binary mode filepointer pointing to the media file
           to be represented.
           The constructor can be called with all keyword arguments
           present as keys in DUBLIN_CORE_PROPERTIES.keys().
        """

        self.identifier = hashlib.new("whirlpool", fp.read()).hexdigest()

        for key in kwargs.keys():

            if key in DUBLIN_CORE_PROPERTIES.keys():

                self.__dict__[key] = kwargs[key]

        return

    def __getattr__(self, name):
        """Make sure access to undefined valid metadata attributes returns an empty string.
        """

        if name not in DUBLIN_CORE_PROPERTIES.keys():

            raise AttributeError("'Item' object has no attribute '{0}'".format(name))

        try:
            return self.__dict__[name]

        except:
            return ""

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

    def dump(self):
        """Serialise current repository to storage.
           The default implementation writes the data to a JSON file in CWD.
        """

        # Make sure we only use dicts

        dict_to_serialise = {}

        for identifier in self.items.keys():

            dict_to_serialise[identifier] = {}

            for attribute in DUBLIN_CORE_PROPERTIES.keys():

                value = None

                try:
                    value = self.items[identifier][attribute]

                except KeyError:
                    # It's a dict, but the key is missing
                    value = ""

                except:

                    try:
                        value = self.items[identifier].__getattr__(attribute)

                    except:

                        try:
                            value = self.items[identifier].__dict__[attribute]

                        except:
                            # Giving up
                            value = ""

                dict_to_serialise[identifier][attribute] = value

        with open("repository.json", "wt", encoding="utf8") as fp:

            fp.write(json.dumps(dict_to_serialise, sort_keys=True, indent=4) + "\n")

        return

    def load(self):
        """Read repository data from storage.
           The default implementation reads the data from a JSON file in CWD.
        """

        with open("repository.json", "rt", encoding="utf8") as fp:

            self.items = json.loads(fp.read())

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

            name_part, email_part = email.split(sep="<", maxsplit=1)

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

        with open("accounts.txt", "wt", encoding="utf8") as fp:

            for email_part in self.accounts.keys():

                fp.write('"{0}" <{1}>\n'.format(self.accounts[email_part], email_part))

        return

    def load(self):
        """Read account data from storage.
           The default implementation reads the data from a plain text file in CWD,
           using Accounts.add() for parsing.
        """

        with open("accounts.txt", "rt", encoding="utf8") as fp:

            for line in fp.readlines():

                self.add(line)

        return

class ItemsWebApp:
    """HTTP-REST-Interface to the Repository class, to be mounted in the CherryPy root.
    """

    # It is not feasible to expose Repository directly.
    # OOP uses verbs, while REST is supposed to use nouns.

    def add(self):

        page = simple.html.Page("Add Item")

        page.append("<p>ItemsWebApp.add() standing by</p>")

        return str(page)

    add.exposed = True
    
class WebApp:
    """Web application main class, suitable as cherrypy root.
    """

    def __init__(self):
        """Initialise WebApp.
        """

        self.index = "index.html not found in current working directory."

        try:
            with open("index.html", "rt", encoding="utf8") as fp:

                self.index = fp.read()

        except FileNotFoundError:

            # Default already set

            pass

        # Mount sub-handlers
        #
        self.items = ItemsWebApp()

        # Make self.__call__ visible to cherrypy
        #
        self.exposed = True

        return

    def __call__(self):
        """Called by cherrypy for the / root page.
           Returns 'index.html' from CWD, or an error message.
        """

        return self.index

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

    cherrypy.quickstart(root, config=config_dict)

    return

if __name__ == "__main__":

    main()
