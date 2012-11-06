#!/usr/bin/env python

# Open message:// protocol in new mutt session


import subprocess
import json
import os.path
import sys

from appscript import *


MUTT="/Users/seri/homebrew/bin/mutt"

def get_message(message_id=None):
    result = None
    out = subprocess.check_output(["notmuch", "show", "--format=json",
                                   "id:{message_id}".format(message_id=message_id)])
    msg = json.loads(out)

    if msg:
        msg = msg[0][0][0]
        msg["mailbox"] = get_mailbox_path(msg["filename"])

        if not os.path.isdir(msg["mailbox"]):
            print "Mailbox {0} is not a directory!".format(msg["mailbox"])
            result = None
        else:
            result = msg

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
            "-e", "push <search>~i{0}<enter><enter>".format(message["id"])]

def mutt_intern_select_cmd(message):
    return """\
: push <change-folder>{mailbox}<enter>\
<search>~i{id}<enter><enter>""".format(**message)


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

def open_mail_in_existing_mutt(message):
    sess = filter(lambda x : x["name"] == "mutt", iterm_sessions())

    if len(sess) == 0:
        print "No mutt sessions found -> opening new one"
        open_new_mutt_in_iterm(message)
    else:
        session = sess[0]["session"]
        print "Opening mail in session: {0}".format(sess[0]["tty"])

        session.write(text=mutt_intern_select_cmd(message))


def main():
    if len(sys.argv) < 2:
        print "USAGE: {0} <message_id>".format(sys.argv[0])
        sys.exit(1)

    message = get_message(sys.argv[1])

    if not message:
        print "Could not find message"
        sys.exit(23)

    open_new_mutt_in_iterm(message)

if __name__ == '__main__': main()
