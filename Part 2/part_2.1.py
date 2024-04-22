import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def moves(board):
    moves = ['0000']

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())

    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.legal_moves:
            # this would be a valid castling move in RBC
            moves.append(move.uci())

    moves.sort()
    return moves

def main():
    fen_str = input()
    board = chess.Board(fen_str)

    for move in moves(board):
        print(move)
  
if __name__ == "__main__":
    main()
