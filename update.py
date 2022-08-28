import os
import sys
import time
import shutil
import hashlib
import time
from datetime import datetime
import logging
import requests


# CONFIGURATION
UPDATE_TO_SNAPSHOT = False
INSTANCE_NAME = "minecraft"
MINECRAFT_HOME = os.path.dirname(os.path.abspath(__file__))
APP_HOME = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = APP_HOME + 'world_backups' + INSTANCE_NAME
LOG_FILENAME = APP_HOME + 'logs/auto_updater_' + INSTANCE_NAME + '.log'
RAM_INITIAL = '512m'
RAM_MAX = '2g'
MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"


# Read alternate configuration from command line arguments
if len(sys.argv) > 1:
    for x in range(len(sys.argv)-1):
        # Check for whether the snapshot arg was given
        if sys.argv[x].startswith("-") and sys.argv[x] == "-snapshot":
            UPDATE_TO_SNAPSHOT = True
        # Look for flags, but skip it if no arg was provided for the flag
        elif sys.argv[x].startswith("-") and x != len(sys.argv)-1:
            # Get the flag and value
            flag = sys.argv[x][1:]
            value = sys.argv[x+1]
            # Process the flag
            match sys.argv[x][1:]:
                case "name":
                    INSTANCE_NAME = value
                case "ram_max":
                    RAM_MAX = value
                case "ram_initial":
                    RAM_INITIAL = value
                case "path":
                    MINECRAFT_HOME = value
        # Update paths
        BACKUP_DIR = os.path.join(APP_HOME, 'world_backups', INSTANCE_NAME)
        LOG_FILENAME = os.path.join(APP_HOME, 'logs/auto_updater_' + INSTANCE_NAME + '.log')

# Set up logging
if not os.path.exists(os.path.join(APP_HOME, 'logs')):
    os.makedirs(os.path.join(APP_HOME, 'logs'))
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
# Move to the minecraft directory
os.chdir(MINECRAFT_HOME)

# retrieve version manifest
response = requests.get(MANIFEST_URL)
data = response.json()

if UPDATE_TO_SNAPSHOT:
    minecraft_ver = data['latest']['snapshot']
else:
    minecraft_ver = data['latest']['release']

# get checksum of running server
if os.path.exists('minecraft_server.jar'):
    sha = hashlib.sha1()
    f = open("minecraft_server.jar", 'rb')
    sha.update(f.read())
    cur_ver = sha.hexdigest()
else:
    cur_ver = ""

for version in data['versions']:
    if version['id'] == minecraft_ver:
        jsonlink = version['url']
        jar_data = requests.get(jsonlink).json()
        jar_sha = jar_data['downloads']['server']['sha1']

        logging.info('Your sha1 is ' + cur_ver + '. Latest version is ' + str(minecraft_ver) + " with sha1 of " + jar_sha)

        if cur_ver != jar_sha:
            logging.info('Updating server...')
            link = jar_data['downloads']['server']['url']
            logging.info('Downloading .jar from ' + link + '...')
            response = requests.get(link)

            if not os.path.exists(os.path.join(APP_HOME, '/tmp/')):
                os.makedirs(os.path.join(APP_HOME, '/tmp/'))
            with open(os.path.join(APP_HOME, '/tmp/minecraft_server.jar'), 'wb') as jar_file:
                jar_file.write(response.content)

            logging.info('Downloaded.')
            os.system('screen -S ' + INSTANCE_NAME + ' -X stuff \'say ATTENTION: Server will shutdown temporarily to update in 30 seconds.^M\'')
            logging.info('Shutting down server in 30 seconds.')

            for i in range(20, 9, -10):
                time.sleep(10)
                os.system('screen -S ' + INSTANCE_NAME + ' -X stuff \'say Shutdown in ' + str(i) + ' seconds^M\'')

            for i in range(9, 0, -1):
                time.sleep(1)
                os.system('screen -S ' + INSTANCE_NAME + ' -X stuff \'say Shutdown in ' + str(i) + ' seconds^M\'')
            time.sleep(1)

            logging.info('Stopping server.')
            os.system('screen -S ' + INSTANCE_NAME + ' -X stuff \'stop^M\'')
            time.sleep(5)
            logging.info('Backing up world...')

            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)

            backupPath = os.path.join(
                BACKUP_DIR,
                "world" + "_backup_" + datetime.now().isoformat().replace(':', '-') + "_sha=" + cur_ver)
            shutil.copytree("world", backupPath)

            logging.info('Backed up world.')
            logging.info('Updating server .jar')

            if os.path.exists('minecraft_server.jar'):
                os.remove('minecraft_server.jar')

            os.rename(os.path.join(APP_HOME, '/tmp/minecraft_server.jar'), 'minecraft_server.jar')
            logging.info('Starting server...')
            os.system('screen -S ' + INSTANCE_NAME + ' -d -m java -Xms' + RAM_INITIAL + ' -Xmx' + RAM_MAX + ' -jar minecraft_server.jar')
        else:
            logging.info('Server is already up to date.')
        break
