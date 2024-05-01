# this script is for extracting a list of plugins from FL Studio's plugin database
import os
import json

def load_nfo_file(filepath):
    data_dict = {}
    with open(filepath, 'r') as file:
        for line in file:
            # skip empty lines
            if line == '\n':
                continue

            # split line into key and value
            key, value = line.split('=')
            key = key.strip()
            value = value.strip()

            # add key-value pair to dictionary
            data_dict[key] = value
    return data_dict


def find_nfo_files(folder):
    nfo_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.nfo'):
                nfo_files.append(os.path.join(root, file))
    return nfo_files


def load_nfo_files(nfo_files):
    data = []
    for nfo_file in nfo_files:
        data.append(load_nfo_file(nfo_file))
    return data

def remove_duplicates(nfo_data):
    # use the 'ps_file_name_0' key to check for duplicates
    unique_data = []
    unique_names = set()
    for plugin in nfo_data:
        name = plugin['ps_file_name_0']
        if name not in unique_names:
            unique_data.append(plugin)
            unique_names.add(name)
    return unique_data


def get_plugin_list(installed_folder):
    # Plugin database/nfo files are stored in the 'Installed' folder
    # there is a VerifiedIDs.nfo file in the root file that contains a list of all VST/VST3 plugins
    # but it does not contain the FL native plugins so we will have to look in the subfolders
    # for the plugins that are installed
    plugins_dict = {}
    subfolder_types = ['Fruity', 'VST', 'VST3'] # "New" folder has duplicate entries

    plugins_categories = ['Effects', 'Generators']

    for category_folder in os.listdir(installed_folder):
        if not category_folder in plugins_categories:
            continue

        nfo_data = []
        for subfolder_type in subfolder_types:
            nfo_paths = find_nfo_files(os.path.join(installed_folder, category_folder, subfolder_type))
            nfo_data += load_nfo_files(nfo_paths)

        print(f"Found {len(nfo_data)} {category_folder} plugins.")
        nfo_data = remove_duplicates(nfo_data)
        plugins_dict[category_folder] = nfo_data

    return plugins_dict


def output_csv_from_dict(plugins_dict, names_only=False, separate_files=False):
    if not plugins_dict or len(plugins_dict['Effects']) == 0:
        print("No plugins found")
        return

    if names_only:
        write_names_to_csv(plugins_dict, separate_files)
    else:
        write_full_info_to_csv(plugins_dict, separate_files)


def write_names_to_csv(plugins_dict, separate_files):
    if separate_files:
        for category in plugins_dict.keys():
            with open(category + '.csv', 'w') as file:
                write_plugin_names(file, plugins_dict[category])
            print("Saved", category + '.csv')
    else:
        with open('plugins.csv', 'w') as file:
            for category in plugins_dict.keys():
                write_plugin_names(file, plugins_dict[category])
            print("Saved plugins.csv")


def write_plugin_names(file, plugins):
    for plugin in plugins:
        file.write(plugin['ps_file_name_0'] + '\n')


def write_full_info_to_csv(plugins_dict, separate_files):
    if separate_files:
        for category in plugins_dict.keys():
            with open(category + '.csv', 'w') as file:
                write_plugin_info(file, plugins_dict[category])
            print("Saved", category + '.csv')
    else:
        with open('plugins.csv', 'w') as file:
            for category in plugins_dict.keys():
                write_plugin_info(file, plugins_dict[category])
            print("Saved plugins.csv")


def write_plugin_info(file, plugins):
    keys = plugins[0].keys()
    file.write(','.join(keys) + '\n')
    for plugin in plugins:
        file.write(','.join(plugin.values()) + '\n')

# try loading from pluginpreferences.json first
installed_folder = None
names_only = False
separate_files = False
try:
    with open('pluginpreferences.json', 'r') as file:
        data = json.load(file)
        installed_folder = data['installed_folder']
        names_only = data['names_only']
        separate_files = data['separate_files']
    print("Found last configuration in pluginpreferences.json. Previous 'Installed' folder was:", installed_folder)
    print("Pressing enter for the following prompts will use the saved preferences.\n")
except:
    pass

# prompt user to use the saved preferences or enter new ones
if installed_folder and input("Use saved 'Installed' folder? (Y/n): " ).lower() == 'n':
    installed_folder = None

if installed_folder:
    print("Using folder: ", installed_folder)
else:
    # prompt user for the path to the 'Installed' folder
    installed_folder = input("Enter the path to the 'Image-Line\FL Studio\Presets\Plugin database\Installed' folder: ")
    if not os.path.exists(installed_folder):
        print("Path not found. Please make sure you have entered the correct absolute path.")
        exit()

names_only_str = "Output only plugin names?"
if not names_only:
    names_only = input(names_only_str + " (y/N): ").lower() == 'y'
else:
    names_only = input(names_only_str + " (Y/n): ").lower() != 'n'

separate_files_str = "Output separate csv files for each category (Effects, Generators)?"

if not separate_files:
    separate_files = input(separate_files_str + " (y/N): ").lower() == 'y'
else:
    separate_files = input(separate_files_str + " (Y/n): ").lower() != 'n'

with open('pluginpreferences.json', 'w') as file:
    json.dump({'installed_folder': installed_folder, 'names_only': names_only, 'separate_files': separate_files}, file)

plugins = get_plugin_list(installed_folder)    
output_csv_from_dict(plugins, names_only=names_only, separate_files=separate_files)