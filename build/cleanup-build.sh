#!/bin/bash

# you don't need to run this unless you ran manual build, i.e. sudo pip3 install -r ../source/requirements.txt -t ../source
cd ../source
shopt -s extglob
sudo rm -- *.!(py|txt|yml)
sudo rm -R -- */
sudo rm six.py
cd ..
rm template-export.yml