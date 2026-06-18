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
    echo -e "  ${GREEN}-v, --view${NC}         Run structure.py to view a single crystal structure"
    echo -e "  ${GREEN}-c, --compare${NC}      Run comparison.py to compare multiple crystal structures"
    echo -e "  ${GREEN}-p, --port PORT${NC}    Configure a custom port to run the application on"
    echo -e "  ${GREEN}-s, --setup${NC}        Setup/rebuild the virtual environment and dependencies"
    echo -e "  ${GREEN}-h, --help${NC}         Display this help message"
    echo ""
    echo -e "If no options are provided, the script launches in ${BOLD}Interactive Mode${NC}."
}

# Perform validation & setup of virtual environment
setup_venv() {
    echo -e "\n${YELLOW}${BOLD}[*] Setting up Python Virtual Environment...${NC}"
    
    # Check if python3 is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}${BOLD}[ERROR] python3 is not installed or not in PATH. Please install Python 3 (3.10+ recommended).${NC}"
        exit 1
    fi
    
    # Check python3 version
    PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${GREEN}[INFO] Found Python version: $PYTHON_VER${NC}"
    
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${BLUE}[INFO] Creating new virtual environment at $VENV_DIR...${NC}"
        python3 -m venv "$VENV_DIR"
    else
        echo -e "${GREEN}[INFO] Virtual environment directory already exists.${NC}"
    fi
    
    echo -e "${BLUE}[INFO] Upgrading pip...${NC}"
    "$VENV_DIR/bin/pip" install --upgrade pip
    
    if [ -f "$REQ_FILE" ]; then
        echo -e "${BLUE}[INFO] Installing dependencies from $REQ_FILE...${NC}"
        "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
    else
        echo -e "${YELLOW}[WARN] requirements.txt not found. Installing default packages...${NC}"
        "$VENV_DIR/bin/pip" install dash ase pymatgen crystal-toolkit
        # Save state
        "$VENV_DIR/bin/pip" freeze > "$REQ_FILE"
    fi
    
    echo -e "${GREEN}${BOLD}[SUCCESS] Virtual environment setup completed successfully!${NC}\n"
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
}

# Launch comparison.py
run_compare() {
    check_venv
    local active_port=${CUSTOM_PORT:-$PORT_COMPARE}
    echo -e "\n${GREEN}${BOLD}[+] Launching Multi-Structure Comparison Toolkit (comparison.py)...${NC}"
    echo -e "${BLUE}[*] Running on: ${BOLD}http://127.0.0.1:$active_port${NC}"
    echo -e "${YELLOW}[*] Press Ctrl+C to terminate the server.${NC}\n"
    
    PORT=$active_port "$VENV_DIR/bin/python" "$SCRIPT_DIR/comparison.py"
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
            ;;
    esac
    exit 0
fi

# Interactive Menu Loop
while true; do
    print_banner
    echo -e "   ${BOLD}Configure & Run Applications:${NC}"
    echo -e "   -----------------------------"
    echo -e "   ${CYAN}1)${NC} View Single Structure ${BLUE}(runs structure.py on port ${CUSTOM_PORT:-$PORT_VIEW})${NC}"
    echo -e "   ${CYAN}2)${NC} Compare Multiple Structures ${BLUE}(runs comparison.py on port ${CUSTOM_PORT:-$PORT_COMPARE})${NC}"
    echo -e "   ${CYAN}3)${NC} Configure Custom Port ${YELLOW}(current: ${CUSTOM_PORT:-defaults [View:$PORT_VIEW, Compare:$PORT_COMPARE]})${NC}"
    echo -e "   ${CYAN}4)${NC} Setup/Re-build Virtual Environment ${MAGENTA}(.venv)${NC}"
    echo -e "   ${CYAN}5)${NC} Exit"
    echo -e "${CYAN}================================================================${NC}"
    read -p "Select an option [1-5]: " menu_choice
    
    case "$menu_choice" in
        1)
            run_view
            ;;
        2)
            run_compare
            ;;
        3)
            configure_port
            ;;
        4)
            setup_venv
            read -p "Press Enter to return to the menu..."
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
