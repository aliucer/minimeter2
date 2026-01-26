#!/bin/bash

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Setting up MiniMeter2 Development Environment...${NC}"

# 1. Check for Virtual Environment
if [ ! -d "venv" ]; then
    echo ">>> Creating virtual environment (venv)..."
    python3 -m venv venv
fi

# 2. Activate Virtual Environment
echo ">>> Activating virtual environment..."
source venv/bin/activate

# 3. Install/Update Packages
echo ">>> Installing requirements..."
pip install -r requirements.txt

# 4. Start Application
echo -e "${GREEN}>>> Starting API... (Press Ctrl+C to stop)${NC}"
uvicorn api.main:app --reload
