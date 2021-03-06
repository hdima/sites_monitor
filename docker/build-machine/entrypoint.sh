#!/bin/sh

uid=$1
gid=$2

shift 2

export HOME="/home/build"

groupadd -g $gid build
useradd -c "Build user" -d "$HOME" -u $uid -g $gid build

# Copy skeleton files manually
cp -r /etc/skel/. /home/build/
find /home/build -maxdepth 1 -user root -exec chown build:build '{}' \;

exec sudo -n -E -u \#$uid -g \#$gid -s -- "$@"
