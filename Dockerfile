FROM python:3.12.3-alpine

LABEL name="Python Blocklist Updater" \
      description="Python Blocklist Updater" \
      url="https://github.com/dmachard/docker-blocklist-updater" \
      maintainer="d.machard@gmail.com"

WORKDIR /home/updater
COPY . /home/updater/

RUN apk update \
    && apk add --no-cache gcc alpine-sdk python3-dev \
    && adduser -D updater \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

USER updater

ENTRYPOINT ["python", "-c", "import blocklist_updater as lib; lib.start_updater();"]