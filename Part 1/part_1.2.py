import chess

def main():

    fen_input_str = input()
    board = chess.Board(fen_input_str)

    move = input()
    make_move = chess.Move.from_uci(move) # Parsing UCI string
    board.push(make_move) # Make the move

    print(board.fen())

if __name__ == "__main__":
    main()