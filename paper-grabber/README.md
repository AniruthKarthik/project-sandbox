# Paper Grabber - My Personal Research Library Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)](https://github.com/AniruthKarthik/paper-grabber)

This started as a fun coding project because I use Scopus for finding papers, but wanted something more personal for tracking my research workflow. While Scopus export is great for getting data out, I wanted to **track my research journey over time** - like seeing how papers I saved months ago are gaining citations, or building a timeline of when I discovered key papers in my field.

This tool helps you build a personal research library from Scopus, offering both a quick-save bookmarklet for individual papers and a powerful batch processing script for larger datasets.

## Why I Built This Alongside Regular Export

Scopus export works perfectly for what it's designed for, but I wanted something different for my personal research tracking. 

What I wanted for my personal workflow:
- **Track when I discovered papers** - sometimes the timing matters for understanding how my thinking evolved
- **See citation growth over time** - that paper I saved 6 months ago with 12 citations now has 47!
- **Build one continuous personal library** instead of having separate export files scattered everywhere
- **Smart duplicate handling** for my own collection across different research sessions
- **Personal research timeline** - Excel format works well for my note-taking style

Basically, I wanted my personal research library to evolve with me over time, complementing the powerful search and discovery that Scopus already provides.

## What It Does

*   **Python Script (`papergrab.py`):**
    *   Saves individual papers from Scopus with one click using a bookmarklet.
    *   Keeps everything in one Excel file that builds up over time.
    *   Tracks when you saved each paper (helps see your research timeline).
    *   Smart enough to not duplicate papers you've already saved.
    *   You can re-run it on old papers to update citation counts.
    *   Works on Linux, macOS, and Windows.
*   **JavaScript Batch PDF Downloader (`scopus-batch-script.js`):**
    *   A Tampermonkey/Greasemonkey user script that automates batch PDF downloads directly from the Scopus website.
    *   Interacts with the Scopus user interface to select a range of papers and initiate PDF downloads.
    *   Ideal for quickly downloading multiple PDFs when browsing Scopus search results.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/AniruthKarthik/paper-grabber.git
cd paper-grabber
```

### 2. Setup Python Environment

```bash
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Add Your API Key

You'll need a free Scopus API key from [here](https://dev.elsevier.com/apikey/manage).

```bash
echo "SCOPUS_API_KEY=your_actual_api_key_here" > .env
```

### 5. Create Output Directory

```bash
mkdir -p ~/Documents/papers
```

## How It's Organized

```
paper-grabber/
├── papergrab.py         # Main Python script for individual paper saving
├── scopus_fetcher.py    # Python API logic for Scopus data
├── excel_writer.py      # Python script for Excel saving
├── scopus-batch-script.js # JavaScript for batch processing Scopus EIDs
├── launch.sh            # Browser protocol handler for Python script
├── .env                 # API key (you create this)
├── requirements.txt
└── README.md
```

## Using the Python Script (`papergrab.py`)

### Setting Up the Bookmarklet (Linux/macOS)

This part is a bit technical but worth it - you'll be able to save papers with literally one click.

#### Register Protocol Handler

```bash
cd ~/paper-grabber
chmod +x launch.sh
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/papergrab.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PaperGrab
Exec=$(pwd)/launch.sh %u
NoDisplay=true
MimeType=x-scheme-handler/papergrab;
EOF

update-desktop-database ~/.local/share/applications/
xdg-mime default papergrab.desktop x-scheme-handler/papergrab
```

#### Install Bookmarklet

Create a browser bookmark with this code as the URL:

```javascript
javascript:(function(){try{const url=window.location.href;if(!url.includes('scopus.com')){alert('❌ This bookmarklet only works on Scopus.com pages.');return;}let eid=null;let match=url.match(/[?&]eid=([^&]+)/);if(match){eid=decodeURIComponent(match[1]);}if(!eid){match=url.match(///publications///(\\d{8,})/);if(match){eid='2-s2.0-'+match[1];}}if(!eid){match=url.match(/display.uri.*?eid=([^&]+)/);if(match){eid=decodeURIComponent(match[1]);}}if(!eid){alert('❌ Could not extract EID. Use only on individual paper pages.');return;}if(!eid.startsWith('2-s2.0-')){eid='2-s2.0-'+eid;}const fullUrl=`https://www.scopus.com/record/display.uri?eid=${eid}`;window.location.href='papergrab:'+encodeURIComponent(fullUrl);}catch(e){alert('❌ Error: '+e.message);}})();
```

#### Test It

Go to any paper page on Scopus and click your bookmarklet. The script should launch and save the paper!

### Manual Usage (Works on All OS)

If the bookmarklet setup doesn't work for you, you can always run it manually:

#### Interactive Mode

```bash
source env/bin/activate
python papergrab.py
```

#### Direct URL

```bash
python papergrab.py "https://www.scopus.com/record/display.uri?eid=2-s2.0-85123456789"
```

## Using the JavaScript Batch PDF Downloader (`scopus-batch-script.js`)

This script is a Tampermonkey/Greasemonkey user script that automates the process of downloading multiple PDFs directly from Scopus search results pages. It interacts with the Scopus website's interface to select and download papers in batches.

### Prerequisites

You need a browser extension like [Tampermonkey](https://www.tampermonkey.net/) (Chrome, Edge, Safari, Firefox, Opera) or [Greasemonkey](https://www.greasespot.net/) (Firefox) installed in your web browser.

### How to Use

1.  **Install the script:**
    *   Open the `scopus-batch-script.js` file in a text editor.
    *   Copy the entire content of the file.
    *   Open your Tampermonkey/Greasemonkey dashboard in your browser.
    *   Create a new user script and paste the copied content into the editor. Save the script.
    *   Alternatively, you can often directly install user scripts by navigating to the `.js` file in your browser if you have the extension installed.

2.  **Navigate to Scopus:** Go to any search results page on Scopus (e.g., after performing a search).

3.  **Start the download:**
    *   Once on a Scopus search results page, you should see a control panel appear on the right side of the screen (usually near the top right).
    *   Click the "Start Batch Download" button within this panel.
    *   The script will then automatically interact with the Scopus page to select papers, open the download dialog, fill in the "From" and "To" ranges, and click the necessary download buttons.

4.  **Manual PDF Saving:**
    *   **Important:** Your browser's default PDF viewer or download settings will determine how the PDFs are handled. For each PDF, a "Save As" dialog might appear, or the PDF might automatically download to your default downloads folder.
    *   The script will pause between batches to allow you time to manually save the PDFs if prompted by your browser. It will log messages in the browser's console (F12 to open developer tools) to guide you.

### Script Behavior

*   The script processes papers in batches (default: 40 papers per batch).
*   It simulates clicks and input entries to navigate the Scopus download workflow.
*   It provides logging in the browser console to show its progress and any issues.
*   You can stop the automation at any time using the "Stop" button in the control panel or by pressing `Ctrl+Shift+D` (Windows/Linux) or `Cmd+Shift+D` (macOS).

## What Gets Saved

Everything goes to: `~/Documents/papers/research_papers.xlsx`

Columns include:
* Title
* Authors  
* Abstract
* Year
* Citations
* DOI
* Publication
* Volume/Issue/Pages
* EID
* URL
* Date Added (this is when YOU saved it)

## If Something Breaks

**API Key Issues**:
```bash
cat .env  # Make sure your API key is there
```

**Can't extract paper ID**: Only works on actual paper detail pages, not search results

**Script won't launch from bookmarklet**:
```bash
xdg-mime query default x-scheme-handler/papergrab  # Should show papergrab.desktop
```

**Virtual environment missing**:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Keeping It Updated

```bash
source env/bin/activate
pip install --upgrade -r requirements.txt
```

## File Templates (if you want to set up manually)

**requirements.txt**
```
requests
python-dotenv
openpyxl
```

**launch.sh**
```bash
#!/bin/bash

URL="$1"
CLEAN_URL="${URL#papergrab:}"
cd "$(dirname "$0")" || exit 1

if [ -f env/bin/activate ]; then
  source env/bin/activate
else
  echo "❌ Virtual environment not found."
  exit 1
fi

LOG="/tmp/papergrab_$(date +%s).log"
python3 papergrab.py "$CLEAN_URL" > "$LOG" 2>&1
STATUS=$?

if [ $STATUS -ne 0 ]; then
  (command -v gnome-terminal && gnome-terminal -- bash -c "cat $LOG; echo; read") \
  || (command -v xterm && xterm -e "cat $LOG; echo; read") \
  || (cat "$LOG"; echo; read)
else
  rm -f "$LOG"
fi
```

**.env**
```
SCOPUS_API_KEY=your_actual_api_key_here
```

## Useful Links

* [Scopus API Docs](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl)
* [Get API Key](https://dev.elsevier.com/apikey/manage)

## License

MIT - feel free to use/modify however you want.

---

This has been super useful for my own research workflow. If you're also tired of juggling random paper exports and want to build an actual research timeline, maybe it'll help you too!

**Happy paper hunting!**