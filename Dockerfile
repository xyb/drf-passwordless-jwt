FROM python:3

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100

# SUPERVISOR
# https://github.com/dockerfile/supervisor/blob/master/Dockerfile
RUN pip install --no-cache-dir supervisor \
  && mkdir /etc/supervisor/ /etc/supervisor/conf.d/ \
  && echo_supervisord_conf > /etc/supervisor/supervisord.conf \
  && sed -i 's/nodaemon=false/nodaemon=true/' /etc/supervisor/supervisord.conf \
  && echo '[include]' >> /etc/supervisor/supervisord.conf \
  && echo 'files = /etc/supervisor/conf.d/*.conf' >> /etc/supervisor/supervisord.conf
VOLUME ["/etc/supervisor/conf.d"]
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]

RUN pip install --no-cache-dir gunicorn py-spy

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir \
    --trusted-host mirrors.aliyun.com \
    -i http://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt
ADD ./supervisor.conf /etc/supervisor/conf.d/app.conf
ADD ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]
ADD . /app
EXPOSE 8000
CMD /app/entrypoint.sh
