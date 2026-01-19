#!/bin/bash

# Phase 1 Verification Script
# Run this after completing all Phase 1 stories to verify everything works

set -e  # Exit on any error

echo "========================================="
echo "  Listing Genie - Phase 1 Verification"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

section() {
    echo ""
    echo "========================================="
    echo "  $1"
    echo "========================================="
}

# Check prerequisites
section "Prerequisites"

if [ -f ".env" ]; then
    pass ".env file exists"
else
    fail ".env file not found (copy from .env.example)"
fi

if [ -d "app" ]; then
    pass "app/ directory exists"
else
    fail "app/ directory not found"
fi

if [ -d "frontend" ]; then
    pass "frontend/ directory exists"
else
    fail "frontend/ directory not found"
fi

# Story 1.1 - FastAPI Backend
section "Story 1.1 - FastAPI Backend"

if [ -f "app/main.py" ]; then
    pass "app/main.py exists"
else
    fail "app/main.py not found"
fi

if [ -f "app/config.py" ]; then
    pass "app/config.py exists"
else
    fail "app/config.py not found"
fi

if [ -f "app/core/middleware.py" ]; then
    pass "app/core/middleware.py exists"
else
    fail "app/core/middleware.py not found"
fi

if [ -f "requirements.txt" ]; then
    pass "requirements.txt exists"
else
    fail "requirements.txt not found"
fi

# Story 1.2 - Database
section "Story 1.2 - Database Setup"

if [ -f "app/models/database.py" ]; then
    pass "app/models/database.py exists"
else
    fail "app/models/database.py not found"
fi

if [ -f "app/db/session.py" ]; then
    pass "app/db/session.py exists"
else
    fail "app/db/session.py not found"
fi

# Check for models
if grep -q "class GenerationSession" app/models/database.py 2>/dev/null; then
    pass "GenerationSession model defined"
else
    fail "GenerationSession model not found"
fi

if grep -q "class SessionKeyword" app/models/database.py 2>/dev/null; then
    pass "SessionKeyword model defined"
else
    fail "SessionKeyword model not found"
fi

if grep -q "class ImageRecord" app/models/database.py 2>/dev/null; then
    pass "ImageRecord model defined"
else
    fail "ImageRecord model not found"
fi

# Story 1.3 - Storage
section "Story 1.3 - Storage Setup"

if [ -f "app/services/storage_service.py" ]; then
    pass "app/services/storage_service.py exists"
else
    fail "app/services/storage_service.py not found"
fi

if [ -d "storage" ]; then
    pass "storage/ directory exists"
else
    warn "storage/ directory will be created on first run"
fi

# Story 1.4 - Frontend
section "Story 1.4 - React Frontend"

if [ -f "frontend/package.json" ]; then
    pass "frontend/package.json exists"
else
    fail "frontend/package.json not found"
fi

if [ -f "frontend/vite.config.ts" ]; then
    pass "frontend/vite.config.ts exists"
else
    fail "frontend/vite.config.ts not found"
fi

if [ -f "frontend/tailwind.config.js" ]; then
    pass "frontend/tailwind.config.js exists"
else
    fail "frontend/tailwind.config.js not found"
fi

if [ -f "frontend/src/App.tsx" ]; then
    pass "frontend/src/App.tsx exists"
else
    fail "frontend/src/App.tsx not found"
fi

if [ -f "frontend/src/api/client.ts" ]; then
    pass "frontend/src/api/client.ts exists"
else
    fail "frontend/src/api/client.ts not found"
fi

# Story 1.5 - Docker
section "Story 1.5 - Docker Environment"

if [ -f "Dockerfile" ]; then
    pass "Dockerfile exists"
else
    fail "Dockerfile not found"
fi

if [ -f "Dockerfile.dev" ]; then
    pass "Dockerfile.dev exists"
else
    fail "Dockerfile.dev not found"
fi

if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
else
    fail "docker-compose.yml not found"
fi

if [ -f ".dockerignore" ]; then
    pass ".dockerignore exists"
else
    warn ".dockerignore not found (recommended)"
fi

# Runtime tests (if services are running)
section "Runtime Tests (Optional)"

echo "Checking if services are running..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    pass "Backend is running on port 8000"

    # Test health endpoint
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        pass "Health check returns 'healthy'"
    else
        fail "Health check response unexpected"
    fi

    # Test API health endpoint
    API_HEALTH=$(curl -s http://localhost:8000/api/health)
    if echo "$API_HEALTH" | grep -q "database"; then
        pass "API health check includes database status"
    else
        fail "API health check missing database status"
    fi
else
    warn "Backend not running (start with: uvicorn app.main:app --reload)"
fi

# Check frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    pass "Frontend is running on port 5173"
else
    warn "Frontend not running (start with: cd frontend && npm run dev)"
fi

# Check Docker
if command -v docker &> /dev/null; then
    pass "Docker is installed"

    if docker-compose --version &> /dev/null 2>&1 || docker compose version &> /dev/null 2>&1; then
        pass "Docker Compose is available"
    else
        warn "Docker Compose not found"
    fi
else
    warn "Docker not installed (optional for development)"
fi

# Summary
section "Verification Summary"

TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo ""
echo "Tests Passed: ${GREEN}$PASSED${NC}"
echo "Tests Failed: ${RED}$FAILED${NC}"
echo "Success Rate: ${PERCENTAGE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  ✓ Phase 1 Complete!${NC}"
    echo -e "${GREEN}  Ready for Phase 2 development${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start services: docker-compose up"
    echo "2. Access frontend: http://localhost:5173"
    echo "3. Access API docs: http://localhost:8000/docs"
    echo "4. Begin Phase 2 stories (Image Generation)"
    exit 0
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}  ✗ Phase 1 Incomplete${NC}"
    echo -e "${RED}  Fix failed tests above${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi
