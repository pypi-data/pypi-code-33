import chess
import chess.engine
import chess.pgn
import datetime


def is_insufficient_material_for_time_win(color, board):
    """Return true if color has any way of winning the game. NOTE: Not complete, see niklasf/python-chess/issues/362"""
    # Remove all of not colors pieces (except for king).
    # If the game now has insufficient material we'll call it a draw (exceptions exists).
    board = board.copy()
    for sq in chess.squares:
        p = board.piece_at(sq)
        if p.color != color and p.piece_type != chess.KING:
            board.remove_piece_at(sq)
    return board.is_insufficient_material()


def play_match(engine1, engine2, time_control):
    """Play a match between the given engines with a given time control.

    Arguments
    ---------
    engine1, engine2: str
        Executable of the UCI engines to play. Engine1 will play white.
    time_control: chester.timecontrol.TimeControl
        A TimeControl instance describing the time control to use.

    Returns
    -------
        A `chess.pgn.Game` instance describing the game.
    """
    engine1 = chess.engine.SimpleEngine.popen_uci(engine1)
    engine2 = chess.engine.SimpleEngine.popen_uci(engine2)

    current_player = engine1

    result = None
    time_control.start_new_game()
    board = chess.Board()
    while not board.is_game_over():
        output = current_player.play(
            board,
            chess.engine.Limit(
                white_clock=time_control.wtime,
                black_clock=time_control.btime,
                white_inc=time_control.increment,
                black_inc=time_control.increment,
            ),
        )

        player_flagged = time_control.signal_move_made()

        if player_flagged:
            if is_insufficient_material_for_time_win(not board.turn, board):
                result = "1/2-1/2"
            else:
                result = "0-1" if board.turn == chess.WHITE else "1-0"
            break

        board.push(output.move)
        current_player = engine1 if board.turn == chess.WHITE else engine2

    pgn = chess.pgn.Game.from_board(board)
    pgn.headers["White"] = engine1.id.get("name")
    pgn.headers["Black"] = engine2.id.get("name")
    pgn.headers["Date"] = datetime.datetime.today().strftime("%Y-%m-%d")
    if result is not None:
        pgn.headers["Result"] = result

    engine1.quit()
    engine2.quit()

    return pgn
