# RadTrack
RadTrack is a Python 3-based desktop tool for reviewing radiology-report data stored in Excel, extracting and curating structured information from free-text reports, and building labeled datasets for research. 

RadTrack makes it simple to extract and export research-ready tabular data from report text. The workflow is designed for cases where findings of interest appear inside unstructured report text and must be manually reviewed and entered into structured columns. 

RadTrack features a smart formatting tool that detects structural sentence types in reports (primarily section headers) and uses them to improve on-screen readability. A script is provided to train this tool on a representative dataset before use.

RadTrack is primarily tested on macOS.

## Getting started

### Step 1: Prepare report spreadsheet

Before using RadTrack, you will need an Excel spreadsheet with a single header row followed by one row for each report. The spreadsheet should have at least the following columns:
- One or more **identifier columns** (this can be simply a number identifying each report)
- One or more **report columns** (this is where the report text should go)
- One or more **data columns** (these can be left blank, as they will be filled in by the software)

### Step 2: Install dependencies
RadTrack has been tested on Python 3.10+. You may install dependencies using pip and the included `requirements.txt` file. Within the `RadTrack` folder, run:

`pip install -r requirements.txt`

### Step 3: Open RadTrack launcher

Within the `RadTrack` folder, run

`python launch_radtrack.py`

This will bring up the launcher screen, where you will load the report spreadsheet and specify the identifier, report, and data columns. You may also select the smart formatting model, if you trained one in Step 5 (below). Then launch RadTrack.

### Step 4: Review and curate records

In the main window, you can:
- Move to the previous/next row
- Jump to a specific row number
- Enter extracted values into specified fields
- Enter regular expression patterns for highlighting (multiple terms per color can be specified, separated by `|`)
- Toggle ON/OFF the smart formatter (if enabled)

Extracted values are saved automatically when switching rows or exitting the application. The output path is:
`<original_filename>_edited_output.xlsx`.

### Step 5 (optional): Set up the smart formatting model

Within the `RadTrack` folder, run

`python train_formatter.py`

Here, you should perform the following steps:
1. Select the report spreadsheet
2. Choose a single column containing the report text for training
3. Press the "Auto-Analyze" button to train the model
4. Save the model.

The model should be saved to a `.pkl` file, which can be loaded when running RadTrack.

## Detailed features

### Keyboard shortcuts

The GUI includes keyboard shortcuts for row navigation.

- `⌘[` OR `Ctrl+[` — previous row
- `⌘]` OR `Ctrl+]` — next row
- `⌘G` OR `Ctrl+G` — focus the row-jump field
- `Esc` — save and exit

### Regular expression (regex) highlighting

The main app allows the user to highlight regex terms in five colors: yellow, blue, green, red, and purple.

Each box accepts a pattern, which can be a single term, multiple terms separated by vertical bar (`|`), or an arbitrary regex patterm. Pattern matching is case-insensitive. Examples:
- `fracture`
- `mass|nodule|lesion`
- `\b\d+(?:\.\d+)?\s*cm\b`

## License

RadTrack is provided as-is under the MIT License. See `LICENSE` for detailed terms.
