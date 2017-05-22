import subprocess
import logging
import datetime
import os.path
import shlex
import time

#TODO: move templates to config file
ffmpegtemplate = """ffmpeg -y -nostdin \
{inputs} \
-ac 2 -channel_layout 2 -aspect 16:9 \
{videotracks} \
{audiotracks} \
-flags +global_header -flags +ilme+ildct \
-f mpegts {filename}.ts"""
videotracktemplate = "-map {id}:v -c:v:{id} mpeg2video -pix_fmt:v:{id} yuv422p -qscale:v:{id} 2 -qmin:v:{id} 2 -qmax:v:{id} 7 -keyint_min 0 -bf:{id} 0 -g:{id} 0 -intra:{id} -maxrate:{id} 90M "
audiotracktemplate = "-map {id}:a -c:a:{id} mp2 -b:a:{id} 192k -ac:a:{id} 2 -ar:a:{id} 48000 "
inputtemplate = "-i tcp://{host}:{port} "
filenameTemplate = "voctorec_{year}-{month}-{day}_{hour}-{minute}-{second}"

class MultiTrackRec:
    def __init__(self):
        self.recording = False
        self.curTime = 0
        self.ffmpegProcess = None
        self.videotracks = list()
        self.audiotracks = list()
        self.log = logging.getLogger("multitrackrec")
        self.log.info("MultiTrackRecorder Initialized")

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
        cmd = self.get_ffmpeg_str()
        parsed = shlex.split(cmd)
        self.log.debug("Parsed cmd: " + str(parsed))
        if not self.ffmpegProcess:
            self.log.info("Starting FFmpeg Recording Process")
            self.ffmpegProcess = subprocess.Popen(parsed, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, )
        else:
            self.log.error("Error: Process already running / exited unexpectedly. Restarting instead.")
            self.ffmpegProcess.terminate()
            self.start_recording()
        self.recording = True

    def update_status(self):
        if self.ffmpegProcess.poll():
            self.recording = False
            self.log.error("FFmpeg exited unexpectedly. RC: " + str(self.ffmpegProcess.poll()))
        else:
            print("data:")
            print(self.ffmpegProcess.stderr.readlines())

    def get_ffmpeg_str(self):
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
        filename = filenameTemplate.format(year=date.year, month=date.month, day=date.day, hour=time.hour,
                                           minute=time.minute, second=time.second)
        filenamecopy = filename
        i = 0
        while os.path.exists(filename):
            filename = filenamecopy + "_" + str(i)
            i += 1
        ffstr = ffmpegtemplate.format(inputs=inputStr, videotracks=videoStr, audiotracks=audioStr, filename=filename)
        self.log.debug("FFmpeg String generated: " + ffstr)
        return ffstr

