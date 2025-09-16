#!/bin/bash

echo $1

# Check if an argument was provided
if [ $# -eq 0 ]; then
    echo "No argument provided."
    exit 1
fi

# Check if the argument is 6 characters long
if [ ${#1} -ne 7 ]; then
    echo "Argument must be exactly 7 characters long."
    exit 1
fi

# Check if the file exists
if [ -e "/home/stations/$1" ]; then
    echo "File /home/stations/$1 exists. Exiting."
    exit 1
fi

echo "|---------------|"
echo "|| || || || || ||"
echo "|| |$1 || ||"
echo "|| || || || || ||"
echo "|---------------|"
echo "Creating jail directory for $1"
echo "Located at /home/stations/$1/home/$1"

mkdir /home/stations/$1
mkdir /home/stations/$1/home

mkdir /home/stations/$1/home/$1
chown $1 /home/stations/$1/home/$1
chgrp sftp_users /home/stations/$1/home/$1
usermod -aG sftp_users $1
