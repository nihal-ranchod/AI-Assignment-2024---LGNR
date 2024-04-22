import chess

# Possibly a castling mistake here

def main():
    fen_str = input()
    board = chess.Board(fen_str)
    fens = []

    # Append the initial position FEN
    fens.append(board.fen())

    for move in board.pseudo_legal_moves:
        board.push(move)
        fens.append(board.fen())
        board.pop()

    fens.sort()
    print(*fens, sep="\n")


if __name__ == "__main__":
    main()
