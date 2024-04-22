import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def generate_possible_moves(board):
    possible_moves = ['0000'] # Initialise with null move

    for move in board.pseudo_legal_moves:
        possible_moves.append(move.uci())

    # Adding all valid castling moves in RBC
    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move) and move not in board.legal_moves:
            possible_moves.append(move.uci())

    possible_moves.sort()
    return possible_moves

def main():
    fen_str = input()
    board = chess.Board(fen_str)

    for move in generate_possible_moves(board):
        print(move)
  
if __name__ == "__main__":
    main()
