"""OpenMediaRepository - a web based open media repository framework.

   Copyright (c) 2015 Florian Berger <florian.berger@posteo.de>


   ## Basic Data Structures

   The basic data structures are the Repository and the Accounts.

   >>> import openmediarepository as omr
   >>> r = omr.Repository()
   >>> a = omr.Accounts()
   >>>


   ## Repository Items

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
    """

    pass

class Accounts:
    """Represent accounts, and provide access.
    """

    pass

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
