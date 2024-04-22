import chess

def main():

    fen_input_str = input()
    board = chess.Board(fen_input_str)

    move = input()
    Nf3 = chess.Move.from_uci(move)
    board.push(Nf3)

    print(board.fen())

if __name__ == "__main__":
    main()