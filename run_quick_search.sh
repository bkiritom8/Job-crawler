#!/bin/bash
# Quick search script for Bhargav

echo "Starting MLOps/DevOps job search..."

python main.py \
  --resume my_resume.txt \
  --roles "MLOps Engineer,DevOps Engineer,ML Infrastructure Engineer,Platform Engineer,Cloud Engineer" \
  --remote \
  --max-jobs 60 \
  --min-score 65 \
  --top-n 15 \
  --output my_matches.json

echo ""
echo "Search complete! Results saved to my_matches.json"
