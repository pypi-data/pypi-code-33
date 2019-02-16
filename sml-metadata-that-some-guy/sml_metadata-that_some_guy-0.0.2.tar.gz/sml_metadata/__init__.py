import json

time_old = 0


# create json object with some random players
def generate_player(time):
    global time_old
    if time - time_old < 10:
        return None

    # save the current time
    time_old = time

    # json object
    players = {"players": [{"name": "Manuel Neuer",
                            "player_detail": {"birthday": "27-03-1986", "position": "GK", "number": "1"}},
                           {"name": "Niklas Süle",
                            "player_detail": {"birthday": "03-09-1995", "position": "DF", "number": "12"}},
                           {"name": "Franck Ribéry",
                            "player_detail": {"birthday": "07-04-1983", "position": "MF", "number": "11"}},
                           {"name": "Javi Martínez",
                            "player_detail": {"birthday": "02-09-1988", "position": "DF", "number": "19"}},
                           {"name": "Jérôme Boateng",
                            "player_detail": {"birthday": "03-09-1988", "position": "DF", "number": "5"}},
                           {"name": "Robert Lewandowski",
                            "player_detail": {"birthday": "21-08-1988", "position": "FW", "number": "9"}},
                           {"name": "Leon Goretzka",
                            "player_detail": {"birthday": "06-02-1995", "position": "MF", "number": "10"}},
                           {"name": "Rafinha",
                            "player_detail": {"birthday": "07-09-1985", "position": "DF", "number": "16"}}]}

    # Serialize players to a JSON formatted 'str'.
    print("Serialize players to a JSON formatted 'str'")
    data = json.dumps(players)
    print(data)
    return data.encode()
