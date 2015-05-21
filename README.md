# webreview-buildbot

NOTE: This application is under development.

## Machine setup

Create an Ubunutu Google Compute Engine instance and acquire the Gerrit OAuth scope at instance creation time.

```
gcloud compute instances create \
webreview-builder-1 \
--image ubuntu-14-04 \
--machine-type n1-standard-1 \
--scopes https://www.googleapis.com/auth/gerritcodereview \
--no-boot-disk-auto-delete \
--zone us-central1-a
```

Retrieve the service account; grant access to Gerrit for your service account.

```
gcloud compute instances describe webreview-buildbot-1 | grep email:
````

Install Jenkins, Docker, and OAuth-based Git authentication for Gerrit on the GCE machine.

```
sudo apt-get update
wget -q -O - https://jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get install -f jenkins
wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker jenkins
git clone https://gerrit.googlesource.com/gcompute-tools
./gcompute-tools/git-cookie-authdaemon
sudo service jenkins restart
```

You may verify your Gerrit access with: `git ls-remote https://HOST.googlesource.com/project`

## Jenkins setup

Port forward to your local machine, and access Jenkins at http://localhost:8080.

```
gcloud compute ssh webreview-buildbot-1 --ssh-flag="-L 8080:localhost:8080"
```

Add a parameterized build with the following recipe.

```
#!/bin/bash

git clone https://gerrit.googlesource.com/gcompute-tools
./gcompute-tools/git-cookie-authdaemon
git clone https://$WEBREVIEW_GIT_HOST/$WEBREVIEW_PROJECT $WEBREVIEW_PROJECT
cd $WEBREVIEW_PROJECT
if [ -a "package.json" ]; then
  npm install
fi
if [ -a "bower.json" ]; then
  bower install
fi
if [ -a "gulpfile.js" ]; then
  gulp build
fi
/usr/bin/grow deploy -f review
```
