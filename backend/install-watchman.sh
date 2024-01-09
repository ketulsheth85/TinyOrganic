#!/usr/bin/env sh

wget https://github.com/facebook/watchman/releases/download/v2021.07.19.00/watchman-v2021.07.19.00-linux.zip
unzip watchman-v2021.07.19.00-linux.zip
mkdir -p /usr/local/lib /usr/local/bin /usr/local/var/run/watchman
cp watchman-v2021.07.19.00-linux/bin/* /usr/local/bin
cp watchman-v2021.07.19.00-linux/lib/* /usr/local/lib
chmod 755 /usr/local/bin/watchman
chmod 777 /usr/local/var/run/watchman
mkdir -p /var/run/watchman/root-state
