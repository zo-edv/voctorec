#!/usr/bin/env python3

import signal
import logging
import sys



from gi.repository import GObject

GObject.threads_init()
import time

from lib.args import Args
from lib.loghandler import LogHandler
import lib.connection as Connection

def msgCallback(args):
    log = logging.getLogger("MessageHandler")
    log.info("Received Message: " + str(args))



class Voctoconfig(object):

    def __init__(self):
        self.log = logging.getLogger("Voctoconfig")
        self.log.debug("Creating GObject Mainloop")
        self.mainloop = GObject.MainLoop()

    def run(self):
        self.log.info("Running MainLoop")
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            self.log.info("Terminated via KeyboardInterrupt")

    def quit(self):
        self.log.info("Quitting MainLoop")
        self.mainloop.quit()

def main():
    docolor = (Args.color == 'always') or (Args.color == 'auto' and
                                           sys.stderr.isatty())
    loghandler = LogHandler(docolor, Args.timestamp)
    logging.root.addHandler(loghandler)
    if Args.verbose >= 2:
        level = logging.DEBUG
    elif Args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.root.setLevel(level)
    logging.debug('setting SIGINT handler')
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Connection.establish(Args.host)
    Connection.enterNonblockingMode()
    Connection.on("message", msgCallback)
    mainloop = GObject.MainLoop()
    mainloop.run()



if __name__ == '__main__':
    main()