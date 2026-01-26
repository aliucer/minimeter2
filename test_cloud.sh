#!/bin/bash
# test_cloud.sh
# Automates the tests against the LIVE Cloud Run deployment

# Google Cloud Run URL
BASE_URL="https://minimeter-api-787646377501.us-central1.run.app"

echo ">>> TARGET: $BASE_URL"

echo ">>> 1. Creating Customer..."
# Create customer and capture the response
CUST_RES=$(curl -s -X POST "$BASE_URL/customers" -H "Content-Type: application/json" -d '{"name": "Cloud Demo User"}')
echo "Response: $CUST_RES"

# Extract ID 
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

echo ">>> 4. Waiting 10 seconds for cloud processing..."
sleep 10

echo ">>> 5. Checking Result..."
RESULT=$(curl -s -X GET "$BASE_URL/agent/result/$JOB_ID")
echo "Final Result:"
echo $RESULT
