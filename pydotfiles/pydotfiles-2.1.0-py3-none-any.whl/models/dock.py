from pathlib import Path
from pydotfiles.loading import load_plist
from pydotfiles.utils import run_command


class DockManager:
    """
    Manages anything related to a dock
    """

    @property
    def dock_plist_path(self):
        return Path.home().joinpath("Library/Preferences/com.apple.dock.plist")

    def get_current_dock_applications(self):
        dock_plist_data = load_plist(self.dock_plist_path)
        return extract_persistent_app_names(dock_plist_data)

    @staticmethod
    def delete_dock_plist_file():
        command = f'defaults delete com.apple.Dock persistent-apps'
        run_command(command)

    @staticmethod
    def add_application_to_default_on_dock(application):
        command = f'defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/{application}.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"'
        run_command(command)

    @staticmethod
    def restart_dock():
        command = f"killall Dock"
        run_command(command)


"""
Helper methods
"""


def extract_persistent_app_names(plist_data):
    persistent_apps = plist_data['persistent-apps']
    return {persistent_app['tile-data']['file-label'] for persistent_app in persistent_apps}
