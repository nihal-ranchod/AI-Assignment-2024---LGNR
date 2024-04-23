import chess
import chess.engine
import collections
import os

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class Agent:
    def __init__(self):

        # Initialize Stockfish engine
        stockfish_path = 'stockfish/stockfish.exe'
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)

    def handle_game_start(self, color: chess.Color, board: chess.Board, opponent_name: str):
        # Initialize variables and store own piece squares
        self.board = board
        self.color = color
        self.own_piece_squares = {square for square, piece in self.board.piece_map().items() if piece.color == self.color}

    def choose_move(self, move_actions: list, seconds_left: float) -> chess.Move:
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))  # Decreased time
            return result.move
        except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
            pass
        return None

def compute_most_common_move(fen_strings):
    moves_count = collections.defaultdict(int)
    bot = Agent()

    for fen_str in fen_strings:
        board = chess.Board(fen_str)

        try:
            # Determine the color of the bot based on the turn in the FEN string
            color = board.turn

            # Start the game
            bot.handle_game_start(color, board, "Opponent")

            # Choose a move
            move = bot.choose_move(list(board.legal_moves), 0.5)
            if move:
                move_uci = move.uci()
                moves_count[move_uci] += 1

        except Exception as e:
            print(f"Error processing board {fen_str}: {e}")

    # Quit the engines
    bot.engine.quit()

    # Find the most common move
    most_common_moves = sorted(moves_count.items(), key=lambda x: (-x[1], x[0]))
    return most_common_moves[0][0]

def main():
    # Read the number of boards
    n_boards = int(input())

    # Read the FEN strings
    fen_strings = [input().strip() for _ in range(n_boards)]

    # Compute the most common move
    most_common_move = compute_most_common_move(fen_strings)

    # Output the result
    print(most_common_move)

if __name__ == "__main__":
    main()
