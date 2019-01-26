#!python3


# standard imports
import sys


# local imports
import xutil

g_display = xutil.g_display


def find_window(window=None, window_id=None, window_name=None, class_type=None, class_name=None, level=0):
    """
    Find a window by a piece of given information.

    :param window_id:
    :param window_name:
    :param class_type:
    :param class_name:
    :return: a reference to a window
    """
    # ensure at least one value is present
    # if [window_id, window_name, class_type, class_name].count(None) == 4:
    #     raise Exception('Something must be given to find.')

    # root node
    if window is None:
        global g_display
        window = g_display.screen().root

    # walk each child
    for child in window.query_tree().children:

        child_id = child.id
        child_wm_name = child.get_wm_name()
        child_wm_class = child.get_wm_class()
        print(level * ' ', child_wm_name, child_wm_class, child_id)

        # window_id
        if window_id is not None and child_id == window_id:
            return child

        # window_name
        if window_name is not None and child_wm_name == window_name:
            return child

        if child_wm_class is not None:

            # class type
            if class_type is not None and child_wm_class[0] == class_type:
                return child

            # class name
            if class_name is not None and child_wm_class[1] == class_name:
                return child

        # walk each child of the child
        result = find_window(
            child,
            window_id=window_id,
            window_name=window_name,
            class_type=class_type,
            class_name=class_name,
            level=level+2
        )
        if result is not None:
            return result

    return None


def main():

    find_window()
    return 0


if __name__ == '__main__':
    sys.exit(main())
