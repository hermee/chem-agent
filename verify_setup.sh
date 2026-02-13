#!/bin/bash
# Verify system setup for Reactome LNP Agent

set -e

echo "🔍 Verifying Reactome LNP Agent Setup..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 found: $($1 --version 2>&1 | head -n1)"
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

check_python_package() {
    if python3.12 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python package '$1' installed"
    else
        echo -e "${RED}✗${NC} Python package '$1' not found"
        return 1
    fi
}

echo "📦 System Dependencies:"
check_command python3.12 || true
check_command node || true
check_command npm || true
check_command cargo || true
check_command rustc || true
check_command uv || true
check_command aws || true

echo ""
echo "🐍 Python Environment:"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    source .venv/bin/activate
    check_python_package rdkit || true
    check_python_package fastapi || true
    check_python_package langchain || true
    deactivate
else
    echo -e "${RED}✗${NC} Virtual environment not found. Run: uv sync"
fi

echo ""
echo "🌐 Frontend Dependencies:"
if [ -d "src/frontend/reactome-ui/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node modules installed"
else
    echo -e "${RED}✗${NC} Node modules not found. Run: cd src/frontend/reactome-ui && npm install"
fi

echo ""
echo "⚙️  Configuration:"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    if grep -q "AWS_REGION" .env; then
        echo -e "${GREEN}✓${NC} AWS_REGION configured"
    else
        echo -e "${YELLOW}⚠${NC} AWS_REGION not set in .env"
    fi
else
    echo -e "${RED}✗${NC} .env file not found. Copy from .env.example"
fi

echo ""
echo "🔑 AWS Credentials:"
if aws sts get-caller-identity &>/dev/null; then
    echo -e "${GREEN}✓${NC} AWS credentials valid"
    aws sts get-caller-identity --query 'Account' --output text | xargs echo "   Account:"
else
    echo -e "${RED}✗${NC} AWS credentials not configured or invalid"
fi

echo ""
echo "🎯 Ports:"
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $1 is in use"
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
    fi
}
check_port 8000 || true
check_port 4200 || true
check_port 8001 || true

echo ""
echo "📁 Project Structure:"
[ -d "src/backend" ] && echo -e "${GREEN}✓${NC} Backend directory exists" || echo -e "${RED}✗${NC} Backend directory missing"
[ -d "src/frontend/reactome-ui" ] && echo -e "${GREEN}✓${NC} Frontend directory exists" || echo -e "${RED}✗${NC} Frontend directory missing"
[ -d "data" ] && echo -e "${GREEN}✓${NC} Data directory exists" || echo -e "${RED}✗${NC} Data directory missing"

echo ""
echo "✅ Verification complete!"
echo ""
echo "Next steps:"
echo "  1. If any checks failed, see SETUP.md for installation instructions"
echo "  2. Run './run.sh' to start the application"
echo "  3. Access the UI at http://localhost:4200"
