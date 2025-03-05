import asyncio
import websockets
import os
import json

from pluginlist import get_plugin_list, output_csv_from_dict  # Import your existing functions

CSV_FILES = ["Effects.csv", "Generators.csv"]

def load_preferences():
    try:
        with open("pluginpreferences.json", "r") as file:
            data = json.load(file)
            return data["installed_folder"]
    except (FileNotFoundError, KeyError):
        installed_folder = input("Enter the path to the 'Installed' folder: ")
        with open("pluginpreferences.json", "w") as file:
            json.dump({"installed_folder": installed_folder}, file, indent=2)
        return installed_folder


async def send_csv(websocket):
    """Reads the CSV files and sends their contents over WebSocket."""
    try:
        for file_name in CSV_FILES:
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    data = f.read()
                await websocket.send(f"{file_name}:{data}")
    except Exception as e:
        print(f"Error sending CSV file: {e}")

async def send_plugin_data(websocket, path):
    installed_folder = load_preferences()
    print(f"Installed folder: {installed_folder}")
    while True:
        plugins_dict = get_plugin_list(installed_folder)
        output_csv_from_dict(plugins_dict)

        csv_files = ["Effects.csv", "Generators.csv"]
        plugin_data = {}

        for csv_file in csv_files:
            if os.path.exists(csv_file):
                with open(csv_file, "r") as file:
                    plugin_data[csv_file] = file.read()

        await websocket.send(json.dumps(plugin_data))
        print("Sent updated plugin data.")

        await asyncio.sleep(300)

start_server = websockets.serve(send_plugin_data, "localhost", 8765)

print("Serving at ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()