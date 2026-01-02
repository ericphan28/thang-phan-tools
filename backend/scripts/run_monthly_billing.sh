#!/bin/bash
# Monthly billing cron job
# Add to crontab: 0 0 1 * * /path/to/run_monthly_billing.sh

cd "$(dirname "$0")/../"
source venv/bin/activate 2>/dev/null || true

echo "[$(date)] Running monthly billing job..."
python -m app.jobs.monthly_billing
echo "[$(date)] Monthly billing job completed"
