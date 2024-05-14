import random
from reconchess import *
import chess.engine

class ImprovedAgent(Player):
    def __init__(self):
        # Initialize board and color attributes
        self.board = None
        self.color = None
        self.opponent_color = None

        # Initialize captured piece and move number attributes
        self.my_piece_captured_square = None
        self.move_number = 0

        # Define predefined moves for white and black
        self.white_move = [
            chess.Move.from_uci("b1c3"),
            chess.Move.from_uci("c3b5"),
            chess.Move.from_uci("b5d6"),
            chess.Move.from_uci("d6e8"),
        ]

        self.black_move = [
            chess.Move.from_uci("b8c6"),
            chess.Move.from_uci("c6b4"),
            chess.Move.from_uci("b4d3"),
            chess.Move.from_uci("d3e1"),
        ]
        
        # Define path to stockfish executable
        stockfish_path = '/opt/stockfish/stockfish'

        # Initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        # Initialize the board and our player's color
        self.board = board
        self.color = color
        
        # Determine the opponent's color based on our player's color
        if self.color == chess.WHITE:
            self.opponent_color = chess.BLACK
        else:
            self.opponent_color = chess.WHITE
            
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # Store the square where our piece was captured
        self.my_piece_captured_square = capture_square

        # If the opponent captured our piece, remove it from our board
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # Get squares with opponent's pieces
        opponent_piece_squares = [square for square, piece in self.board.piece_map().items() if piece.color == self.opponent_color]
        
        # Prioritize sensing squares with opponent's pieces
        for square in sense_actions:
            if square in opponent_piece_squares:
                return square
        
        # Define strategic moves based on player's color
        strategic_moves = self.white_move if self.color == chess.WHITE else self.black_move

        # Prioritize strategic squares based on predefined moves
        for move in strategic_moves:
            if move.to_square in sense_actions:
                return move.to_square
        
        # Define the most central squares on a chess board
        central_squares = [18, 19, 20, 27, 28, 29, 36, 37, 38]

        # Prioritize the most central squares
        for square in central_squares:
            if square in sense_actions:
                return square

        # If no central squares are available, sense any remaining square
        valid_squares = [sq for sq in sense_actions if 1 < sq < 56 and sq % 8 not in [0, 7]]
        return valid_squares[0] if valid_squares else None
    
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # Update the board with the sensed squares and pieces
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # Find the square of the opponent's king
        enemy_king_square = self.board.king(self.opponent_color)
        if enemy_king_square is not None:
            # Find all the pieces of the bot's color that are attacking the opponent's king
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                # If there are any attackers, capture the piece attacking the opponent's king
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # If the bot is playing as white
        if self.color == chess.WHITE:
            # If there are predefined moves available
            if self.move_number < len(self.white_move):
                self.move_number += 1
                # If the predefined move is in the list of legal moves
                if self.white_move[self.move_number-1] in move_actions:
                    return self.white_move[self.move_number - 1]
                else:
                    self.move_number = 10
            else:
                # Use Stockfish Engine for move analysis
                try: 
                    self.board.turn = self.color
                    if self.board.is_valid():
                        result = self.engine.play(self.board, chess.engine.Limit(time=1))
                        # If the move suggested by Stockfish is in the list of legal moves
                        if result.move in move_actions:
                            return result.move
                    else:
                        return random.choice(move_actions)
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))
        else: # If the bot is playing as black
            if self.move_number < len(self.black_move):
                self.move_number += 1
                # If the predefined move is in the list of legal moves
                if self.black_move[self.move_number-1] in move_actions:
                    return self.black_move[self.move_number - 1]
                else:
                    self.move_number = 10
            else:
                # Use Stockfish Engine for move analysis
                self.move_number += 1
                try:
                    if self.board.is_valid():
                        result = self.engine.play(self.board, chess.engine.Limit(time=1))
                        # If the move suggested by Stockfish is in the list of legal moves
                        if result.move in move_actions:
                            return result.move                    
                    return random.choice(move_actions)
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))

        # If Stockfish doesn't provide a valid move, bot chooses a random move from the list of legal moves (move_actions) or returns None if no legal moves are available.        
        return random.choice(move_actions)      

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # Push a null move onto the stack to maintain game state consistency
        self.board.push(chess.Move.null())
        
        # If a move was executed, push move onto the board stack
        if taken_move is not None:
            #print(f'In handle move result, taken move:{taken_move} was successful')
            self.board.push(taken_move)
        else:
            # If no move was executed, push another null move onto the board stack
            self.board.push(chess.Move.null()) 
                
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        # Quit the engine
        self.engine.quit()