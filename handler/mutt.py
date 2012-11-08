#!/usr/bin/env python

# Open message:// protocol in new mutt session


import subprocess
import json
import os.path
import sys
import re
import struct
import time
import urllib

from appscript import *

MUTT="/Users/seri/homebrew/bin/mutt"

def quote_filename(filename):
    return filename.replace(" ", "\\ ")

def get_message(message_id=None):
    result = None
    out = subprocess.check_output(["notmuch", "search", "--format=json",
                                   "--output=files", "--limit=1",
                                   "id:{message_id}".format(message_id=message_id)])
    filenames = json.loads(out)

    if filenames and len(filenames) > 0:
        result = {
            "mailbox" : quote_filename(get_mailbox_path(filenames[0])),
            "id" : message_id,
        }

        if not os.path.isdir(result["mailbox"]):
            print "Mailbox {0} is not a directory!".format(result)
            result = None

    return result

def get_mailbox_path(filename):
    def find_path(head, tail):
        if tail in ("cur", "new", "tmp"):
            return head
        elif not head:
            return None
        else:
            return find_path(*os.path.split(head))

    return find_path(*os.path.split(filename))


def iterm_sess_dict(sess):
    return {
        "name"    : sess.name(),
        "tty"     : sess.tty(),
        "session" : sess,
        }

def iterm_sessions():
    result = []

    for term in app("iTerm").terminals():
        for sess in term.sessions():
            result.append(iterm_sess_dict(sess))
    return result

def start_new_mutt_cmd(message):
    return [MUTT,
            "-f", message["mailbox"],
            "-z",
            "-e", "push <search>~i\"{0}\"<enter><enter>".format(message["id"])]

def mutt_intern_select_cmd(message):
    return """\
: push <change-folder>{mailbox}<enter>\
<search>~i\"{id}\"<enter><enter>""".format(**message)


def cmd_seq_to_str(seq):
    result = seq[0]
    result += " "
    result += " ".join(map(lambda x: "\"{0}\"".format(x), seq[1:]))
    return result

def open_new_mutt_here(message):
    subprocess.call(start_new_mutt_cmd(message))

def open_new_mutt_in_iterm(message):
    ap = app("iTerm")
    ap.activate()
    sess = ap.current_terminal().sessions.end.make(new=k.session)
    sess.name.set("mutt")
    sess.exec_(command=cmd_seq_to_str(start_new_mutt_cmd(message)))

def open_mail_in_existing_mutt(message, fallback=open_new_mutt_in_iterm):
    sess = filter(lambda x : x["name"] == "mutt", iterm_sessions())

    if len(sess) == 0:
        print "No mutt sessions found -> opening new one"
        fallback(message)
    else:
        session = sess[0]["session"]
        print "Opening mail in session: {0}".format(sess[0]["tty"])

        session.write(text=mutt_intern_select_cmd(message))

def unquote_mid(mid):
    result = urllib.unquote(mid)
    result = result.replace("<","").replace(">","")
    return result

def handle_message(mid, func=open_mail_in_existing_mutt):
    from Foundation import NSLog

    mid = unquote_mid(mid)
    msg = get_message(mid)
    if not msg:
        NSLog("No message for %@ found!", mid)
    else:
        NSLog("Opening message %@", msg)
        func(get_message(mid))
