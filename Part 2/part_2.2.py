import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def generate_possible_moves(board):
    possible_moves = ['0000'] # Initialise with null move

    # Add pseudo-legal moves
    for move in board.pseudo_legal_moves:
        possible_moves.append(move.uci())

    # Adding all valid castling moves in RBC
    for move in without_opponent_pieces(board).generate_castling_moves():
        # Check if the castling move is not illegal and not already in the list of legal moves
        if not is_illegal_castle(board, move) and move not in board.legal_moves:
            possible_moves.append(move.uci())

    possible_moves.sort()
    return possible_moves

def main():
    fen_str = input()
    board = chess.Board(fen_str)

    new_positions = []
    for move in generate_possible_moves(board):
        move = chess.Move.from_uci(move)
        board.push(move)
        new_positions.append(board.fen())
        board.pop()
    
    new_positions.sort()
    for position in new_positions:
        print(position)

if __name__ == "__main__":
    main()
