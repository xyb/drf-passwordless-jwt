FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir \
    --trusted-host mirrors.aliyun.com \
    -i http://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt
ADD . /app
EXPOSE 8000
CMD /app/entrypoint.sh
