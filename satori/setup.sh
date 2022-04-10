#!/bin/bash
conda env update --file environment.yml
pip install -r requirements.txt
./talkinghead/setup.sh
python -m spacy download en_core_web_md

