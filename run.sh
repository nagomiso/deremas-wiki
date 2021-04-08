#!/bin/bash -me
if type poetry > /dev/null 2>&1
then
    :
else
    echo "'poetry' command is required." >&2
    exit 1
fi

poetry run scrapy crawl deremas -o outputs.jsonlines
