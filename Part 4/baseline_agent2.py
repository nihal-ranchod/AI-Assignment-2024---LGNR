import random
import chess
from reconchess import *
import chess.engine

class RandomSensing(Player):
    def __init__(self):
        self.current_state = chess.Board() # Initialise current state of the game board
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish.exe") # Stockfish Connection

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.color = color
        self.current_state = board

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # If opponent captured our piece, remove it from the board
        if captured_my_piece:
            # Check if opponent's turn to move before removing the piece
            if self.current_state.turn != self.color:
                self.current_state.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        # Choose a square to sense on the board, avoiding sqaures on the edges of the board
        valid_squares = [sq for sq in sense_actions if 1 < sq < 56 and sq % 8 not in [0, 7]]
        return random.choice(valid_squares) if valid_squares else None

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # Update the current state of the board based on the sensed window
        for square, piece in sense_result:
            # If a piece is present in the sensed square, update the board accordingly
            if piece is not None:
                self.current_state.set_piece_at(square, piece)
            # If no piece is present, remove any existing piece from the sensed square
            else:
                self.current_state.remove_piece_at(square)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        time_limit = max(seconds_left / 10, 1)  # Calculate time limit for Stockfish
        if len(self.current_state.move_stack) > 10000:
            # If number of moves exceeds 10000, randomly remove moves to reduce the number to 10000
            self.current_state.pop(random.randint(0, len(self.current_state.move_stack) - 1))

        # Initialise a dictionary to store move votes     
        votes = {}
        for _ in range(len(self.current_state.move_stack)):
            # Get the best move from Stockfish analysis
            with self.engine.analysis(self.current_state, multipv=1, limit=chess.engine.Limit(time=time_limit)) as analysis:
                try:
                    best_move = analysis.best_move
                    # Check if move is legal and add it to the votes dictionary
                    if best_move in move_actions:
                        if best_move in votes:
                            votes[best_move] += 1
                        else:
                            votes[best_move] = 1
                except chess.engine.EngineError:
                    pass

        if votes:
            # Choose move with highest number of votes
            return max(votes, key=votes.get)
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # Apply the move to the board if it was taken
        if taken_move is not None:
            # Check if a move was requested and if it's legal before applying it
            if requested_move is not None:
                if self.current_state.is_legal(requested_move):
                    self.current_state.push(requested_move)
            else:
                # If no move was requested (None), do nothing
                pass

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        # Quit stockfish connection
        self.engine.quit()
