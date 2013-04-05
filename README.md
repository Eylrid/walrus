walrus
======

Walrus is a tool for sending images in [PyBitmessage](Bitmessage/PyBitmessage).

Roughly, it:
* Base64 encodes the provided image
* Wraps the image string in richtext markup
* Sends the result as a message

To do those things it uses the API built into [PyBitmessage](Bitmessage/PyBitmessage)

Bitmessage's Wiki explains [how to configure your API credentials](https://bitmessage.org/wiki/API_Reference).

configuration
-------------

Walrus needs your API credentials. By default Walrus will attempt to load PyBitmessage's keys.dat from PyBitmessage's appdata folder. This should be fine for most users.

If you're running PyBitmessage in portable mode you'll need to set the path to the PyBitmessage folder. Use the `bitmsgpath` variable near the top of walrus.py to do so.

If you'd rather manually specify the username, password, host, and port, you can do so by setting the variables directly below `bitmsgpath`.

Walrus, by default, assumes you want to share images with the Image Board mailing list. The address is set below `bitmsgpath`. You can also specify an address to send to at runtime using the -t flag. 

patches
-------

Occasionally I will make changes to PyBitmessage to better suite me. Sometimes, if the change could be directly useful to walrus, I'll include a patch in the /patches folder.

Unless explicitly stated, they're released under the MIT license. *Use them at your own risk.*

**How to apply a patch**:

Download/copy the .patch file to your PyBitmessage folder and run `git apply [patch]`

usage
-----

```
Usage: walrus.py filename [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -s, --send            Send output to Address
  -f FROM, --from=FROM  Address/Label to send from
  -t TO, --to=TO        Address/Label to send to.
  -u SUBJECT, --subject=SUBJECT
                        Subject of the message. Default is image name.
```

Example of printing a base64 string of /home/user/image.png:

`$ python walrus.py /home/user/image.png`

todo
----

- [x] Get basic functionality implemented
- [ ] Flesh out API portion and split into separate file
- [ ] Support multiple images per message
- [ ] Ensure To Address is valid
- [ ] Make compatible with Python 3

help
----

Walrus has been tested on Ubuntu. It should work just as well on OSX and Windows but I can't be sure. Please open an issue if you've found an error in Walrus.

If you've found a problem with [PyBitmessage](Bitmessage/PyBitmessage), please open an issue on their Github issue tracker

news
----

I've created an address to broadcast news about walrus

Add `BM-BbZhmd6xAZHMPktvZ83122e9Y9XpxJpA` to your Subscriptions today

contribute
----------

I'd be happy to receive suggestions and pull requests here on Github.

license
-------

Walrus is licensed under the MIT license. See the included LICENSE file or http://delicatebits.mit-license.org
