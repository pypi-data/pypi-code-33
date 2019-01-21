import shelve
import pickle
import gzip
import shutil
import json
import os

from . import DIR_PATH, STATES_PATH, STORAGE_PATH, STORAGE_GZ_PATH, DEFAULT_BOARD
from .logger import setup_logger
from .utils import get_time


class NoteboardException(Exception):
    """Base Exception Class of Noteboard."""


class ItemNotFoundError(NoteboardException):
    """Raised when no item with the specified id found."""

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "No item with id '{}' was found.".format(self.id)


class BoardNotFoundError(NoteboardException):
    """Raised when no board with specified name found."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "No board with name '{}' was found.".format(self.name)


class States:

    """This class is in charge of saving & loading historic states of Noteboard.
    * Called in `Storage` class.
    """

    def __init__(self):
        self.stacks = []
        self.logger = setup_logger()
    
    def load(self, rm=True):
        """
        Load the very last state (info & data) and pop it from the stack.

        Arguments:
            rm {bool} -- pop the last state if True, otherwise get data of the state only
        """
        try:
            with gzip.open(STATES_PATH, "rb") as pkl:
                self.stacks = pickle.load(pkl)
        except FileNotFoundError:
            raise NoteboardException("States file not found for loading")
        if len(self.stacks) == 0:
            return False    # No more undos
        if rm is True:
            state = self.stacks.pop()    # => [undo] get the last state and remove it
            self.logger.debug("Load state: {}".format(state))
            # Update the pickle file
            with gzip.open(STATES_PATH, "wb") as pkl:
                pickle.dump(self.stacks, pkl)
        else:
            state = self.stacks[-1]
        return state
    
    def save(self, info, action, data):
        """
        Save state data to pickle file.

        Arguments:
            info {str} -- basic information of this state
            action {str} -- the last action
            state {dict} -- data of the current state to be saved
        """
        is_new = not os.path.isfile(STATES_PATH)
        # Create and initialise pickle file with an empty list
        if is_new:
            with gzip.open(STATES_PATH, "wb+") as pkl:
                pickle.dump([], pkl)
        # Dump state data
        # => read the current saved states
        with gzip.open(STATES_PATH, "rb") as pkl:
            self.stacks = pickle.load(pkl)
        # => dump state data
        state = {"info": info, "action": action, "data": data}
        self.logger.debug("Dump state: {}".format(state))
        self.stacks.append(state)
        with gzip.open(STATES_PATH, "wb") as pkl:
            pickle.dump(self.stacks, pkl)


class Storage:

    """This class handles the main back-end job of Noteboard, including I/O of shelf and operations."""

    def __init__(self):
        self._shelf = None
        self._States = States()
        self.logger = setup_logger()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
        return False

    def open(self):
        # Open shelf
        if self._shelf is not None:
            raise NoteboardException("Shelf object has already been opened.")

        if not os.path.isdir(DIR_PATH):
            self.logger.debug("Making directory {} ...".format(DIR_PATH))
            os.mkdir(DIR_PATH)

        if os.path.isfile(STORAGE_GZ_PATH):
            # decompress compressed storage.gz to a storage file
            with gzip.open(STORAGE_GZ_PATH, "rb") as f_in:
                with open(STORAGE_PATH, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(STORAGE_GZ_PATH)

        self._shelf = shelve.open(STORAGE_PATH, "c", writeback=True)

    def close(self):
        if self._shelf is None:
            raise NoteboardException("No opened shelf object to be closed.")

        # Cleanup
        for board in self.shelf:
            # remove empty boards
            if not self.shelf[board]:
                self.shelf.pop(board)
                continue
            # always sort items on the boards before closing
            self.shelf[board] = list(sorted(self.shelf[board], key=lambda x: x["id"]))

        self._shelf.close()
        # compress storage to storage.gz
        with gzip.open(STORAGE_GZ_PATH, "wb") as f_out:
            with open(STORAGE_PATH, "rb") as f_in:
                shutil.copyfileobj(f_in, f_out)
        os.remove(STORAGE_PATH)

    @property
    def shelf(self):
        """Use this property to access the shelf object from the outside."""
        if self._shelf is None:
            raise NoteboardException("No opened shelf object to be accessed.")
        return self._shelf

    @property
    def boards(self):
        """Get all existing board titles."""
        return list(self.shelf.keys())

    @property
    def ids(self):
        """Get all existing item ids."""
        results = []
        for board in self.shelf:
            for item in self.shelf[board]:
                results.append(item["id"])
        return sorted(results)

    @property
    def total(self):
        """Get the total amount of items in all boards."""
        return len(self.ids)

    def get_item(self, id):
        """Get the item with the give ID. ItemNotFoundError will be raised if nothing found."""
        for board in self.shelf:
            for item in self.shelf[board]:
                if item["id"] == id:
                    return item
        raise ItemNotFoundError(id)

    def get_board(self, name):
        """Get the board with the given name. BoardNotFound will be raised if nothing found."""
        for board in self.shelf:
            if board == name:
                return self.shelf[name]
        raise BoardNotFoundError(name)

    def get_all_items(self):
        items = []
        for board in self.shelf:
            for item in self.shelf[board]:
                items.append(item)
        return items

    def _add_board(self, board):
        if board.strip() == "":
            raise ValueError("Board title must not be empty.")
        if board in self.shelf.keys():
            raise KeyError("Board already exists.")
        self.logger.debug("Added Board: '{}'".format(board))
        self.shelf[board] = []  # register board by adding an empty list

    def _add_item(self, id, board, text):
        date, timestamp = get_time()
        payload = {
            "id": id,           # int
            "text": text,       # str
            "time": timestamp,  # int
            "date": date,       # str
            "tick": False,      # bool
            "mark": False,      # bool
            "star": False,      # bool
            "tag": ""           # str
        }
        self.shelf[board].append(payload)
        self.logger.debug("Added Item: {} to Board: '{}'".format(json.dumps(payload), board))
        return payload

    def add_item(self, board, text):
        """[Action]
        * Can be Undone: Yes
        Prepare data to be dumped into the shelf.
        If the specified board not found, it automatically creates and initialise a new board.
        This method passes the prepared dictionary data to self._add_item to encrypt it and really add it to the board.
        
        Returns:
            dict -- data of the added item
        """
        current_id = 1
        # get all existing ids
        ids = self.ids
        if ids:
            current_id = ids[-1] + 1
        # board name
        board = board or DEFAULT_BOARD
        # save state before doing modification
        self._save_state("Add item {} to {}".format(current_id, board), "add")
        # add
        if board not in self.shelf:
            # create board
            self._add_board(board)
        # add item
        return self._add_item(current_id, board, text)

    def remove_item(self, id):
        """[Action]
        * Can be Undone: Yes
        Remove an existing item from board.

        Returns:
            dict -- data of the removed item
            str -- board name of the regarding board of the removed item
        """
        status = False
        for board in self.shelf:
            for item in self.shelf[board]:
                if item["id"] == id:
                    # save
                    self._save_state("Remove item {} on {}".format(id, board), "remove")
                    # remove
                    self.shelf[board].remove(item)
                    removed = item
                    board_of_removed = board
                    self.logger.debug("Removed Item: {} on Board: '{}'".format(json.dumps(item), board))
                    status = True
            if len(self.shelf[board]) == 0:
                del self.shelf[board]
        if status is False:
            raise ItemNotFoundError(id)
        return removed, board_of_removed
    
    def clear_board(self, board=None):
        """[Action]
        * Can be Undone: Yes
        Remove all items of a board or of all boards (if no board is specified).

        Returns:
            int -- total amount of items removed
        """
        if not board:
            amt = len(self.ids)
            # save
            self._save_state("Clear {} items on all boards".format(amt), "clear")
            # remove all items of all boards
            self.shelf.clear()
            self.logger.debug("Cleared all {} Items".format(amt))
        else:
            amt = len(self.shelf[board])
            # save
            self._save_state("Clear {} items on {}".format(amt, board), "clear")
            # remove
            if board not in self.shelf:
                raise BoardNotFoundError(board)
            del self.shelf[board]
            self.logger.debug("Cleared {} Items on Board: '{}'".format(amt, board))
        return amt

    def modify_item(self, id, key, value):
        """[Action]
        * Can be Undone: Partially (only when modifying text)
        Modify the data of an item, given its ID.
        If the item does not have the key, one will be created.

        Arguments:
            id {int} -- id of the item you want to modify
            key {str} -- one of [id, text, time, tick, star, mark, tag]
            value -- new value to replace the old value
        
        Returns:
            dict -- the old item
        """
        for board in self.shelf:
            for item in self.shelf[board]:
                if item["id"] == id:
                    old = item.copy()
                    if key == "text":
                        # Save if modifying text
                        self._save_state("Edit text of item {}".format(id), "edit")
                        # update modify time
                        # ? remove this feature
                        date, time = get_time()
                        item["time"] = time
                        item["date"] = date
                    item[key] = value
                    self.logger.debug("Modified Item from {} to {}".format(json.dumps(old), json.dumps(item)))
                    return old
        raise ItemNotFoundError(id)

    def move_item(self, id, board):
        """[Action]
        * Can be undone: No
        Move the whole item to the destination board, given the id of the item and the name of the board.

        If the destination board does not exist, one will be created.

        Arguments:
            id {int} -- id of the item you want to move
            board {str} -- name of the destination board

        Returns:
            item {dict} -- the item that is moved
        """
        for b in self.shelf:
            for item in self.shelf[b]:
                if item["id"] == id:
                    if not self.shelf.get(board):
                        # register board with a empty list if board not found
                        self.shelf[board] = []
                    # append to dest board `board`
                    self.shelf[board].append(item)
                    # remove from the current board `b`
                    self.shelf[b].remove(item)
                    return item
        raise ItemNotFoundError(id)

    @staticmethod
    def _validate_json(data):
        keys = ["id", "text", "time", "date", "tick", "mark", "star", "tag"]
        for board in data:
            if str(board) == "":
                return False
            # Check for board type (list)
            if not isinstance(data[board], list):
                return False
            for item in data[board]:
                # Check for item type (dictionary)
                if not isinstance(item, dict):
                    return False
                # Check for existence of keys
                for key in keys:
                    if key not in item.keys():
                        return False
        return True

    def import_(self, path):
        """[Action]
        * Can be Undone: Yes
        Import and load a local file (json) and overwrite the current boards.

        Arguments:
            path {str} -- path to the archive file
        
        Returns:
            path {str} -- full path of the imported file
        """
        path = os.path.abspath(path)
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise NoteboardException("File not found ({})".format(path))
        except json.JSONDecodeError:
            raise NoteboardException("Error when decoding JSON format")
        else:
            if self._validate_json(data) is False:
                raise NoteboardException("Invalid JSON structure for board")
            # Save
            self._save_state("Import boards from {}".format(path), "import")
            # Overwrite the current shelf and update it
            self.shelf.clear()
            self.shelf.update(dict(data))
            return path
    
    def export(self, dest="./board.json"):
        """[Action]
        * Can be Undone: No
        Exoport the current shelf as a JSON file to `dest`.

        Arguments:
            dest {str} -- path of the destination
        
        Returns:
            path {str} -- full path of the exported file
        """
        dest = os.path.abspath(dest)
        data = dict(self.shelf)
        with open(dest, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
        return dest
    
    def _save_state(self, info, action):
        data = dict(self.shelf)
        return self._States.save(info, action, data)
    
    def load_state(self):
        state = self._States.load()
        if state is False:
            return state
        self.shelf.clear()
        self.shelf.update(state["data"])
