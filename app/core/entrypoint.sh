#!/bin/bash
#gunicorn -b 0.0.0.0:10500 --reload --access-logfile sdc-gunicorn_access.log --error-logfile sdc-gunicorn_error.log --log-level debug --timeout 120 sdc-backup-api &
python speedbot.py &