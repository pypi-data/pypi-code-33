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
                            "player_detail": {"birthday": "27-03-1986", "position": "GK"}},
                           {"name": "Niklas Süle",
                            "player_detail": {"birthday": "03-09-1995", "position": "DF"}},
                           {"name": "Franck Ribéry",
                            "player_detail": {"birthday": "07-04-1983", "position": "MF"}},
                           {"name": "Javi Martínez",
                            "player_detail": {"birthday": "02-09-1988", "position": "DF"}},
                           {"name": "Jérôme Boateng",
                            "player_detail": {"birthday": "03-09-1988", "position": "DF"}},
                           {"name": "Robert Lewandowski",
                            "player_detail": {"birthday": "21-08-1988", "position": "FW"}},
                           {"name": "Leon Goretzka",
                            "player_detail": {"birthday": "06-02-1995", "position": "MF"}},
                           {"name": "Rafinha",
                            "player_detail": {"birthday": "07-09-1985", "position": "DF"}}]}

    # Serialize players to a JSON formatted 'str'.
    print("Serialize players to a JSON formatted 'str'")
    data = json.dumps(players)
    print(data)
    return data.encode()
