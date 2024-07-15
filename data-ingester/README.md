# Overview

This sample project provides a mechanism to SSH into Snellius and trigger a job that 
lists all files available for a given day and stores them as a json.


# Snellius setup

Install project on snellius with:

```
git clone https://github.com/mycostreams/amf-track-scratch.git
```

Configure the `rclone` on snellius with a `swift` remote. For example, the following to `~/$USER/.config/rclone/rclone.conf`

```bash
[swift]
type = swift
env_auth = true
```

# Run the cron worker

Before running ensure that you have ssh'd into Snellius locally. This ensures that it is in your known hosts.  This file is mounted is mounted as a volume into the docker container.


Create a .env file and enter your Surf username/password.
```bash
cp .env.example .env
```


To run the cron worker run the following:
```bash
docker compose up
```
