# OPV_Analysis

Graphical User Interface (GUI) for JV curve analysis of organic photovoltaic cells.

# Usage

This UI plots JV data and analyzes up to 8 devices at a time and outputs Voc, Jsc, FF, and 
PCE data for each device as well as the average of those devices via .txt file. The user may
also select which devices he or she would like to exclude, of which, changes will be reflected 
in the averaged values. This UI takes in a folder of JV data and analyzes the .liv1 files in 
the folder.

To use this UI:

	1. Run the OPV_wx_GUI.py which will prompt the user to select a folder of 
	   device data
	2. Select a folder of device data
	3. Choose to exclude any devices using the "Exclude from average" buttons
	4. Export the analyzed data using the "Export" button (the .txt file will be
	   outputted to the same directory as OPV_wx_GUI.py file
	5. Exit the UI
	6. Repeat to analyze other substrates

## Dependencies

This UI requires Python, Numpy, and wxPython.
