# What is this?

Docker image to generate and update blocklist

## Docker run

```bash
sudo docker run -d -v ./data:/config --env-file ./env.list --name=blocklist dmachard/blocklist-updater:latest
```

## Docker build

Build docker image

```bash
sudo docker build . --file Dockerfile -t blocklist-updater
```

## Environment variables

| Variables | Description |
| ------------- | ------------- |
| PUBLICADDR_OVHCLOUD_DEBUG | debug mode 1 or 0 |
| PUBLICADDR_OVHCLOUD_EVERY | delay between check, default is 3600s |
| BLOCKLIST_UPDATER_CONFIG_PATH | config file |
| BLOCKLIST_UPDATER_OUTPUT_FORMAT | cdb|raw|hosts |
| BLOCKLIST_UPDATER_OUTPUT_PATH | output file path |

## Run from source

## For developpers

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

```bash
python3 -m pip install -r requirements.txt
python3 example.py -e env.list
```
