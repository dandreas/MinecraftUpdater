# MinecraftUpdater
This is a python package to automate the updating of your Minecraft server.<br>
It's very annoying to have to download the jar,
ftp it over, stop the server, back up your world, etc. This automates all that. Just clone this into your server. Then run python3 update.py in the new folder. It will check if you have the
latest version of Minecraft using the Mojang provided manfest URL. If your server is out of date, it will download the latest minecraft server jar from the official Mojang S3 bucket. Then using screen it will announce to the server that it is going to restart for an update, and give a 30 seconds countdown before stopping the server. Next it will then backup your world into a new folder, incase something goes wrong. It then updates the server jar and starts the server back up in a screen session so it's in the background.

## Requirements
1. Python 3.10+
2. Python requests library (pip3 install requests)
           
## Configuration
This fork of the code allows 1 clone of this script to be used for several minecraft servers.<br>
The backups and log will be stored in the same folder as update.py:<br>
    1. Logs will be logs/auto_updater_<screenname>.log<br>
    2. Backups are stored in world_backups/<screenname>/<br>
Usage: <br>
`python3 update.py -name <screenname> -ram_max <ram_max> -ram_initial <ram_initial> -path <minecraftpath> -snapshot`<br>
The path variable defaults to ../../<br>
The ram_inital defaults to 512m and ram_max defaults to 2g
If -snapshot is passed, it will get the snapshot release instead of the stable release

## Scheduling Updates
This script is intended to be run as a cron job.
