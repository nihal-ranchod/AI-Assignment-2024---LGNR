import random
import chess
from reconchess import *
import chess.engine

class RandomSensing(Player):
    def __init__(self):
        super().__init__()
        self.current_state = None
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish.exe")

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.current_state = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if self.current_state.turn == self.color:
            if captured_my_piece:
                self.current_state.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        valid_squares = [sq for sq in sense_actions if 1 < sq < 56 and sq % 8 not in [0, 7]]
        return random.choice(valid_squares) if valid_squares else None

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        pass

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        legal_moves = list(self.current_state.legal_moves)
        valid_moves = [move for move in legal_moves if move in move_actions]
        if valid_moves:
            return random.choice(valid_moves)
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if requested_move is not None and taken_move is not None:
            self.current_state.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        self.engine.quit()
