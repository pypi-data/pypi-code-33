import difflib
import os

import dlc_gui

project_path = "/home/daniel/Code/DeepLabCut/Projects/robot-Daniel-2018-12-18"

config_path = os.path.join(project_path, "config.yaml")
dir = os.path.join(project_path, "labeled-data/atlas")

dm_dir = dlc_gui.main.DataModel(config_path)
dm_dir.init_from_dir(dir)
dm_file = dlc_gui.main.DataModel(config_path)
dm_file.init_from_file(os.path.join(dir, "CollectedData_Daniel_blank.h5"))

print("print asdafsdfasdfafdas")
dm_dir_json = dm_dir.data_frame.to_json()
dm_file_json = dm_file.data_frame.to_json()

with open("dm_dir_json.json", "w") as f:
    f.write(dm_dir_json)

with open("dm_file_json.json", "w") as f:
    f.write(dm_file_json)

# differ = difflib.Differ()
# diff = differ.compare(dm_dir_json, dm_file_json)
# print("\n".join(diff))

assert dm_dir_json == dm_file_json
