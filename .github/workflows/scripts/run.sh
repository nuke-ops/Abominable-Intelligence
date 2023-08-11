#!/bin/bash

# Start the bot in the background
python abominable_intelligence/abominable_intelligence.py &

# Capture the PID of the started process
BOT_PID=$!

# Wait for a few seconds for the bot to start up
sleep 5

# Check if the bot is still running
if ps -p $BOT_PID > /dev/null
then
    echo "status=success" >> $GITHUB_ENV
else
    echo "status=failure" >> $GITHUB_ENV
    echo "Error: Bot failed to start"
    exit 1
fi

# Wait for a few seconds for the bot to run
sleep 5

# Stop the bot using the captured PID
kill $BOT_PID

# Wait for the process to fully terminate
wait $BOT_PID

# Check if the bot has stopped
if ps -p $BOT_PID > /dev/null
then
    echo "status=failure" >> $GITHUB_ENV
    echo "Error: Bot failed to stop"
    exit 1
else
    echo "status=success" >> $GITHUB_ENV
fi

exit 0
