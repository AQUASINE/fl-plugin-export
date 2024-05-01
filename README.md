# FL Studio Plugin Export

To address the lack of a way to export a list of plugins directly from FL Studio, this is a simple workaround script that allows you to export a list of all your plugins in FL Studio in `.csv` format by collecting all the data from .nfo files in the `Image-Line/FL Studio/Presets/Plugin database/Installed` folder. 

This script can export just a list of names or all the data found in the .nfo files. It can also split the list into a list of Effects and a list of Generators if needed. It also saves your preferences to a pluginpreferences.json file so that you don't have to find it again.