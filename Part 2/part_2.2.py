import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

# Possibly a castling mistake here

def moves(board):
    moves = ['0000']

    for move in board.pseudo_legal_moves:
        moves.append(move.uci())

    for move in without_opponent_pieces(board).generate_castling_moves():
        if not is_illegal_castle(board, move):
            # this would be a valid castling move in RBC
            moves.append(move.uci())

    moves.sort()
    return moves

def main():
    fen_str = input()
    board = chess.Board(fen_str)

    new_positions = []
    for move in moves(board):
        move = chess.Move.from_uci(move)
        board.push(move)
        new_positions.append(board.fen())
        board.pop()
    
    new_positions.sort()
    for position in new_positions:
        print(position)

if __name__ == "__main__":
    main()
