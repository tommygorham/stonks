# setup_venv.ps1 - Virtual Environment Setup Script for Windows

param(
    [string]$Action = "create",
    [string]$VenvName = "venv"
)

function Create-VirtualEnvironment {
    param([string]$Name)

    Write-Host "Creating virtual environment: $Name" -ForegroundColor Green

    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Found Python: $pythonVersion" -ForegroundColor Green

        # Check Python version compatibility
        $versionOutput = python --version 2>&1
        if ($versionOutput -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
                Write-Host "Warning: Python $major.$minor detected. Python 3.7+ is recommended for best compatibility." -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "Error: Python not found. Please install Python and add it to your PATH." -ForegroundColor Red
        exit 1
    }

    # Remove existing virtual environment if it exists
    if (Test-Path $Name) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        try {
            Remove-Item -Recurse -Force $Name -ErrorAction Stop
            Write-Host "Existing virtual environment removed." -ForegroundColor Green
        } catch {
            Write-Host "Error: Could not remove existing virtual environment. Please close any applications using it and try again." -ForegroundColor Red
            Write-Host "You may need to run PowerShell as Administrator." -ForegroundColor Yellow
            exit 1
        }
    }

    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv $Name
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Virtual environment created successfully!" -ForegroundColor Green
            Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
            Write-Host "  .\$Name\Scripts\Activate.ps1" -ForegroundColor Cyan
            Write-Host "Then install dependencies with:" -ForegroundColor Yellow
            Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
        } else {
            throw "Virtual environment creation failed"
        }
    } catch {
        Write-Host "Error: Failed to create virtual environment." -ForegroundColor Red
        Write-Host "Possible solutions:" -ForegroundColor Yellow
        Write-Host "1. Run PowerShell as Administrator" -ForegroundColor White
        Write-Host "2. Check if antivirus is blocking the operation" -ForegroundColor White
        Write-Host "3. Try creating the virtual environment in a different location" -ForegroundColor White
        Write-Host "4. Ensure you have write permissions to the current directory" -ForegroundColor White
        exit 1
    }
}

function Activate-VirtualEnvironment {
    param([string]$Name)

    $activateScript = ".\$Name\Scripts\Activate.ps1"

    if (Test-Path $activateScript) {
        Write-Host "Activating virtual environment: $Name" -ForegroundColor Green
        & $activateScript
    } else {
        Write-Host "Error: Virtual environment '$Name' not found." -ForegroundColor Red
        Write-Host "Run '.\setup.ps1 create' to create a virtual environment." -ForegroundColor Yellow
        exit 1
    }
}

function Install-Dependencies {
    param([string]$Name)

    $activateScript = ".\$Name\Scripts\Activate.ps1"

    if (Test-Path $activateScript) {
        Write-Host "Installing dependencies in virtual environment: $Name" -ForegroundColor Green
        & $activateScript

        # Upgrade pip first (best practice)
        Write-Host "Upgrading pip..." -ForegroundColor Yellow
        python -m pip install --upgrade pip

        Write-Host "Installing project dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Dependencies installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Error: Virtual environment '$Name' not found." -ForegroundColor Red
        exit 1
    }
}

function Remove-VirtualEnvironment {
    param([string]$Name)

    if (Test-Path $Name) {
        Write-Host "Removing virtual environment: $Name" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $Name
        Write-Host "Virtual environment removed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Virtual environment '$Name' not found." -ForegroundColor Yellow
    }
}

# Main script logic
switch ($Action.ToLower()) {
    "create" {
        Create-VirtualEnvironment -Name $VenvName
    }
    "activate" {
        Activate-VirtualEnvironment -Name $VenvName
    }
    "install" {
        Install-Dependencies -Name $VenvName
    }
    "remove" {
        Remove-VirtualEnvironment -Name $VenvName
    }
    "setup" {
        Create-VirtualEnvironment -Name $VenvName
        Install-Dependencies -Name $VenvName
        Write-Host "`nSetup complete! To activate the virtual environment, run:" -ForegroundColor Green
        Write-Host "  .\$VenvName\Scripts\Activate.ps1" -ForegroundColor Cyan
    }
    default {
        Write-Host "Usage: .\setup.ps1 [Action] [VenvName]" -ForegroundColor Yellow
        Write-Host "Actions:" -ForegroundColor Yellow
        Write-Host "  create   - Create a new virtual environment" -ForegroundColor White
        Write-Host "  activate - Activate an existing virtual environment" -ForegroundColor White
        Write-Host "  install  - Install dependencies in virtual environment" -ForegroundColor White
        Write-Host "  remove   - Remove virtual environment" -ForegroundColor White
        Write-Host "  setup    - Create and install dependencies (default)" -ForegroundColor White
        Write-Host "Example: .\setup.ps1 setup" -ForegroundColor Cyan
    }
}
