# this script is for extracting a list of plugins from FL Studio's plugin database
import os
import re
import json
import argparse

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


def output_json_full(plugins_dict):
    plugin_json = {}
    manufacturer_dict = {}

    for category in plugins_dict.values():
        for plugin in category:
            manufacturer = plugin.get('ps_file_vendorname_0')
            product_name = plugin.get('ps_file_name_0')

            if manufacturer:
                if manufacturer not in manufacturer_dict:
                    manufacturer_dict[manufacturer] = []
                manufacturer_dict[manufacturer].append(product_name)

    plugin_json['plugins'] = [{'manufacturer': key, 'products': value} for key, value in manufacturer_dict.items()]
    
    with open('plugins.json', 'w') as file:
        json.dump(plugin_json, file, indent=2)
    print("Saved plugins.json")

def remove_non_verified(nfo_data):
    # load the VerifiedIDs.nfo file to get a list of verified plugins
    verified_plugins = []
    with open(installed_folder + '\\VerifiedIDs.nfo', 'r') as file:
        for line in file:
            info = line.split(':')
            file_path = info[2].strip().split('=')[1]
            # grab plugin name from "\(name).nfo" using regex
            pattern = re.compile(r'.*\\(.+).(nfo|NFO)')
            match = pattern.search(file_path)
            if match:
                plugin_name = match.group(1)
                verified_plugins.append(plugin_name)
    print(f"Found {len(verified_plugins)} verified plugins.")
    print(verified_plugins)
        
    verified_data = []
    removed_data = []
    for plugin in nfo_data:
        if 'ps_file_name_0' in plugin.keys() and plugin['ps_file_name_0'] in verified_plugins:
            verified_data.append(plugin)
            continue

        removed_data.append(plugin)
            
    print(f"Kept {len(verified_data)} verified plugins.")
    print(f"Removed {len(removed_data)} unverified plugins.")

    for plugin in removed_data:
        print(plugin['ps_file_name_0'])
    
    return verified_data
        


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
            data = load_nfo_files(nfo_paths)
            if subfolder_type != 'Fruity':
                data = remove_non_verified(data)
            nfo_data.extend(data)
        
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

def main():
    global installed_folder
    parser = argparse.ArgumentParser(description="Extract plugin data from FL Studio")
    parser.add_argument("--json-full", action="store_true", help="Output plugins in full JSON format")
    args = parser.parse_args()

    try:
        with open('pluginpreferences.json', 'r') as file:
            data = json.load(file)
            installed_folder = data['installed_folder']
            names_only = data['names_only']
            separate_files = data['separate_files']
        print("Using last saved configuration.")
    except:
        installed_folder = input("Enter the path to the 'Installed' folder: ")
        names_only = input("Output only plugin names? (y/N): ").lower() == 'y'
        separate_files = input("Output separate CSV files for each category? (y/N): ").lower() == 'y'
        with open('pluginpreferences.json', 'w') as file:
            json.dump({'installed_folder': installed_folder, 'names_only': names_only, 'separate_files': separate_files}, file)

    plugins = get_plugin_list(installed_folder)

    if args.json_full:
        output_json_full(plugins)
    else:
        output_csv_from_dict(plugins, names_only=names_only, separate_files=separate_files)


if __name__ == "__main__":
    main()