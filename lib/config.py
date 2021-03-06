import os.path
import logging
from configparser import ConfigParser
from lib.args import Args
import lib.connection as Connection

__all__ = ['Config']


def getlist(self, section, option):
    return [x.strip() for x in self.get(section, option).split(',')]


def fetchServerConfig(self):
    log = logging.getLogger('Config')
    log.info("reading server-config")

    server_config = Connection.fetchServerConfig()

    log.info("merging server-config %s", server_config)
    self.read_dict(server_config)

ConfigParser.getlist = getlist
ConfigParser.fetchServerConfig = fetchServerConfig

files = [
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 '../default-config.ini'),
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 '../config.ini'),
    '/etc/voctomix/voctorec.ini',
    os.path.expanduser('~/.config/voctomix/voctorec.ini'),
    os.path.expanduser('~/.voctorec.ini'),
]

if Args.ini_file is not None:
    files.append(Args.ini_file)

Config = ConfigParser()
readfiles = Config.read(files)

log = logging.getLogger('ConfigParser')
log.debug('considered config-files: \n%s',
          "\n".join(["\t\t" + os.path.normpath(file) for file in files]))
log.debug('successfully parsed config-files: \n%s',
          "\n".join(["\t\t" + os.path.normpath(file) for file in readfiles]))
