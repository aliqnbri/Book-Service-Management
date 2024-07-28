#!/bin/bash

# Run the command to get the PID of the process listening on port 8000
PID=$(lsof -i :8000 -sTCP:LISTEN -t)


# Kill the process with the obtained PID using kill -9
kill -9 $PID

# Print the kill code number
echo "  PID code  $PID Killed !"
