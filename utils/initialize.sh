#!/bin/bash

VMNAME=webreview-buildbot-new

echo "Deploying $VMNAME ..."
gcloud compute instances create \
  $VMNAME \
  --image container-vm \
  --machine-type n1-standard-1 \
  --scopes https://www.googleapis.com/auth/gerritcodereview,https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/computeaccounts.readonly,https://www.googleapis.com/auth/logging.write \
  --zone us-central1-a \
  --boot-disk-type pd-ssd \
  --boot-disk-size 200GB
