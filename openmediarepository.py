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
   of keys.

   The identifier of an item is the hex digest of the Whirlpool hash
   of its content.

   Items may posess additional attributes, as defined in the Dublin
   Core Metadata standard.

   For convenience, there is an Item class.

       >>> import io
       >>> test_item_supplied_class = omr.Item(io.BytesIO(bytes("<svg><!-- Test 3 --></svg>", encoding="utf8")), creator=emails[2], description="Test 3 SVG image.")

   Access to mandatory properties of an Item which are not defined
   will return an empty string.

       >>> test_item_supplied_class.date
       ''

   Arbitrary attributes will not.

       >>> test_item_supplied_class.arbitrary
       Traceback (most recent call last):
       ...
       AttributeError: 'Item' object has no attribute 'arbitrary'


   ## Repository API

   Items can be added either as an Item instance, as a dict, or as an
   object which responds accordingly to attribute queries.

       >>> import hashlib
       >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 1 --></svg>", encoding="utf8"))
       >>> test_item_dict = {"identifier" : hash.hexdigest()}
       >>> test_item_dict["creator"] = emails[0]
       >>> test_item_dict["title"] = "Test 1 SVG image"

       >>> class TestItem:
       ...     pass
       >>> test_item_custom_class = TestItem()
       >>> hash = hashlib.new("whirlpool", bytes("<svg><!-- Test 2 --></svg>", encoding="utf8"))
       >>> test_item_custom_class.identifier = hash.hexdigest()
       >>> test_item_custom_class.creator = emails[1]
       >>> test_item_custom_class.format = "image/svg"

       >>> repository.add(test_item_dict)
       >>> repository.add(test_item_custom_class)
       >>> repository.add(test_item_supplied_class)

   Invalid items will be rejected.

       >>> repository.add({"not" : "valid"})
       Traceback (most recent call last):
       ...
       RuntimeError: Can not add invalid item to repository: '{'not': 'valid'}'

   The Repository.items dict allows for listing and enumerating items.

   After adding, all items in the Repository will adhere to the
   interface of the Item class, i.e. you can access their attributes
   the Python way.

       >>> l = [item.identifier[:8] for item in repository.items.values()]
       >>> l.sort()
       >>> l
       ['6f847d12', '9d71ca42', 'aac73176']


  The repository can be dumped for later reconstruction.

       >>> identifiers = list(repository.items.keys())
       >>> identifiers.sort()
       >>> def print_items(identifiers):
       ...     attributes = list(omr.DUBLIN_CORE_PROPERTIES.keys())
       ...     attributes.sort()
       ...     for identifier in identifiers:
       ...         print(identifier[:8])
       ...         for attribute in attributes:
       ...             value = None
       ...             try:
       ...                 value = repository.items[identifier].__dict__[attribute]
       ...             except:
       ...                 value = ""
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
           source:
           title:
       9d71ca42
           creator: alice@some.domain
           date:
           description:
           format:
           identifier: 9d71ca42166e88aa759331b6b82de5b1
           rights:
           source:
           title: Test 1 SVG image
       aac73176
           creator: eve@some.domain
           date:
           description: Test 3 SVG image.
           format:
           identifier: aac73176dd0aa26ecfad7e7263c60572
           rights:
           source:
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
           source:
           title:
       9d71ca42
           creator: alice@some.domain
           date:
           description:
           format:
           identifier: 9d71ca42166e88aa759331b6b82de5b1
           rights:
           source:
           title: Test 1 SVG image
       aac73176
           creator: eve@some.domain
           date:
           description: Test 3 SVG image.
           format:
           identifier: aac73176dd0aa26ecfad7e7263c60572
           rights:
           source:
           title:


   ## HTTP API

   The CherryPy framework handles the HTTP API by means of translating
   URIs to instance methods of the WebApp class.

       >>> webapp = WebApp()

   ### Get a form to add an item

   URI: /items/add
   Method: GET

       >>> html_response = webapp.items.add()
       >>> html_response.startswith("<!DOCTYPE") or html_response.startswith("<html")
       True

   ### Add an item

   URI: /items
   Method: POST

       >>> html_response = webapp.items(**test_item_dict)
       >>> html_response.index("Item added") > -1
       True

   Duplicate additions are not allowed via the HTTP API.

       >>> html_response = webapp.items(**test_item_dict)
       >>> html_response.index("identifier already exists") > -1
       True

   ### Display multiple items

   URI: /items
   Method: GET

       >>> html_response = webapp.items()
       >>> html_response.index("<ul>") > -1
       True

   ### Display a single item

   URI: /items/(identifier)
   Method: GET

       >>> html_response = webapp.items.__getattr__(test_item_dict["identifier"])
       >>> html_response.index("<ul>") > -1
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
import datetime
import glob
#
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
    "source": "A related resource from which the described resource is derived.",
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

    def __init__(self, fp = None, **kwargs):
        """Initialise.
           fp is a binary mode filepointer pointing to the media file
           to be represented.
           The constructor can be called with all keyword arguments
           present as keys in DUBLIN_CORE_PROPERTIES.keys().
        """

        self.identifier = None

        if fp is not None:
            
            self.identifier = hashlib.new("whirlpool", fp.read()).hexdigest()

        elif "identifier" in kwargs.keys() and kwargs["identifier"]:

            self.identifier = kwargs["identifier"]

        else:

            raise RuntimeError("Can not determine valid identifier from '{0}' and {1}".format(fp, kwargs))

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
        """Add an item to the repository as an Item instance.
           item is either a dictionary or returns fitting values
           on __getattr__() calls. An Item instance does the latter.
        """

        # First shot: we believe it to already be an Item instance,
        # or compatible.
        #
        try:
            self.items[item.identifier] = item

        except AttributeError:

            # Apparently not. Let's try with a dict.

            try:

                self.items[item["identifier"]] = Item(**item)
            
            except:

                # Giving up
                #
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

                try:
                    dict_to_serialise[identifier][attribute] = self.items[identifier].__dict__[attribute]

                except KeyError:

                    # Not adding missing attribute

                    pass

        with open("repository.json", "wt", encoding="utf8") as fp:

            fp.write(json.dumps(dict_to_serialise, sort_keys=True, indent=4) + "\n")

        return

    def load(self):
        """Read repository data from storage.
           The default implementation reads the data from a JSON file in CWD.
        """

        items_as_dict = {}

        with open("repository.json", "rt", encoding="utf8") as fp:

            items_as_dict = json.loads(fp.read())

        for identifier in items_as_dict.keys():

            self.items[identifier] = Item(**items_as_dict[identifier])

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

       Attributes:

       ItemsWebApp.repository
           Repository instance.

       ItemsWebApp.css
           CSS code to be put in <style></style> section of HTML output.
    """

    # It is not feasible to expose Repository directly.
    # OOP uses verbs, while REST is supposed to use nouns.

    def __init__(self, repository, css = ""):
        """Initialise ItemsWebApp with a dependency-injected Repository.
           css, if given, is CSS code to be put in <style></style> section of HTML output.
        """

        self.css = css

        self.repository = repository

        return

    def __call__(self, *args, **kwargs):
        """List items, or add a given item.
           Called by cherrypy.
           HTTP GET calls will submit args.
           HTTP POST calls will submit kwargs.
        """

        # NOTE: Multiple exit points ahead.
        
        page = simple.html.Page("Item", css=self.css)
        
        if args:

            if args[0] not in self.repository.items.keys():

                # TODO: Return error code
                #
                page.append("<p>Error: item does not exist</p>")

                return str(page)

            page.append('<ul><li><a href="/">Home</a></li><li><a href="/items">Items</a></li></ul>')
        
            # TODO: Item rendering should be done by a special method
            #
            page.append("<h1>{0}</h1>".format(self.repository.items[args[0]].title))

            page.append("<ul>")

            for dc_key in DUBLIN_CORE_PROPERTIES.keys():

                if dc_key != "title":

                    page.append("<li>{0}: {1}</li>".format(dc_key.capitalize(), self.repository.items[args[0]].__getattr__(dc_key)))

            page.append("</ul>")

            return str(page)

        # No args.

        page = simple.html.Page("Items", css=self.css)

        if len(kwargs):

            if (not "identifier" in kwargs.keys()
                or not len(kwargs["identifier"])
                or not kwargs["identifier"].isalnum()):

                # TODO: Return error code
                #
                page.append("<p>Error: invalid identifier</p>")

                return str(page)

            if kwargs["identifier"] in self.repository.items.keys():

                # TODO: Return error code
                #
                page.append("<p>Error: identifier already exists</p>")

                return str(page)

            item_dict = {"identifier": kwargs["identifier"]}

            for key in kwargs.keys():

                if key != "identifier" and key in DUBLIN_CORE_PROPERTIES.keys():

                    item_dict[key] = kwargs[key]

            self.repository.add(item_dict)

            # Be persistent
            #
            self.repository.dump()

            page.append("<h1>Item added</h1>")

            page.append('<p><a href="/items/{0}">View item</a></p>'.format(kwargs["identifier"]))

            return str(page)

        # No kwargs either.

        page.append('<ul><li><a href="/">Home</a></li></ul>')
        
        page.append("<h1>Items</h1>")

        page.append("<ul>")
        
        for identifier in self.repository.items.keys():

            page.append('<li><a href="/items/{0}">{1}</a>'.format(identifier, self.repository.items[identifier].title))

            page.append("<ul>")
            
            for dc_key in DUBLIN_CORE_PROPERTIES.keys():

                if dc_key != "title":

                    page.append("<li>{0}: {1}</li>".format(dc_key.capitalize(), self.repository.items[identifier].__getattr__(dc_key)))

            page.append("</ul>")        

            page.append("</li>")

        page.append("</ul>")

        return str(page)

    def add(self):

        page = simple.html.Page("Add Item", css=self.css)

        page.append('<ul><li><a href="/">Home</a></li></ul>')
        
        page.append("<h1>Add item</h1>")

        page.append("<dl>")
        
        for key in DUBLIN_CORE_PROPERTIES.keys():

            page.append("<dt>{0}</dt><dd>{1}</dd>".format(key.capitalize(), DUBLIN_CORE_PROPERTIES[key]))

        page.append("</dl>")

        form = simple.html.Form(action="/items",
                                method="POST")

        form.add_fieldset("Item")

        for key in DUBLIN_CORE_PROPERTIES.keys():

            value = ""
            
            if key == "date":

                value = datetime.date.today().isoformat()

            if key == "rights":

                value = "CC-BY"

            if key == "format":

                value = "text/plain"

            form.add_input(label = key.capitalize(),
                           type = "text",
                           name = key,
                           value = value)

        page.append(str(form))

        return str(page)

    add.exposed = True

class WebApp:
    """Web application main class, suitable as cherrypy root.

       Attributes:

       WebApp.css
           CSS code to be put in <style></style> section of HTML output.

       WebApp.repository
           Repository instance.

       WebApp.index
           String containing the index HTML page.

       WebApp.items
           ItemsWebApp instance.
    """

    def __init__(self, css = ""):
        """Initialise WebApp.
           css, if given, is CSS code to be put in <style></style> section of HTML output.
        """

        self.css = css

        self.repository = Repository()

        try:
            self.repository.load()
            
        except FileNotFoundError:
            
            # File will be created on first edit
            #
            pass

        self.index = "index.html not found in current working directory."

        try:
            with open("index.html", "rt", encoding="utf8") as fp:

                self.index = fp.read()

        except FileNotFoundError:

            # Default already set

            pass

        # Mount sub-handlers
        #
        self.items = ItemsWebApp(self.repository, self.css)
        self.items.exposed = True

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

    css = ""

    css_files = glob.glob("*.css")

    if css_files:

        with open(css_files[0], "rt", encoding = "utf8") as fp:

            css = fp.read()

    root = WebApp(css)

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
