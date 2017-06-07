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
from lib.multitrackrec import MultiTrackRec






class voctorec(object):

    def __init__(self):
        self.log = logging.getLogger("voctorec")
        self.log.debug("Creating GObject Mainloop")
        self.mainloop = GObject.MainLoop()

        Connection.establish(Args.host)
        Connection.enterNonblockingMode()
        Connection.on("message", self.msgCallback)

        #TODO automatic track id
        self.rec = MultiTrackRec()
        self.rec.add_video_track(11000, 0, "mix")
        self.rec.add_video_track(13000, 1, "cam_mirror")
        self.rec.add_video_track(13001, 2, "grabber_mirror")
        self.rec.add_audio_track(0, "mainaudio")

    def msgCallback(self, args):
        log = logging.getLogger("MessageHandler")
        log.info("Received Message: " + str(args))
        if args == "rec":
            if self.rec.recording:
                self.rec.stop_recording()
            else:
                self.rec.start_recording()

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

    vrec = voctorec()
    vrec.run()




if __name__ == '__main__':
    main()