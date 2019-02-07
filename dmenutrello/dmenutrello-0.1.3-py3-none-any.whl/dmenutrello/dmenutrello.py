import functools
import dmenu
import configparser
from os.path import expanduser
from trello import TrelloClient

#constants
BOARDS = 0
LISTS = 1
CARDS = 2
COMMENTS = 3

dmenu_show = None

def show(mode, data, parent, prompt):
    menuItems= []
    if mode != BOARDS:
        menuItems.append('..')
    menuItems.extend(data.keys())
    out = dmenu_show(menuItems, prompt=prompt)
    #check for match
    if out == '..':
        return data, parent
    if out in data:
        #save object for return, 'this' is the parent of the underlying object
        this = data[out]
        #override match with new dictionary and fill it
        data[out] = {}
        if mode == BOARDS:
            for d in this.list_lists():
                data[out][d.name] = d
        elif mode == LISTS:
            for d in this.list_cards():
                data[out][d.name] = d
        elif mode == CARDS:
            for d in this.get_comments():
                data[out][d['data']['text']] = d
        return data[out], this
    elif out is not None:
        #no match, add new and call this function again with another prompt
        if mode == BOARDS:
            data[out] = parent.add_board(out)
        elif mode == LISTS:
            data[out] = parent.add_list(out)
        elif mode == CARDS:
            data[out] = parent.add_card(out)
        elif mode == COMMENTS:
            data[out] = parent.comment(out)
        return show(mode, data, parent, "ok")

def main():
    global dmenu_show
    config = configparser.ConfigParser()
    parent = [None] * 5
    data = [None] * 5
    data[0] = {}

    config.read(expanduser('~/.dmenutrello'))

    dmenu_show = functools.partial(dmenu.show,
            font=config.get('DMENU', 'font'),
            background_selected=config.get('DMENU','background_selected'),
            foreground_selected=config.get('DMENU','foreground_selected'),
            foreground=config.get('DMENU','foreground'),
            background=config.get('DMENU','background'))

    key = config.get('TRELLO', 'key')
    token = config.get('TRELLO', 'token')
    parent[0] = TrelloClient(
        api_key = key,
        api_secret = token
        )

    #initial filling
    for board in parent[0].list_boards():
        data[0][board.name] = board

    # itreate through the levels
    i = 0
    while i != 4:
        data[i+1], parent[i+1] = show(i, data[i], parent[i], '')
        # if the same element returns its a back(..) move
        if data[i+1] == data[i]:
            #because show function replaces the trello object with a dict of the sub object
            # I have to find it and replace it with the trello object
            for key,value in data[i-1].items():
                if type(value) is dict:
                    data[i-1][key] = parent[i]
            i -= 1
        else:
            i += 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

