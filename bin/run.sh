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

python3 glimpse_2wksago weekly assignee = victor.chong@linaro.org > wkly_2wksago.txt
printf "\n## Progress\n\n" >> wkly_2wksago.txt
python3 ldtstool_2wksago fetch | \
	python3 ldtstool_2wksago filter --assignee victor.chong@linaro.org | \
	python3 ldtstool_2wksago weekly >> wkly_2wksago.txt
printf "\n## Progress\n\n" >> wkly_2wksago.txt
python3 96btool_2wksago fetch | \
	python3 96btool_2wksago filter | \
	python3 96btool_2wksago weekly >> wkly_2wksago.txt
