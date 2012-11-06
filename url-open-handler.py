#!/usr/bin/python

import struct

from objc import YES, NO, nil, signature
from AppKit import *
from Foundation import *
from PyObjCTools import NibClassBuilder, AppHelper

class AppDelegate(NSObject):

    def applicationWillFinishLaunching_(self, notification):
        man = NSAppleEventManager.sharedAppleEventManager()
        man.setEventHandler_andSelector_forEventClass_andEventID_(
            self,
            "openURL:withReplyEvent:",
            struct.unpack(">i", "GURL")[0],
            struct.unpack(">i", "GURL")[0])
        man.setEventHandler_andSelector_forEventClass_andEventID_(
            self,
            "openURL:withReplyEvent:",
            struct.unpack(">i", "WWW!")[0],
            struct.unpack(">i", "OURL")[0])
        NSLog("Registered URL handler")

    @signature('v@:@@')
    def openURL_withReplyEvent_(self, event, replyEvent):
        NSLog("openURL")
        keyDirectObject = struct.unpack(">i", "----")[0]
        url = event.paramDescriptorForKeyword_(keyDirectObject).stringValue().decode('utf8')

        urlPattern = re.compile(r"^(.*?)://(.*)$")
        match = urlPattern.match(url)
        if match and match.group(1) == 'feed':
            url = match.group(2)
            match = urlPattern.match(url)
            if not match:
                url = u'http://%s' % url

        if url.startswith('message'):
            pass

        NSLog("%@", url)
        # TODO handler urls
#        NSApplication.sharedApplication().terminate_(nil)
#        open_new_mutt_in_iterm(get_message("trinity-6639d7a5-32bc-48be-9ab0-7a9a6cf7f5a4-1352162349366@msvc067")):

def main():
    app = NSApplication.sharedApplication()

    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)

    AppHelper.runEventLoop()

if __name__ == '__main__':
    main()
