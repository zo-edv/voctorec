import subprocess
import logging
import datetime
import os.path
import shlex
import time
import lib.connection as Connection
from gi.repository import GObject
import copy

# TODO: move templates to config file
ffmpegtemplate = """ffmpeg -y -nostdin -v \
{inputs} \
-ac 2 -channel_layout 2 -aspect 16:9 \
{videotracks} \
{audiotracks} \
-flags +global_header -flags +ilme+ildct \
-f segment -segment_time 180 -segment_format mpegts {filename}-%d.ts"""
videotracktemplate = "-map {id}:v -c:v:{id} mpeg2video -pix_fmt:v:{id} yuv420p -qscale:v:{id} 2 -qmin:v:{id} 2 -qmax:v:{id} 7 -keyint_min 0 -bf:{id} 0 -g:{id} 0 -intra:{id} -maxrate:{id} 90M "
audiotracktemplate = "-map {id}:a -c:a:{id} mp2 -b:a:{id} 192k -ac:a:{id} 2 -ar:a:{id} 48000 "
inputtemplate = "-i tcp://{host}:{port} "
filenameTemplate = "voctorec_{year}-{month}-{day}_{hour}-{minute}-{second}"

class MultiTrackRec:
    def __init__(self):
        self.recording = False
        self.curTime = ""
        self.curBitrate = ""
        self.curSize = ""
        self.ffmpegProcess = None
        self.videotracks = list()
        self.audiotracks = list()
        self.segmented = True
        self.segment_time = 180
        self.log = logging.getLogger("multitrackrec")
        self.log.info("MultiTrackRecorder Initialized")
        self.basepath = "/home/zoadmin/record/"

    def add_video_track(self, port, id, name):
        track = {"id": int(id), "name": str(name), "port": int(port)}
        self.videotracks.append(track)
        self.log.info("Added Videotrack {name}".format(name=name))
        self.log.debug("Track: " + str(track))

    def add_audio_track(self, id, name):
        track = {"id": int(id), "name": str(name)}
        self.audiotracks.append(track)
        self.log.info("Added Audiotrack {name}".format(name=name))
        self.log.debug("Track: " + str(track))

    def start_recording(self):

        self.log.info('starting recording')

        date = datetime.datetime.now()

        foldername = filenameTemplate.format(year=date.year, month=date.month, day=date.day, hour=date.hour,
                                           minute=date.minute, second=date.second)
        foldernamecopy = copy.copy(foldername)
        self.log.debug(foldername)
        self.log.debug(self.basepath)
        i = 0
        folderpath = self.basepath + foldername
        while os.path.exists(folderpath):
            folderpath = self.basepath + foldernamecopy + "_" + str(i)
            i += 1

        self.log.info("Creating Folder " + folderpath)
        os.mkdir(folderpath)


        cmd = self.get_ffmpeg_str(folderpath + "/segment")
        parsed = shlex.split(cmd)
        self.log.debug("Parsed cmd: " + str(parsed))

        if not self.ffmpegProcess:
            self.log.info("Starting FFmpeg Recording Process")
            self.ffmpegProcess = subprocess.Popen(parsed, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        else:
            self.log.error("Error: Process already running / exited unexpectedly. Restarting instead.")
            self.ffmpegProcess.terminate()
            self.ffmpegProcess = None
            self.start_recording()
        self.recording = True
        Connection.send("message", "rec_running")
        GObject.io_add_watch(self.ffmpegProcess.stderr, GObject.IO_IN, self.on_data)

    def stop_recording(self):
        self.ffmpegProcess.terminate()
        self.ffmepgProcess = None
        self.recording = False
        Connection.send("message", "rec_stop")

    def on_data(self, source, _, *args):
        line = source.readline()
        line = line.split()
        self.log.debug(line)
        try:
            if "time=" in line[-2]:
                self.curTime = line[-2][5:]

            self.log.debug("Time: {}, Bitrate: {}, Size: {}".format(self.curTime, self.curBitrate, self.curSize))
            Connection.send("message", "recstatus,{},{},{}".format(self.curTime, self.curBitrate, self.curSize))

        except IndexError:
            pass
        return True

    def get_ffmpeg_str(self, name):
        audioStr = ""
        videoStr = ""
        inputStr = ""
        for track in self.videotracks:
            videoStr += videotracktemplate.format(id=track["id"])
            inputStr += inputtemplate.format(host="localhost", port=track["port"])
        for track in self.audiotracks:
            audioStr += audiotracktemplate.format(id=track["id"])
        date = datetime.date.today()
        time = datetime.time()

        ffstr = ffmpegtemplate.format(inputs=inputStr, videotracks=videoStr, audiotracks=audioStr, filename=name)
        self.log.debug("FFmpeg String generated: " + ffstr)
        return ffstr
