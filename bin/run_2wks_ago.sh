#!/bin/bash

python3 glimpse_2wks_ago weekly assignee = victor.chong@linaro.org > wkly_2wks_ago.txt
printf "\n## Progress\n\n" >> wkly_2wks_ago.txt
python3 ldtstool_2wks_ago fetch | \
	python3 ldtstool_2wks_ago filter --assignee victor.chong@linaro.org | \
	python3 ldtstool_2wks_ago weekly >> wkly_2wks_ago.txt
printf "\n## Progress\n\n" >> wkly_2wks_ago.txt
python3 96btool_2wks_ago fetch | \
	python3 96btool_2wks_ago filter | \
	python3 96btool_2wks_ago weekly >> wkly_2wks_ago.txt
