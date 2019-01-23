
import easygui


def show_message(title: str, message="", button=""):
    if not isinstance(title, str):
        raise TypeError("`title` expected string object")
    if not isinstance(message, str):
        raise TypeError("`message` expected string object")
    if not isinstance(button, str):
        raise TypeError("`button` expected string object")

    if button:
        easygui.msgbox(message, title, button)
    else:
        easygui.msgbox(message, title)

def show_question(title: str, message=" ", buttons=()):
    if not isinstance(title, str):
        raise TypeError("`title` expected string object")
    if not isinstance(message, str):
        raise TypeError("`message` expected string object")
    if not isinstance(buttons, list) and not isinstance(buttons, tuple):
        raise TypeError("`buttons` expected a list or tuple of strings")
    if len(buttons) != 2:
        raise TypeError("`buttons` expected to contain two elements")
    if not isinstance(buttons[0], str):
        raise TypeError("`buttons[0]` expected string object")
    if not isinstance(buttons[1], str):
        raise TypeError("`buttons[1]` expected string object")

    if buttons:
        return easygui.ynbox(message, title, buttons)
    else:
        return easygui.ynbox(message, title)

if __name__ == "__main__":
    show_message("title", "message content", "OK")
    ret = show_question("Are you show to quit?", "Some files not saved yet!", ("OK", "Cancel"))
    print(ret)
    ret = show_question("Are you show to quit?", "Some files not saved yet!", ("OK"))
    print(ret)
