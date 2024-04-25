import random
import chess.engine
from reconchess import *

stockfish_path = 'stockfish/stockfish.exe'

class TroutAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)
        self.list_of_possible_states = []

    def handle_game_start(self, color: chess.Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: chess.Color, capture_square: Optional[Square]):
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # Exclude squares on the edges of the board
        valid_sense_actions = [sq for sq in sense_actions if 1 < sq < 56 and 1 < sq % 8 < 6]
        # If our piece was just captured, sense where it was captured
        if self.my_piece_captured_square and self.my_piece_captured_square in valid_sense_actions:
            return self.my_piece_captured_square
        # Otherwise, randomly choose a sense action
        return random.choice(valid_sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        num_boards = len(self.list_of_possible_states)
        time_limit = min(10.0 / max(num_boards, 1), seconds_left)  # Avoid division by zero

        if not self.list_of_possible_states:
            return None  # No possible moves, return None

        if num_boards > 10000:
            self.list_of_possible_states = random.sample(self.list_of_possible_states, 10000)

        votes = {}
        for state in self.list_of_possible_states:
            board = state.copy()
            result = self.engine.play(board, chess.engine.Limit(time=time_limit))
            if result.move in votes:
                votes[result.move] += 1
            else:
                votes[result.move] = 1

        if not votes:
            return None  # No votes, return None

        chosen_move = max(votes, key=votes.get)
        return chosen_move


    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
