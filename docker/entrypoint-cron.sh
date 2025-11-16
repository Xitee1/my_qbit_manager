#!/bin/bash
set -e

# Create cron schedule from environment variable
echo "${CRON_SCHEDULE} cd /app && python -m my_qbit_manager.main >> /app/logs/cron.log 2>&1" > /etc/cron.d/qbit-manager

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/qbit-manager

# Apply cron job
crontab /etc/cron.d/qbit-manager

# Create the log file to be able to run tail
touch /app/logs/cron.log

# Start cron and tail the log file
cron && tail -f /app/logs/cron.log
