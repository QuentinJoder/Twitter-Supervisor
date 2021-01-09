#!/bin/bash
# Script created to ease my work in PyCharm Community Edition
# '$ ./flask_run.sh develoment' to launch the app in Debug mode
# '$ ./flask_run.sh production' to launch the app in regular mode
export FLASK_APP=twittersupervisor
export FLASK_ENV=$1
flask run
