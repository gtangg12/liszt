#!/bin/bash
conda env update --file environment.yml
pip install -r requirements.txt
./talkinghead/setup.sh
./wav2lip/setup.sh

