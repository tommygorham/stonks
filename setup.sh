#!/bin/bash
# setup_venv.sh - Virtual Environment Setup Script for Unix/Linux

ACTION=${1:-"setup"}
VENV_NAME=${2:-"venv"}

create_venv() {
    local name=$1
    echo "Creating virtual environment: $name"

    # Check if Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python not found. Please install Python and add it to your PATH."
        exit 1
    fi

    echo "Found Python: $($PYTHON_CMD --version)"

    # Check Python version compatibility
    version_output=$($PYTHON_CMD --version 2>&1)
    if [[ $version_output =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
        major=${BASH_REMATCH[1]}
        minor=${BASH_REMATCH[2]}

        if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 7 ]); then
            echo "Warning: Python $major.$minor detected. Python 3.7+ is recommended for best compatibility."
        fi
    fi

    # Remove existing virtual environment if it exists
    if [ -d "$name" ]; then
        echo "Removing existing virtual environment..."
        rm -rf "$name" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "Error: Could not remove existing virtual environment. Please close any applications using it and try again."
            echo "You may need to run with sudo or check file permissions."
            exit 1
        fi
        echo "Existing virtual environment removed."
    fi

    # Create virtual environment
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv "$name"

    if [ $? -eq 0 ]; then
        echo "Virtual environment created successfully!"
        echo "To activate the virtual environment, run:"
        echo "  source $name/bin/activate"
        echo "Then install dependencies with:"
        echo "  pip install -r requirements.txt"
    else
        echo "Error: Failed to create virtual environment."
        echo "Possible solutions:"
        echo "1. Check file permissions"
        echo "2. Ensure you have write access to the current directory"
        echo "3. Try creating the virtual environment in a different location"
        echo "4. Check if antivirus is blocking the operation"
        exit 1
    fi
}

activate_venv() {
    local name=$1
    local activate_script="$name/bin/activate"

    if [ -f "$activate_script" ]; then
        echo "Activating virtual environment: $name"
        source "$activate_script"
    else
        echo "Error: Virtual environment '$name' not found."
        echo "Run './setup.sh create' to create a virtual environment."
        exit 1
    fi
}

install_deps() {
    local name=$1
    local activate_script="$name/bin/activate"

    if [ -f "$activate_script" ]; then
        echo "Installing dependencies in virtual environment: $name"
        source "$activate_script"

        # Upgrade pip first (best practice)
        echo "Upgrading pip..."
        python -m pip install --upgrade pip

        echo "Installing project dependencies..."
        pip install -r requirements.txt

        if [ $? -eq 0 ]; then
            echo "Dependencies installed successfully!"
        else
            echo "Error: Failed to install dependencies."
            exit 1
        fi
    else
        echo "Error: Virtual environment '$name' not found."
        exit 1
    fi
}

remove_venv() {
    local name=$1

    if [ -d "$name" ]; then
        echo "Removing virtual environment: $name"
        rm -rf "$name"
        echo "Virtual environment removed successfully!"
    else
        echo "Virtual environment '$name' not found."
    fi
}

# Main script logic
case "$ACTION" in
    "create")
        create_venv "$VENV_NAME"
        ;;
    "activate")
        activate_venv "$VENV_NAME"
        ;;
    "install")
        install_deps "$VENV_NAME"
        ;;
    "remove")
        remove_venv "$VENV_NAME"
        ;;
    "setup")
        create_venv "$VENV_NAME"
        install_deps "$VENV_NAME"
        echo ""
        echo "Setup complete! To activate the virtual environment, run:"
        echo "  source $VENV_NAME/bin/activate"
        ;;
    *)
        echo "Usage: ./setup.sh [Action] [VenvName]"
        echo "Actions:"
        echo "  create   - Create a new virtual environment"
        echo "  activate - Activate an existing virtual environment"
        echo "  install  - Install dependencies in virtual environment"
        echo "  remove   - Remove virtual environment"
        echo "  setup    - Create and install dependencies (default)"
        echo "Example: ./setup.sh setup"
        ;;
esac
