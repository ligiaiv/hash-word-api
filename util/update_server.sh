#!/bin/bash

rsync -rav --include='*/' --include='*.py' --include='*.sh' --exclude='*' --exclude='.git' ../ root@XXX.XXX.XXX.XXX:/root/word_api_v3
