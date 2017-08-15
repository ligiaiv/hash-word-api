#!/bin/bash

screen -X -S word_api_v3 quit

screen -dmS word_api_v3 python3 __init__.py

screen -r word_api_v3
echo Restarted!!!

exit 0