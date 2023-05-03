#!/bin/bash

# Start the bot in the background
python abominable-Intelligence/abominable_intelligence.py &

# Wait for a few seconds for the bot to start up
sleep 5

# Check if the bot is still running
if pgrep -f "python abominable-Intelligence/abominable_intelligence.py" >/dev/null
then
    echo "::set-output name=status::success"
else
    echo "::set-output name=status::failure"
    echo "Error: Bot failed to start"
    exit 1
fi

# Wait for a few seconds for the bot to run
sleep 5

# Stop the bot
pkill -f "python abominable-Intelligence/abominable_intelligence.py"

# Check if the bot has stopped
if pgrep -f "python abominable-Intelligence/abominable_intelligence.py" >/dev/null
then
    echo "::set-output name=status::failure"
    echo "Error: Bot failed to stop"
    exit 1
else
    echo "::set-output name=status::success"
fi

exit 0

