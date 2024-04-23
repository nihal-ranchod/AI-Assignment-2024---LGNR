import chess.engine
import random
from reconchess import *
import os

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class TroutBot(Player):

    def __init__(self):
        # Initialize variables
        self.board = None
        self.color = None
        self.my_piece_captured_square = None

        # Initialize Stockfish engine
        stockfish_path = os.environ.get(STOCKFISH_ENV_VAR, 'stockfish/stockfish.exe')
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)

        # Store squares occupied by own pieces
        self.own_piece_squares = set()

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        # Initialize variables and store own piece squares
        self.board = board
        self.color = color
        self.own_piece_squares = {square for square, piece in self.board.piece_map().items() if piece.color == self.color}

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # If piece was captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # If possible capture during move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        # Randomly choose a sense action, excluding own piece squares
        return random.choice(list(set(sense_actions) - self.own_piece_squares))

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # Try to take the king if possible
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # Try to move with Stockfish
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.1))  # Decreased time
            return result.move
        except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
            pass

        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # If move executed, apply to board and update own piece squares
        if taken_move is not None:
            self.board.push(taken_move)
            self.own_piece_squares = {square for square, piece in self.board.piece_map().items() if piece.color == self.color}

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        # Quit Stockfish engine
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass


def main():
    fen_str = input()
    bot = TroutBot()
    board = chess.Board(fen_str)

    # Determine the color of the bot based on the turn in the FEN string
    color = board.turn

    # Start the game
    bot.handle_game_start(color, board, "Opponent")

    # Choose a move and print its UCI representation
    move = bot.choose_move(list(board.legal_moves), 0.5)
    if move:
        print(move.uci())

    # Quit the engines
    bot.engine.quit()

if __name__ == "__main__":
    main()
