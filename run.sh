#!/bin/bash

# --- Color Definitions for Premium Look ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

# Default ports
PORT_VIEW=8060
PORT_COMPARE=8050
CUSTOM_PORT=""

# Print a nice banner
print_banner() {
    clear
    echo -e "${CYAN}${BOLD}================================================================${NC}"
    echo -e "${BLUE}${BOLD}   🔮  TWENTE CRYSTAL STRUCTURE VISUALIZER & COMPARISON TOOL  🔮${NC}"
    echo -e "${CYAN}${BOLD}================================================================${NC}"
}

# Print help/usage info
show_help() {
    echo -e "${BOLD}Usage:${NC} $0 [options]"
    echo ""
    echo -e "${BOLD}Options:${NC}"
    echo -e "  ${GREEN}-s, --setup${NC}        Setup virtual environment, install dependencies, and run"
    echo -e "  ${GREEN}-v, --view${NC}         Run structure.py to view a single crystal structure"
    echo -e "  ${GREEN}-c, --compare${NC}      Run comparison.py to compare multiple crystal structures"
    echo -e "  ${GREEN}-p, --port PORT${NC}    Configure a custom port to run the application on"
    echo -e "  ${GREEN}-h, --help${NC}         Display this help message"
    echo ""
    echo -e "If no options are provided, the script launches in ${BOLD}Interactive Mode${NC}."
}

# Find a suitable Python 3 interpreter (>= 3.10) that can create venvs
find_python() {
    # List of candidate interpreters to try, in priority order
    local candidates=(
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
        "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"
        "/opt/homebrew/bin/python3"
        "/usr/local/bin/python3"
        "/usr/bin/python3"
    )
    # Also add any python3.XX variants found in PATH
    for ver in 13 12 11 10; do
        local p
        p=$(command -v "python3.${ver}" 2>/dev/null) && candidates+=("$p")
    done

    for candidate in "${candidates[@]}"; do
        if [ -x "$candidate" ]; then
            # Check version >= 3.10
            local ver
            ver=$("$candidate" -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}")' 2>/dev/null) || continue
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ] 2>/dev/null; then
                # Quick test: can it create a venv?
                local tmpdir
                tmpdir=$(mktemp -d)
                if "$candidate" -m venv "$tmpdir/test_venv" 2>/dev/null; then
                    rm -rf "$tmpdir"
                    echo "$candidate"
                    return 0
                fi
                rm -rf "$tmpdir"
            fi
        fi
    done
    return 1
}

# Perform validation & setup of virtual environment
setup_venv() {
    echo -e "\n${YELLOW}${BOLD}[*] Setting up Python Virtual Environment...${NC}"
    
    # Check if python3 is installed at all
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}${BOLD}[ERROR] python3 is not installed or not in PATH. Please install Python 3 (3.10+ recommended).${NC}"
        read -p "Press Enter to return to the menu..."
        return 1
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${BLUE}[INFO] Searching for a suitable Python interpreter...${NC}"
        
        PYTHON_BIN=$(find_python)
        if [ -n "$PYTHON_BIN" ]; then
            PYTHON_VER=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            echo -e "${GREEN}[INFO] Using Python $PYTHON_VER ($PYTHON_BIN)${NC}"
            echo -e "${BLUE}[INFO] Creating new virtual environment at $VENV_DIR...${NC}"
            "$PYTHON_BIN" -m venv "$VENV_DIR" || { echo -e "${RED}[ERROR] Failed to create virtual environment.${NC}"; read -p "Press Enter to return to the menu..."; return 1; }
        else
            # Fallback: create venv without pip and bootstrap pip manually
            PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            echo -e "${YELLOW}[WARN] No standard Python could create a venv with pip. Falling back to manual bootstrap...${NC}"
            echo -e "${GREEN}[INFO] Using Python $PYTHON_VER ($(command -v python3))${NC}"
            echo -e "${BLUE}[INFO] Creating virtual environment without pip...${NC}"
            python3 -m venv --without-pip "$VENV_DIR" || { echo -e "${RED}[ERROR] Failed to create virtual environment.${NC}"; read -p "Press Enter to return to the menu..."; return 1; }
            echo -e "${BLUE}[INFO] Bootstrapping pip via get-pip.py...${NC}"
            curl -sS https://bootstrap.pypa.io/get-pip.py -o "$VENV_DIR/get-pip.py" || { echo -e "${RED}[ERROR] Failed to download get-pip.py. Check your internet connection.${NC}"; rm -rf "$VENV_DIR"; read -p "Press Enter to return to the menu..."; return 1; }
            "$VENV_DIR/bin/python" "$VENV_DIR/get-pip.py" --quiet || { echo -e "${RED}[ERROR] Failed to install pip.${NC}"; rm -rf "$VENV_DIR"; read -p "Press Enter to return to the menu..."; return 1; }
            rm -f "$VENV_DIR/get-pip.py"
        fi
    else
        echo -e "${GREEN}[INFO] Virtual environment directory already exists.${NC}"
    fi
    
    echo -e "${BLUE}[INFO] Upgrading pip...${NC}"
    "$VENV_DIR/bin/pip" install --upgrade pip || { echo -e "${RED}[ERROR] Failed to upgrade pip.${NC}"; read -p "Press Enter to return to the menu..."; return 1; }
    
    if [ -f "$REQ_FILE" ]; then
        echo -e "${BLUE}[INFO] Installing dependencies from $REQ_FILE...${NC}"
        "$VENV_DIR/bin/pip" install -r "$REQ_FILE" || { echo -e "${RED}[ERROR] Failed to install dependencies from $REQ_FILE.${NC}"; read -p "Press Enter to return to the menu..."; return 1; }
    else
        echo -e "${YELLOW}[WARN] requirements.txt not found. Installing default packages...${NC}"
        "$VENV_DIR/bin/pip" install dash ase pymatgen crystal-toolkit || { echo -e "${RED}[ERROR] Failed to install default packages.${NC}"; read -p "Press Enter to return to the menu..."; return 1; }
        # Save state
        "$VENV_DIR/bin/pip" freeze > "$REQ_FILE"
    fi
    
    # Activate virtual environment
    if [ -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${BLUE}[INFO] Activating virtual environment...${NC}"
        source "$VENV_DIR/bin/activate"
    fi
    
    echo -e "${GREEN}${BOLD}[SUCCESS] Virtual environment setup completed successfully and activated!${NC}\n"
}

# Verify if virtual environment is ready; prompt user to create it if not
check_venv() {
    if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/python" ]; then
        echo -e "${YELLOW}${BOLD}[!] Virtual environment not found or incomplete.${NC}"
        read -p "Would you like to set it up now? [Y/n]: " choice
        choice=${choice:-Y}
        case "$choice" in
            [yY][eE][sS]|[yY])
                setup_venv
                ;;
            *)
                echo -e "${RED}${BOLD}[ERROR] A valid virtual environment is required to run the scripts. Exiting.${NC}"
                exit 1
                ;;
        esac
    else
        # If it already exists, activate it
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
        fi
    fi
}

# Launch structure.py
run_view() {
    check_venv
    local active_port=${CUSTOM_PORT:-$PORT_VIEW}
    echo -e "\n${GREEN}${BOLD}[+] Launching Crystal Structure Visualizer (structure.py)...${NC}"
    echo -e "${BLUE}[*] Running on: ${BOLD}http://127.0.0.1:$active_port${NC}"
    echo -e "${YELLOW}[*] Press Ctrl+C to terminate the server.${NC}\n"
    
    PORT=$active_port "$VENV_DIR/bin/python" "$SCRIPT_DIR/structure.py"
    read -p "Press Enter to return to the menu..."
}

# Launch comparison.py
run_compare() {
    check_venv
    local active_port=${CUSTOM_PORT:-$PORT_COMPARE}
    echo -e "\n${GREEN}${BOLD}[+] Launching Multi-Structure Comparison Toolkit (comparison.py)...${NC}"
    echo -e "${BLUE}[*] Running on: ${BOLD}http://127.0.0.1:$active_port${NC}"
    echo -e "${YELLOW}[*] Press Ctrl+C to terminate the server.${NC}\n"
    
    PORT=$active_port "$VENV_DIR/bin/python" "$SCRIPT_DIR/comparison.py"
    read -p "Press Enter to return to the menu..."
}

# Set a custom port
configure_port() {
    read -p "Enter custom port number (1024-65535): " input_port
    if [[ "$input_port" =~ ^[0-9]+$ ]] && [ "$input_port" -ge 1024 ] && [ "$input_port" -le 65535 ]; then
        CUSTOM_PORT=$input_port
        echo -e "${GREEN}[✓] Port configured to: $CUSTOM_PORT${NC}"
    else
        echo -e "${RED}[ERROR] Invalid port number. Must be an integer between 1024 and 65535.${NC}"
    fi
    read -p "Press Enter to return to the menu..."
}

# Parse Command Line Options
ACTION=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--view)
            ACTION="view"
            shift
            ;;
        -c|--compare)
            ACTION="compare"
            shift
            ;;
        -p|--port)
            if [[ "$2" =~ ^[0-9]+$ ]] && [ "$2" -ge 1024 ] && [ "$2" -le 65535 ]; then
                CUSTOM_PORT="$2"
            else
                echo -e "${RED}[ERROR] Invalid port value '$2'. Using default port.${NC}"
            fi
            shift 2
            ;;
        -s|--setup)
            ACTION="setup"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR] Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Execute command line action if specified
if [ -n "$ACTION" ]; then
    case "$ACTION" in
        view)
            run_view
            ;;
        compare)
            run_compare
            ;;
        setup)
            setup_venv
            if [ $? -eq 0 ]; then
                run_view
            fi
            ;;
    esac
    exit 0
fi

# Interactive Menu Loop
while true; do
    print_banner
    echo -e "   ${BOLD}Configure & Run Applications:${NC}"
    echo -e "   -----------------------------"
    echo -e "   ${CYAN}1)${NC} Create Virtual Environment & Install Dependencies ${MAGENTA}(.venv)${NC}"
    echo -e "   ${CYAN}2)${NC} View Single Structure ${BLUE}(runs structure.py on port ${CUSTOM_PORT:-$PORT_VIEW})${NC}"
    echo -e "   ${CYAN}3)${NC} Compare Multiple Structures ${BLUE}(runs comparison.py on port ${CUSTOM_PORT:-$PORT_COMPARE})${NC}"
    echo -e "   ${CYAN}4)${NC} Configure Custom Port ${YELLOW}(current: ${CUSTOM_PORT:-defaults [View:$PORT_VIEW, Compare:$PORT_COMPARE]})${NC}"
    echo -e "   ${CYAN}5)${NC} Exit"
    echo -e "${CYAN}================================================================${NC}"
    read -p "Select an option [1-5]: " menu_choice
    
    case "$menu_choice" in
        1)
            setup_venv
            if [ $? -eq 0 ]; then
                run_view
            fi
            ;;
        2)
            run_view
            ;;
        3)
            run_compare
            ;;
        4)
            configure_port
            ;;
        5)
            echo -e "${GREEN}Thank you for using Twente Crystal Visualizer & Comparison CLI! Goodbye.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR] Invalid selection. Please choose an option from 1 to 5.${NC}"
            sleep 2
            ;;
    esac
done
