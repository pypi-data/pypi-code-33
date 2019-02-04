import functools
import dmenu
import argparse
from trello import TrelloClient

dmenu_show= functools.partial(dmenu.show, font='DejaVu Sans Mono for Powerline-14', background_selected='#2aa198',foreground_selected='#191919', foreground='#2aa198', background='#191919')



def menu(key, token):
    print(key)
    print(token)
    client = TrelloClient(
        api_key = key,
        api_secret = token
        )
    match = False

    #client.list_boards()
    #client.add_board()
    #board.list_lists()
    #board.add_list()
    #list.list_cards()
    #list.add_card()
    #card.get_comments()
    #names.append(board.name+ " #" + str(len(board.list_lists())))
    
    data = {}
    matchedData = None
    ### BOARD
    #fill data dict 
    for board in client.list_boards():
        data[board.name] = board
    
    out = dmenu_show(data.keys())
    board = None
    #check for match
    if out in data:
        match = True
        temp = data[out]
        board=temp
        data[out] = {}
        for d in temp.list_lists():
            data[out][d.name] = d
        matchedData = data[out]
    elif out is not None:
        #no match, add new
        data[out] = client.add_board(out)
        out=dmenu_show(data.keys, prompt="ok")

    print(data) 
    data = matchedData
    out=dmenu_show(matchedData.keys())
   
    if out in data:
        temp = data[out]
        data[out] = {}
        for d in temp.list_cards():
            data[out][d.name] = d
        matchedData = data[out]
    elif out is not None:
        #no match, add new
        data[out] = board.add_list(out)
        out=dmenu_show(data.keys(), prompt="ok")

    out=dmenu_show(matchedData.keys())



def createParser():
    """Create argparse object"""

    parser = argparse.ArgumentParser(description="Append -h to any command to view its syntax.")
    parser._positionals.title = "commands"


    parser.add_argument('key', metavar='KEY', type=str, help='path')
    parser.add_argument('token', metavar='TOKEN', type=str, help='path')

    return parser

def main():

    parser = createParser()
    args = parser.parse_args()
    menu(args.key, args.token)

if __name__ == '__main__':
    main()

