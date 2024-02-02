#!/usr/bin/env bash

sed -i "s/--workers [[:digit:]]* /--workers ${WORKERS:-2} /" /etc/supervisor/conf.d/app.conf

cd /app/
python manage.py migrate
python manage.py collectstatic --noinput
supervisord --nodaemon -c /etc/supervisor/supervisord.conf
