import random
from reconchess import *
import chess.engine

class ImprovedBot(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_color = None
        
        self.my_piece_captured_square = None
        self.move_number = 0

        # Predefined moves for white and black
        self.white_move = [chess.Move.from_uci("b1c3")]
        self.white_move.append(chess.Move.from_uci("c3b5"))
        self.white_move.append(chess.Move.from_uci("b5d6"))
        self.white_move.append(chess.Move.from_uci("d6e8"))
        
        self.black_move = [chess.Move.from_uci("b8c6")]
        self.black_move.append(chess.Move.from_uci("c6b4"))
        self.black_move.append(chess.Move.from_uci("b4d3"))
        self.black_move.append(chess.Move.from_uci("d3e1"))
        
        # Path to stockfish executable
        stockfish_path = 'stockfish/stockfish.exe'

        # Initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color
        
        if self.color == chess.WHITE:
            self.opponent_color = chess.BLACK
        else:
            self.opponent_color = chess.WHITE
        
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # If the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        opponent_piece_squares = [square for square, piece in self.board.piece_map().items() if piece.color == self.opponent_color]
        
        # Prioritize sensing opponent's pieces
        for square in sense_actions:
            if square in opponent_piece_squares:
                return square
        
        # If no opponent's pieces are nearby, prioritize strategic squares based on predefined moves
        if self.color == chess.WHITE:
            for move in self.white_move:
                if move.to_square in sense_actions:
                    return move.to_square
        else:
            for move in self.black_move:
                if move.to_square in sense_actions:
                    return move.to_square
        
        # If no predefined moves apply, sense any remaining square randomly
        return random.choice(sense_actions)
    
    '''
    In this implementation, we first identify squares containing opponent's pieces and prioritize sensing those squares.
    If no opponent's pieces are nearby, we then check if there are any squares in the predefined moves (self.white_move 
    or self.black_move) that can be sensed. If such squares exist, we prioritize sensing them. If none of the predefined
    moves apply, we randomly choose a square to sense from the remaining available options.
    '''
    
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # Add changes to board, if any
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        enemy_king_square = self.board.king(self.opponent_color) # Finds the square of the opponents king
        print("Enemy king square is", enemy_king_square)
        if enemy_king_square != None: # Checks if the opponent's king is on the board

            #----- if there are any ally pieces that can take king, execute one of those moves ------
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square) # Finds all the pieces of the bot's colour that are attacking the oppponent's king
            if enemy_king_attackers: # Checks if theres any attackers
                print("Attacking enemy king")
                attacker_square = enemy_king_attackers.pop() # Retrievs one of the squares from which the bot's pieces are attacking the opponent's king
                #self.board.push(chess.Move(attacker_square, enemy_king_square))
                return chess.Move(attacker_square, enemy_king_square) # Returns a move that captures the piece attacking the opponent's king

        if self.color == chess.WHITE: # checks if it's playing as white or black and executes predefined moves stored in self.white_move or self.black_move
            # If no predefined moves are available or executed, bot utilises Stockfish Engine to analyse board position and suggest a move    
            if self.move_number < len(self.white_move):
                print(self.move_number)
                self.move_number += 1
                print(self.white_move[self.move_number - 1])
                #self.board.push(self.white_move[self.move_number - 1])
                if(self.white_move[self.move_number-1] in move_actions):
                    return self.white_move[self.move_number - 1]
                else:
                    self.move_number = 10
            else:
                # Stockfish Engine Analysis
                try: 
                    self.board.turn = self.color
                    #self.board.clear_stack()
                    print(self.board) 
                    if(self.board.is_valid()):
                        result = self.engine.play(self.board, chess.engine.Limit(time=1))
                        print(result.move)
                        # Check if move is in move_actions
                        if result.move in move_actions:
                            return result.move
                    else:
                        return random.choice(move_actions)
                        
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))
                
        else:
            if self.move_number < len(self.black_move):
                print(self.board)
                self.move_number += 1
                print(self.black_move[self.move_number - 1])
                #self.board.push(self.black_move[self.move_number - 1])
                if(self.black_move[self.move_number-1] in move_actions):
                    return self.black_move[self.move_number - 1]
                else:
                    self.move_number = 10

            else:
                # Stockfish Engine Analysis
                self.move_number += 1
                print(self.board)
                try:
                    print("Board valid - ", self.board.is_valid())
                    if(self.board.is_valid()):
                        result = self.engine.play(self.board, chess.engine.Limit(time=1))
                        print(result)
                        # Check if move is in move_actions
                        if result.move in move_actions:
                            return result.move                        
                    
                    return random.choice(move_actions)
                    
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))

        return random.choice(move_actions) # If Stockfish doesn't provide a valid move, bot chooses a random move from the list of legal moves (move_actions) or returns None if no legal moves are available.        

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if taken_move is not None: # Checks if a move was successfuly executed
            print(f'In handle move result, taken move:{taken_move} was successuful')
            self.board.push(chess.Move.null()) # Push a null move onto the stack to maintain game state consistency
            self.board.push(taken_move) # If a move was executed, push move onto the board stack
        else:
            self.board.push(chess.Move.null()) # Push a null move onto the board stack
            self.board.push(chess.Move.null()) 
                
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        self.engine.quit()