#!/bin/bash

# Enhanced PaperGrab Launch Script for Brave Browser
# This script handles bookmarklet calls and launches the Python scraper

set -e  # Exit on any error

# Configuration
VENV_PATH="$HOME/project-sandbox/paper-grabber/env"
SCRIPT_PATH="$HOME/project-sandbox/paper-grabber/main/papergrab.py"
LOG_FILE="$HOME/project-sandbox/paper-grabber/papergrab.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[PaperGrab]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check if URL is valid
validate_url() {
    local url="$1"
    if [[ -z "$url" ]]; then
        return 1
    fi
    
    # Remove papergrab: prefix if present
    url="${url#papergrab:}"
    
    # Check if it looks like a valid URL
    if [[ "$url" =~ ^https?:// ]]; then
        return 0
    elif [[ "$url" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,} ]]; then
        return 0
    else
        return 1
    fi
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Check if virtual environment exists
    if [[ ! -d "$VENV_PATH" ]]; then
        print_error "Virtual environment not found at: $VENV_PATH"
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    if [[ -f "$VENV_PATH/bin/activate" ]]; then
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Cannot activate virtual environment"
        return 1
    fi
    
    # Check if Python script exists
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        print_error "Python script not found at: $SCRIPT_PATH"
        print_status "Please ensure papergrab.py is in the correct location"
        return 1
    fi
    
    # Check if required packages are installed
    if ! python3 -c "import selenium, bs4, openpyxl" 2>/dev/null; then
        print_warning "Some required packages may be missing"
        print_status "Installing/updating requirements..."
        pip install selenium beautifulsoup4 openpyxl webdriver-manager requests lxml python-dateutil
    fi
}

# Function to handle the URL processing
process_url() {
    local url="$1"
    
    print_status "Processing URL: $url"
    log_message "Processing URL: $url"
    
    # Create a nice terminal display
    echo ""
    echo "=========================================="
    echo "🔗 PaperGrab - Academic Paper Extractor"
    echo "=========================================="
    echo ""
    
    # Run the Python script
    if python3 "$SCRIPT_PATH" "$url"; then
        print_success "Paper processing completed successfully!"
        log_message "SUCCESS: Paper processed successfully"
        return 0
    else
        print_error "Paper processing failed"
        log_message "ERROR: Paper processing failed"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "PaperGrab Launch Script"
    echo ""
    echo "Usage:"
    echo "  $0 <URL>                 Process a paper URL"
    echo "  $0 --setup              Setup environment and dependencies"
    echo "  $0 --test               Test the setup"
    echo "  $0 --bookmarklet        Generate bookmarklet code"
    echo "  $0 --help               Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 'https://www.scopus.com/record/display.uri?...'"
    echo "  $0 'papergrab:https://pubmed.ncbi.nlm.nih.gov/...'"
    echo ""
}

# Function to generate bookmarklet for Brave browser
generate_bookmarklet() {
    local script_path=$(realpath "$0")
    
    echo "=========================================="
    echo "📚 PaperGrab Bookmarklet for Brave Browser"
    echo "=========================================="
    echo ""
    echo "Copy this JavaScript code and create a bookmark with it:"
    echo ""
    echo "----------------------------------------"
    
    # Generate bookmarklet that calls this bash script
    cat << 'EOF'
javascript:(function(){
    var url = window.location.href;
    var title = document.title;
    
    // Check if this looks like an academic site
    var isAcademic = /scopus|pubmed|ieee|acm|springer|elsevier|wiley|nature|science|arxiv|researchgate|jstor|sage|taylor|cambridge|oxford/i.test(window.location.hostname);
    
    if (!isAcademic) {
        if (!confirm('This doesn\'t look like an academic paper site. Continue anyway?')) {
            return;
        }
    }
    
    // Create the papergrab URL
    var paperGrabUrl = 'papergrab:' + url;
    
    // Try to open with the custom protocol handler
    try {
        window.location.href = paperGrabUrl;
        
        // Show confirmation
        setTimeout(function() {
            if (confirm('PaperGrab launched! Did it work?\n\nClick OK if successful, Cancel to copy URL manually.')) {
                // Success feedback
                console.log('PaperGrab successful for:', title);
            } else {
                // Fallback: copy to clipboard
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(url).then(function() {
                        alert('URL copied to clipboard! Run PaperGrab manually with this URL.');
                    });
                } else {
                    prompt('Copy this URL and run PaperGrab manually:', url);
                }
            }
        }, 1000);
        
    } catch (e) {
        // Fallback if protocol handler fails
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(url).then(function() {
                alert('URL copied to clipboard! Run: ./launch.sh "' + url + '"');
            });
        } else {
            prompt('Copy this URL and run PaperGrab:', url);
        }
    }
})();
EOF
    
    echo "----------------------------------------"
    echo ""
    echo "Setup Instructions:"
    echo "1. Copy the JavaScript code above"
    echo "2. In Brave browser, create a new bookmark"
    echo "3. Set the name to 'PaperGrab'"
    echo "4. Paste the code as the URL"
    echo "5. Save the bookmark"
    echo ""
    echo "Usage:"
    echo "- Navigate to any academic paper page"
    echo "- Click the 'PaperGrab' bookmark"
    echo "- The script will automatically launch"
    echo ""
    echo "Note: You may need to set up a custom protocol handler"
    echo "for 'papergrab:' URLs to automatically launch this script."
}

# Function to setup protocol handler
setup_protocol_handler() {
    echo "Setting up 'papergrab:' protocol handler..."
    
    local desktop_file="$HOME/.local/share/applications/papergrab.desktop"
    local script_path=$(realpath "$0")
    
    # Create desktop entry
    mkdir -p "$(dirname "$desktop_file")"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PaperGrab
Comment=Academic Paper Grabber
Exec=$script_path %u
Icon=application-x-executable
StartupNotify=true
NoDisplay=true
MimeType=x-scheme-handler/papergrab;
EOF
    
    # Update MIME database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications/"
        print_success "Protocol handler registered"
    else
        print_warning "Could not register protocol handler automatically"
    fi
}

# Function to test the setup
test_setup() {
    print_status "Testing PaperGrab setup..."
    
    # Test virtual environment
    if setup_environment; then
        print_success "Virtual environment OK"
    else
        print_error "Virtual environment setup failed"
        return 1
    fi
    
    # Test Python imports
    if python3 -c "import selenium, bs4, openpyxl; print('All imports successful')"; then
        print_success "Python dependencies OK"
    else
        print_error "Missing Python dependencies"
        return 1
    fi
    
    # Test Chrome/Chromium
    if command -v google-chrome >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
        print_success "Chrome/Chromium found"
    else
        print_warning "Chrome/Chromium not found - WebDriver may have issues"
    fi
    
    print_success "Setup test completed!"
}

# Main script logic
main() {
    # Create log file if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    case "${1:-}" in
        --help|-h)
            show_help
            ;;
        --setup)
            setup_environment
            setup_protocol_handler
            ;;
        --test)
            test_setup
            ;;
        --bookmarklet)
            generate_bookmarklet
            ;;
        "")
            print_error "No URL provided"
            show_help
            exit 1
            ;;
        *)
            # Validate URL
            if validate_url "$1"; then
                # Setup and process
                if setup_environment; then
                    process_url "$1"
                    exit_code=$?
                else
                    print_error "Environment setup failed"
                    exit_code=1
                fi
            else
                print_error "Invalid URL provided: $1"
                exit_code=1
            fi
            
            # Wait before closing (useful for GUI terminals)
            echo ""
            echo "----------------------------------------"
            if [[ $exit_code -eq 0 ]]; then
                print_success "Operation completed successfully!"
            else
                print_error "Operation failed. Check the log: $LOG_FILE"
            fi
            
            read -p "Press Enter to close..." -t 30 || true
            exit $exit_code
            ;;
    esac
}

# Run main function with all arguments
main "$@"
