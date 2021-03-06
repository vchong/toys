#!/bin/bash

96btool pull --pipe | \
96btool filter \
	--since 'next friday -11 days' \
	--until 'next friday -5 days' \
	--user vchong | \
96btool weekly

96btool pull --pipe | \
96btool filter \
	--since 'next friday -11 days' \
	--until 'next friday -5 days' \
	--user vchong | \
96btool worklog --time-spent 10h

# NOT victor.chong@linaro.org/token
ldtstool fetch --since 'next friday -11 days' | \
ldtstool filter --until 'next friday -5 days' --assignee victor.chong@linaro.org | \
ldtstool weekly

ldtstool fetch --since 'next friday -11 days' | \
ldtstool filter --until 'next friday -5 days' --assignee victor.chong@linaro.org | \
ldtstool worklog --time-spent 10h

glimpse weekly assignee = victor.chong@linaro.org > wkly.txt
