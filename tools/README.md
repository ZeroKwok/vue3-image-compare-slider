# image-compare-slider Tools

A lightweight visual batch image comparison tool to simplify evaluation after bulk image processing.

## Features

- Extract images to compare from a target directory (`image-compare-slider.py`)
- Support for scanning subdirectories and browsing by index
- One-command hosting of image directories and static assets for quick preview

## Prerequisites

- Python 3.7+
- Node.js and Yarn (optional, for building frontend tools)
- Basic familiarity with the command line

## Installation

```bash
git clone https://github.com/ZeroKwok/vue3-image-compare-slider.git
cd vue3-image-compare-slider
yarn && yarn tools:build && yarn tools:test
```

## Quick Start / Usage

Run scanner to collect image pairs or start the viewer to host the comparison UI.

Example (scan and serve):

```bash
python ./tools/image-compare-slider.py -d path/to/image-directory --scan --view
```

Then open: http://localhost:8000  
Press CTRL+C to quit.

## Command Line Syntax

```bash
image-compare-slider.py <--scan|--view> -d <image-directory> [-t <template-directory>] [-p <port>] [-h <host>]

Options:
- -d, --directory      Path to the image directory
- -t, --template       Optional template directory (overrides default UI templates)
- -p, --port           Port number for the local server (default: 8000)
- -h, --host           Hostname or IP to bind (default: 127.0.0.1)
- --scan               Scan the image directory and generate data files
- --view               Start the image comparison viewer (serves a local web UI)
```

## Notes

The tool expects consistent naming or folder structure for image pairs; adjust scanning rules in the script if needed.
