#!/bin/bash

start=`date -d'next-friday -11 days' +%Y-%m-%d`
end=`date -d'next-friday -5 days' +%Y-%m-%d`
echo "start = $start"
echo "end = $end"

python3 glimpse weekly assignee = victor.chong@linaro.org > wkly_linux.txt
printf "\n## Progress\n\n" >> wkly_linux.txt
python3 ldtstool fetch --since $start --until $end | \
	python3 ldtstool filter --assignee victor.chong@linaro.org | \
	python3 ldtstool weekly >> wkly_linux.txt
printf "\n## Progress\n\n" >> wkly_linux.txt
python3 96btool fetch --since $start | \
	python3 96btool filter --until $end | \
	python3 96btool weekly >> wkly_linux.txt
