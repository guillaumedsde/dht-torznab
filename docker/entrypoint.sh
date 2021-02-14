#!/bin/sh
python /opt/app/manage.py migrate
python /opt/app/manage.py runserver 0.0.0.0:8080
