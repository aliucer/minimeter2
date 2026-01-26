#!/bin/bash
# test_pipeline.sh
# Automates the MiniMeter API flow: Customer -> Account -> Pipeline
BASE_URL="https://minimeter-api-787646377501.us-central1.run.app"

#BASE_URL="http://127.0.0.1:8000"

echo ">>> 1. Creating Customer..."
# Create customer and capture the response
CUST_RES=$(curl -s -X POST "$BASE_URL/customers" -H "Content-Type: application/json" -d '{"name": "AutoTest User"}')
echo "Response: $CUST_RES"

# Extract ID using python (cross-platform way without installing jq)
CUST_ID=$(echo $CUST_RES | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ">>> Created Customer ID: $CUST_ID"
echo "--------------------------------"

echo ">>> 2. Creating Utility Account..."
ACC_RES=$(curl -s -X POST "$BASE_URL/utility-accounts" -H "Content-Type: application/json" -d "{\"customer_id\": $CUST_ID, \"provider\": \"PG&E\"}")
echo "Response: $ACC_RES"

ACC_ID=$(echo $ACC_RES | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo ">>> Created Account ID: $ACC_ID"
echo "--------------------------------"

echo ">>> 3. Triggering Agent Pipeline..."
JOB_RES=$(curl -s -X POST "$BASE_URL/agent/run?utility_account_id=$ACC_ID")
echo "Response: $JOB_RES"

JOB_ID=$(echo $JOB_RES | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo ">>> Pipeline Started! Job ID: $JOB_ID"
echo "--------------------------------"

echo ">>> 4. Waiting 5 seconds for processing..."
sleep 5

echo ">>> 5. Checking Result..."
RESULT=$(curl -s -X GET "$BASE_URL/agent/result/$JOB_ID")
echo "Final Result:"
echo $RESULT
