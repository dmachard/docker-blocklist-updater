FROM python:3.12.1-alpine

LABEL name="Python Blocklist Updater" \
      description="Python Blocklist Updater" \
      url="https://github.com/dmachard/docker-blocklist-updater" \
      maintainer="d.machard@gmail.com"

WORKDIR /home/monitor
COPY . /home/monitor/

RUN apk update \
    && adduser -D monitor \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

USER monitor

ENTRYPOINT ["python", "-c", "import publicaddr_ovhcloud as lib; lib.start_monitor();"]