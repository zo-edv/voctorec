import subprocess
import datetime
import time
import os

connection = "tcp://localhost:11000"
outputfile = "voctorec_{}.ts".format(datetime.date.today())
print("Using Connection: " + connection)
print("Outputfile: " + outputfile)
print("Starting")
args = """ffmpeg \
    -y -nostdin \
    -i {0} \
    -ac 2 -channel_layout 2 -aspect 16:9 \
    -map 0:v -c:v:0 mpeg2video -pix_fmt:v:0 yuv422p -qscale:v:0 2 -qmin:v:0 2 -qmax:v:0 7 -keyint_min 0 -bf:0 0 -g:0 0 -intra:0 -maxrate:0 90M \
    -map 0:a -c:a:0 mp2 -b:a:0 192k -ac:a:0 2 -ar:a:0 48000 \
    -flags +global_header -flags +ilme+ildct \
    -f mpegts {1}""".format(connection, outputfile)
proc = None
while True:
    if not proc:
        proc = subprocess.Popen(args, shell=True)
    time.sleep(10)
    proc.terminate()