# buildbot

Automated, containerized builds for grow projects.

NOTE: this app is under development.

## Running locally

```bash
./utils/setup
./utils/run
./utils/run_worker
```

A local redis server is required. You can `brew install redis` on Mac.

## Deploying new images

Building and pushing new Docker images:

```bash
./prod/build
./prod/push_images
```

## Setup on Google Compute Engine

First time setup:

Make sure you have run `gcloud auth login` for the correct account and
`gcloud config set project PROJECT-NAME` with the correct project name.

```bash
./prod/initialize
```

This will create a static IP, an SSD persistent disk called "buildbot-data", and a GCE
instance called "buildbot-master". The master-startup.sh script is set as a metadata startup script.
It uses GCE safe_format_and_mount to mount the `buildbot-data` disk on `/data` (which is where the
Redis container will write data). If you want to use a different Redis host, you can customize
containers.yaml and set the `REDIS_HOST`, `REDIS_PORT`, and/or `REDIS_DB` environment variables
and to remove the redis container.

Right now, you must manually SSH into the machine and modify `/etc/default/kubelet` to add the
`--allow_privileged=true` flag.

Finally, currently this app uses HTTP Basic Auth, so you must set a GCE instance metadata key
called `buildbot-password` or customize containers.yaml and set the `BUILDBOT_PASSWORD` env var.

## Deploy updates to GCE instance

```
./prod/deploy_update
```
