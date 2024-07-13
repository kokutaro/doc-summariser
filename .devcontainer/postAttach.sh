#!/bin/sh

cd `dirname $0`
cd ..
sudo chown -R user:user ~/.config/gcloud
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
pip install -r ../requirements.txt