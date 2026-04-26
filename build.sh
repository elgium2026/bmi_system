#!/usr/bin/env bash

cd bmi_system

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate