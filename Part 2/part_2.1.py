import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def main():
    fen_str = input()
    board = chess.Board(fen_str)
    moves = ['0000']

    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move):
            # this would be a valid castling move in RBC
            moves.append(move.uci())

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())

    moves.sort()
    for i in moves:
        print(i)
  

if __name__ == "__main__":
    main()
