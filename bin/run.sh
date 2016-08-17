#!/bin/bash

python3 glimpse weekly assignee = victor.chong@linaro.org > wkly.txt
printf "\n## Progress\n\n" >> wkly.txt
python3 ldtstool fetch | \
	python3 ldtstool filter --assignee victor.chong@linaro.org | \
	python3 ldtstool weekly >> wkly.txt
printf "\n## Progress\n\n" >> wkly.txt
python3 96btool fetch | \
	python3 96btool filter | \
	python3 96btool weekly >> wkly.txt
