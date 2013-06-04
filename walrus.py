#!/usr/bin/env python2.7
# Distributed under the MIT software license. See
# http://delicatebits.mit-license.org
#
# --------------------------------------------------------------------
# Project hosted at https://github.com/Eylrid/walrus
# --------------------------------------------------------------------

import sys
from optparse import OptionParser
import ConfigParser
import ntpath
import datetime
import xmlrpclib
import json
import imghdr
import os

walrusVer = '0.2'

# Q: What do I put here?
# A: The values you used when following https://bitmessage.org/wiki/API_Reference
#    For more information see README.md OR https://github.com/delicatebits/walrus
bitmsgpath = ''
api_user = ''
api_pass = ''
api_host = ''
api_port = ''

defaultRecipient = 'BM-2DAvCwKBR5F2Y5edkbQvpzQuLJdSVNDyUz'

def getDateTimeString():
    return '%s UTC' % (datetime.datetime.utcnow().strftime('%A, %B %d, %H:%M'))

def encode(imgpath):
    with open(imgpath, "rb") as f:
        data = f.read()
        return data.encode("base64")

class BitmessageApiClient():
    def __init__(self):
        if api_user=='' or api_host=='' or api_port=='':
            if not self.getCredentialsFromKeysFile():
                print 'Walrus is unable to send messages without access to PyBitmessage\'s API. Exiting.'
                print 'For help read README.md or https://github.com/delicatebits/walrus/blob/master/README.md'
                sys.exit(0)
        self.api_addr = 'http://%s:%s@%s:%s/' % (api_user,api_pass,api_host,api_port)
        self.ready = False
        self.api = xmlrpclib.ServerProxy(self.api_addr)
        self.identity = False
        self.addresses = None
        jsn = self.api.listAddresses()
        try:
            self.addresses = json.loads(jsn)
        except:
            print 'An error occurred when connecting!',jsn
            return
        if len(self.addresses['addresses']) == 0:
            print 'You must have at least one valid Identity in PyBitmessage'
            #userinput = raw_input('Would you like to create a Random Identity now? [y/N]: ').lower()
            #if 'yes' not in userinput and 'y' not in userinput:
            #    return
            #self.createRandomIdentity();
        else:
            self.addresses = self.addresses['addresses']
            self.ready = True

    def createRandomIdentity(self):
        """not yet ready"""
        print 'Warning: Make sure you aren\'t currently creating an Identity in the GUI'
        ripe18 = False
        userinput = raw_input('Spend extra time for a shorter address? [y/N]: ').lower()
        if 'y' in userinput: ripe18 = True
        label = 'Generated by Walrus'
        userinput = raw_input('Enter a label. Default=%s: '%label)
        if len(userinput) > 0: label = userinput
        self.identity = self.api.createRandomAddress(label.encode('base64'),ripe18)
        print self.identity

    def isReady(self):
        return self.ready

    def lookupBitmessageDataFolder(self):
        from os import path, environ
        if sys.platform == 'darwin':
            if "HOME" in environ:
                bitmessagedata = path.join(environ["HOME"], "Library/Application support/PyBitmessage") + '/'
            else:
                print 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
                sys.exit()
        elif 'win32' in sys.platform or 'win64' in sys.platform:
            bitmessagedata = path.join(environ['APPDATA'], "PyBitmessage") + '\\'
        else:
            bitmessagedata = path.expanduser(path.join("~", ".PyBitmessage/"))
        return bitmessagedata

    def getCredentialsFromKeysFile(self):
        if bitmsgpath != '':
            bitmessagedata = bitmsgpath
        else:
            bitmessagedata = self.lookupBitmessageDataFolder()
        config = ConfigParser.SafeConfigParser()
        key_path = os.path.join(bitmessagedata, 'keys.dat')
        config.read(key_path)
        try:
            global api_user,api_pass,api_host,api_port
            api_user = config.get('bitmessagesettings', 'apiusername')
            api_pass = config.get('bitmessagesettings', 'apipassword')
            api_host = config.get('bitmessagesettings', 'apiinterface')
            api_port = config.get('bitmessagesettings', 'apiport')
        except:
            print 'Walrus was unable to read %s' % (bitmessagedata + 'keys.dat')
            return False
        return True

    def getIdentityAddress(self):
        return self.identity['address']

    def identityIsSet(self):
        if self.identity != False:
            return True
        return False

    def getIdentity(self):
        if not self.ready: return False
        idcnt = 0;
        addresses = [a for a in self.addresses if a['enabled']==True]
        for x in addresses:
            print "[ID: %s]\tAddress: %s\tLabel: %s" % (idcnt,x['address'],x['label'])
            idcnt += 1
        userinput = raw_input('Choose an ID: ')
        try:
            i = int(userinput)
        except ValueError:
            print '%s is an invalid choice.' % userinput
            return False
        if len(addresses)-1 < i:
            print '%s is an invalid choice.' % i
            return False
        self.identity = addresses[int(userinput)]
        print 'Message will be sent as %s, %s' % (self.identity['label'],self.identity['address'])
        return True

    def checkFromIdentity(self,userinput):
        if not self.ready: return False
        for x in self.addresses:
            if x['address'] == userinput or x['label'] == userinput:
                if x['enabled'] != True:
                    print '(%s) %s is Disabled!' % (x['label'],x['address'])
                else:
                    self.identity = x
                    print 'Message will be sent as %s, %s' % (self.identity['label'],self.identity['address'])
                    return True
        return False

    def sendMessage(self,toAddress,subject,message):
        if not self.ready or not self.identity:
            print 'Unable to send message.'
            return False
        self.api.sendMessage(toAddress, self.identity['address'], subject, message)
        print 'Message sent to %s!' % defaultRecipient

    def sendBroadcast(self,subject,message):
        if not self.ready or not self.identity:
            print 'Unable to broadcast message.'
            return False
        self.api.sendBroadcast(self.identity['address'], subject, message)
        print 'Message broadcast!'

def create_message(filetype, encoded):
    message = """<html>
<!-- This message was sent via walrus v.%s -->
<!-- You can view richtext messages by right-clicking -->
<!--    the inbox item and choosing "View as Richtext" -->
<!--    If you've updated PyBitmessage since April 2, 2013 -->
<!-- Walrus can be found at: https://github.com/Eylrid/walrus -->
<style type="text/css">
    #header { font-size: 12px; color: #555; }
    #image { max-width: 999px; max-height: 300px; }
</style>
<center>
    <div id="header">
        <p>Sent on %s</p>
    </div>
    <div id="image">
        <img src='data:image/%s;base64, %s' />
    </div>
</center>
</html>""" % (walrusVer, getDateTimeString(), filetype, encoded)

    return message

def main():
    global defaultRecipient
    parser = OptionParser(usage="usage: %prog filename [options]",
                          version="%prog "+walrusVer)
    parser.add_option("-s", "--send", action="store_true", dest="flag_send",
                      default=False, help="Send output to Address")
    parser.add_option("-b", "--broadcast", action="store_true", dest="flag_broadcast",
                      default=False, help="Broadcast output")
    parser.add_option("-d", "--save", action="store", dest="flag_save",
                      default=False, help="Path to save message to disk")
    parser.add_option("-f", "--from", action="store", dest="flag_from", metavar='FROM',
                      default=False, help="Address/Label to send from")
    parser.add_option("-t", "--to", action="store", dest="flag_to", metavar='TO',
                      default=defaultRecipient, help="Address/Label to send to. Default is %default")
    parser.add_option("-u", "--subject", action="store", dest="flag_subject", metavar='SUBJECT',
                      default=False, help="Subject of the message. Default is image name.")
    (options, args) = parser.parse_args()

    if len(args) == 1:
        file_path = args[0]
        file_name = ntpath.basename(file_path)
    else:
        print 'Error: Path to image must be provided'
        return

    if not os.path.isfile(file_path):
        print '%s was not found on your filesystem!' % file_path
        return

    filetype = imghdr.what(file_path)
    if filetype is None:
        print '%s Does not appear to be an image.' % file_path
        return;
    else:
        print '%s is of type: %s' % (file_name, filetype)

    encoded = encode(file_path)
    api = None

    message = create_message(filetype, encoded)

    if options.flag_save != False:
        save = True
        if os.path.isfile(options.flag_save):
            #file already exists
            print '%s already exists.' %options.flag_save
            userinput = raw_input('Overwrite?')
            if 'yes' not in userinput and 'y' not in userinput:
                save = False

        if save:
            with open(options.flag_save, 'w') as file:
                file.write(message)
            print 'Saved to %s' %options.flag_save

    if options.flag_send and options.flag_broadcast:
        print 'Both send and broadcast chosen. Broadcasting only.'
        options.flag_send = False

    if not (options.flag_send or options.flag_broadcast):
        print 'Message:\n%s' % message
        return

    apiClient = BitmessageApiClient()
    if not apiClient.isReady():
        print 'There was an error with the API. Please check your credentials, and make sure you have at least 1 Identity'
        return

    if options.flag_from != False:
        if not apiClient.checkFromIdentity(options.flag_from):
            print 'Invalid From Address/Label provided.'
    if not apiClient.identityIsSet():
        if not apiClient.getIdentity():
            return

    if options.flag_send:
        if options.flag_to != defaultRecipient:
            print 'To Addresses/Labels are not validated, yet'
            userinput = raw_input('Are you sure you want to send a message to %s [y/N]: ' % options.flag_to).lower()
            if 'yes' not in userinput and 'y' not in userinput:
                print 'Exiting'
                exit(0)
            else:
                defaultRecipient = options.flag_to

    print 'Attempting to generate and send message'
    if not apiClient.isReady() or not apiClient.identityIsSet():
        print 'Something went wrong with the API, exiting.'
        return

    if options.flag_subject != False:
        subject = options.flag_subject
    else:
        subject = file_name

    assert options.flag_broadcast or options.flag_send

    if options.flag_broadcast:
        apiClient.sendBroadcast(subject.encode('base64'), message.encode('base64'))
    else:
        apiClient.sendMessage(defaultRecipient, subject.encode('base64'), message.encode('base64'))

    print 'Operations Complete! exiting.'

if __name__ == '__main__':
    main()