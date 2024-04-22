import chess

def main():

    fen_input_str = input()
    board = chess.Board(fen_input_str)

    print(board)

if __name__ == "__main__":
    main()