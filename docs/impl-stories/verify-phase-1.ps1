# Phase 1 Verification Script (PowerShell)
# Run this after completing all Phase 1 stories to verify everything works

$ErrorActionPreference = "Continue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Listing Genie - Phase 1 Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Test counters
$Script:Passed = 0
$Script:Failed = 0

# Helper functions
function Pass {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
    $Script:Passed++
}

function Fail {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $Script:Failed++
}

function Warn {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
}

# Check prerequisites
Section "Prerequisites"

if (Test-Path ".env") {
    Pass ".env file exists"
} else {
    Fail ".env file not found (copy from .env.example)"
}

if (Test-Path "app") {
    Pass "app/ directory exists"
} else {
    Fail "app/ directory not found"
}

if (Test-Path "frontend") {
    Pass "frontend/ directory exists"
} else {
    Fail "frontend/ directory not found"
}

# Story 1.1 - FastAPI Backend
Section "Story 1.1 - FastAPI Backend"

if (Test-Path "app\main.py") {
    Pass "app/main.py exists"
} else {
    Fail "app/main.py not found"
}

if (Test-Path "app\config.py") {
    Pass "app/config.py exists"
} else {
    Fail "app/config.py not found"
}

if (Test-Path "app\core\middleware.py") {
    Pass "app/core/middleware.py exists"
} else {
    Fail "app/core/middleware.py not found"
}

if (Test-Path "requirements.txt") {
    Pass "requirements.txt exists"
} else {
    Fail "requirements.txt not found"
}

# Story 1.2 - Database
Section "Story 1.2 - Database Setup"

if (Test-Path "app\models\database.py") {
    Pass "app/models/database.py exists"
} else {
    Fail "app/models/database.py not found"
}

if (Test-Path "app\db\session.py") {
    Pass "app/db/session.py exists"
} else {
    Fail "app/db/session.py not found"
}

# Check for models
if (Test-Path "app\models\database.py") {
    $content = Get-Content "app\models\database.py" -Raw

    if ($content -match "class GenerationSession") {
        Pass "GenerationSession model defined"
    } else {
        Fail "GenerationSession model not found"
    }

    if ($content -match "class SessionKeyword") {
        Pass "SessionKeyword model defined"
    } else {
        Fail "SessionKeyword model not found"
    }

    if ($content -match "class ImageRecord") {
        Pass "ImageRecord model defined"
    } else {
        Fail "ImageRecord model not found"
    }
}

# Story 1.3 - Storage
Section "Story 1.3 - Storage Setup"

if (Test-Path "app\services\storage_service.py") {
    Pass "app/services/storage_service.py exists"
} else {
    Fail "app/services/storage_service.py not found"
}

if (Test-Path "storage") {
    Pass "storage/ directory exists"
} else {
    Warn "storage/ directory will be created on first run"
}

# Story 1.4 - Frontend
Section "Story 1.4 - React Frontend"

if (Test-Path "frontend\package.json") {
    Pass "frontend/package.json exists"
} else {
    Fail "frontend/package.json not found"
}

if (Test-Path "frontend\vite.config.ts") {
    Pass "frontend/vite.config.ts exists"
} else {
    Fail "frontend/vite.config.ts not found"
}

if (Test-Path "frontend\tailwind.config.js") {
    Pass "frontend/tailwind.config.js exists"
} else {
    Fail "frontend/tailwind.config.js not found"
}

if (Test-Path "frontend\src\App.tsx") {
    Pass "frontend/src/App.tsx exists"
} else {
    Fail "frontend/src/App.tsx not found"
}

if (Test-Path "frontend\src\api\client.ts") {
    Pass "frontend/src/api/client.ts exists"
} else {
    Fail "frontend/src/api/client.ts not found"
}

# Story 1.5 - Docker
Section "Story 1.5 - Docker Environment"

if (Test-Path "Dockerfile") {
    Pass "Dockerfile exists"
} else {
    Fail "Dockerfile not found"
}

if (Test-Path "Dockerfile.dev") {
    Pass "Dockerfile.dev exists"
} else {
    Fail "Dockerfile.dev not found"
}

if (Test-Path "docker-compose.yml") {
    Pass "docker-compose.yml exists"
} else {
    Fail "docker-compose.yml not found"
}

if (Test-Path ".dockerignore") {
    Pass ".dockerignore exists"
} else {
    Warn ".dockerignore not found (recommended)"
}

# Runtime tests (if services are running)
Section "Runtime Tests (Optional)"

Write-Host "Checking if services are running..."

# Check backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        Pass "Backend is running on port 8000"

        $healthData = $response.Content | ConvertFrom-Json
        if ($healthData.status -eq "healthy") {
            Pass "Health check returns 'healthy'"
        } else {
            Fail "Health check response unexpected"
        }
    }

    # Test API health endpoint
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2
    $apiHealth = $apiResponse.Content | ConvertFrom-Json
    if ($apiHealth.dependencies) {
        Pass "API health check includes database status"
    } else {
        Fail "API health check missing database status"
    }
} catch {
    Warn "Backend not running (start with: uvicorn app.main:app --reload)"
}

# Check frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2
    if ($frontendResponse.StatusCode -eq 200) {
        Pass "Frontend is running on port 5173"
    }
} catch {
    Warn "Frontend not running (start with: cd frontend && npm run dev)"
}

# Check Docker
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Pass "Docker is installed"

        try {
            $composeVersion = docker-compose --version 2>$null
            if (!$composeVersion) {
                $composeVersion = docker compose version 2>$null
            }
            if ($composeVersion) {
                Pass "Docker Compose is available"
            }
        } catch {
            Warn "Docker Compose not found"
        }
    }
} catch {
    Warn "Docker not installed (optional for development)"
}

# Summary
Section "Verification Summary"

$Total = $Script:Passed + $Script:Failed
$Percentage = if ($Total -gt 0) { [math]::Round(($Script:Passed / $Total) * 100) } else { 0 }

Write-Host ""
Write-Host "Tests Passed: " -NoNewline
Write-Host "$($Script:Passed)" -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline
Write-Host "$($Script:Failed)" -ForegroundColor Red
Write-Host "Success Rate: $Percentage%"
Write-Host ""

if ($Script:Failed -eq 0) {
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "  ✓ Phase 1 Complete!" -ForegroundColor Green
    Write-Host "  Ready for Phase 2 development" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Start services: docker-compose up"
    Write-Host "2. Access frontend: http://localhost:5173"
    Write-Host "3. Access API docs: http://localhost:8000/docs"
    Write-Host "4. Begin Phase 2 stories (Image Generation)"
} else {
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "  ✗ Phase 1 Incomplete" -ForegroundColor Red
    Write-Host "  Fix failed tests above" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
}
