import subprocess

ffmpegtemplate = """ffmpeg \
	-y -nostdin \
	{inputs} \
	-ac 2 -channel_layout 2 -aspect 16:9 \
	{videotracks} \
    {audiotracks} \
	-flags +global_header -flags +ilme+ildct \
	-f mpegts output.ts"""
videotracktemplate = "-map {id}:v -c:v:{id} mpeg2video -pix_fmt:v:{id} yuv422p -qscale:v:{id} 2 -qmin:v:{id} 2 -qmax:v:{id} 7 -keyint_min 0 -bf:{id} 0 -g:{id} 0 -intra:{id} -maxrate:{id} 90M "
audiotracktemplate = "-map {id}:a -c:a:{id} mp2 -b:a:{id} 192k -ac:a:{id} 2 -ar:a:{id} 48000 "


class multitrackrec:
    def __init__(self):
        self.recording = False
        self.curTime = 0
        self.filenameTemplate = "voctorec_{year}-{month}-{day}_{hour}"
        self.ffmpegProcess = None
        self.videotracks = {}
        self.audiotracks = {}
        self.log = logging.getLogger("multitrackrec")
        self.log.info("MultiTrackRecorder Initialized")

    def addVideoTrack(self, port, id, name):
        track = {"id": int(id), "name": str(name), "port": int(port)}
        self.videotracks.append(track)
        self.log.info("Added Videotrack {name}".format(name=name))
        self.log.debug("Track: " + str(track))

    def addAudioTrack(self, id, name):
        track = {"id": int(id), "name": str(name)}
        self.audiotracks.append(track)
        self.log.info("Added Audiotrack {name}".format(name=name))
        self.log.debug("Track: " + str(track))

    def startRecording(self):

