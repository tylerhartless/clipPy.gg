# clipPy.gg

clipPy.gg is a Python program for compositing gaming/stream clips 
vertically for viewing on tiktok/youtube shorts/facebook reels, etc 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip install -r requirements.txt
```

## Usage

To start clipPy.gg, run this in the command line in the program directory
```bash
python main.py
```

Currently only works (properly) with Apex Legends clips as the HUD elements for other games needs to be masked.
If you would like to try with a different game, select `N/A` from the dropdown. Checked HUD elements will only be 
visible if they are applicable (i.e. checking HUD elements when game is set to "N/A" will return no HUD elements).

To remap Facecam location, clear the `facecamxy` value from the ini file and run the program
