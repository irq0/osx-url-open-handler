#!/usr/bin/python

import struct
import os.path
import subprocess
import re
import importlib

from objc import YES, NO, nil, signature
from AppKit import *
from Foundation import *
from PyObjCTools import NibClassBuilder, AppHelper

import ConfigParser

config = ConfigParser.ConfigParser()

def get_script_for_scheme(scheme):
    script = os.path.expanduser(config.get(scheme, 'run'))
    if not os.path.isfile(script):
        raise Exception("Config Error: Script for {0} is not a file".format(scheme))

    return script

def get_py_module_for_scheme(scheme):
    result = config.get(scheme, 'module')
    return result

def get_py_func_for_scheme(scheme):
    result = config.get(scheme, 'func')
    return result

def get_run_func(scheme):
    return [run_script, run_python][int(config.has_option(scheme, 'module'))]

def run_script(scheme_name, hier_part):
    NSLog("Running script handler")
    subprocess.call([get_script_for_scheme(scheme_name), hier_part])

def run_python(scheme_name, hier_part):
    mod_name = get_py_module_for_scheme(scheme_name)
    func_name = get_py_func_for_scheme(scheme_name)

    NSLog("Running python handler mod=%@ func=%@", mod_name, func_name)

    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)

    func(hier_part)

def run_url(schema_name, hier_part):
    get_run_func(schema_name)(schema_name, hier_part)

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
        keyDirectObject = struct.unpack(">i", "----")[0]
        url = event.paramDescriptorForKeyword_(keyDirectObject).stringValue().decode('utf8')

        urlPattern = re.compile(r"^(.*?)://(.*)$")
        match = urlPattern.match(url)

        schema = match.group(1)
        hier_part = match.group(2)

        NSLog("Received URL: %@", url)
        run_url(schema, hier_part)

def main():
    config.read(os.path.expanduser('~/Library/Preferences/url-open-handler.cfg'))

    app = NSApplication.sharedApplication()

    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)

    AppHelper.runEventLoop()

if __name__ == '__main__':
    main()
