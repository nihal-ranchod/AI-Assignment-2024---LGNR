
import random
from reconchess import *
import os
import chess.engine
import numpy as np

STOCKFISH_ENV_VAR = 'stockfish/stockfish.exe'
class BotOne(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.opponent_color = None
        
        self.my_piece_captured_square = None
        self.move_number = 0

        # self.white_move = [chess.Move.from_uci("e2e4")]
        # self.white_move.append(chess.Move.from_uci("d1h5"))
        # self.white_move.append(chess.Move.from_uci("f1c4"))
        # self.white_move.append(chess.Move.from_uci("h5f7"))
        
        # self.black_move = [chess.Move.from_uci("e7e5")]
        # self.black_move.append(chess.Move.from_uci("d8h4"))
        # self.black_move.append(chess.Move.from_uci("f8c5"))
        # self.black_move.append(chess.Move.from_uci("h4f2"))
        
        
        self.white_move = [chess.Move.from_uci("b1c3")]
        self.white_move.append(chess.Move.from_uci("c3b5"))
        self.white_move.append(chess.Move.from_uci("b5d6"))
        self.white_move.append(chess.Move.from_uci("d6e8"))
        
        self.black_move = [chess.Move.from_uci("b8c6")]
        self.black_move.append(chess.Move.from_uci("c6b4"))
        self.black_move.append(chess.Move.from_uci("b4d3"))
        self.black_move.append(chess.Move.from_uci("d3e1"))
        
        # check if stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'Require an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color
        
        if self.color == chess.WHITE:
            self.opponent_color = chess.BLACK
        else:
            self.opponent_color = chess.WHITE
        
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # if we might capture a piece when we move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        """sense in rows 3 and 4 of the opponent during the beginning of the game...?"""

        # sense where we predict our opponent moved during their previous turn
        if self.future_opponent_move is not None:
            return self.future_opponent_move.to_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)
        # don't sense on a square along the edge
        edges = np.array([0, 1, 2, 3, 4, 5, 6, 7,
                          8, 15, 16, 23, 24, 31, 32,
                          39, 40, 47, 48, 55, 56, 57,
                          58, 59, 60, 61, 62, 63])
        sense_actions = np.setdiff1d(sense_actions, edges)
        sense_actions = sense_actions.tolist()
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add changes to board, if any
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        enemy_king_square = self.board.king(self.opponent_color)
        print("Enemy king square is", enemy_king_square)
        if enemy_king_square != None:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                print("Attacking enemy king")
                attacker_square = enemy_king_attackers.pop()
                #self.board.push(chess.Move(attacker_square, enemy_king_square))
                return chess.Move(attacker_square, enemy_king_square)

        if self.color == chess.WHITE:
                
            if self.move_number < len(self.white_move):
                print(self.move_number)
                self.move_number += 1
                print(self.white_move[self.move_number - 1])
                #self.board.push(self.white_move[self.move_number - 1])
                if(self.white_move[self.move_number-1] in move_actions):
                    return self.white_move[self.move_number - 1]
                else:
                    self.move_number = 10
                
            # elif self.move_number == 4:
                # print("Move 4")
                # self.move_number += 1
                # if(chess.Move.from_uci('c4f7') in move_actions):
                    # move = chess.Move.from_uci('c4f7')
                    # #self.board.push(move)
                    # return move

                # elif(chess.Move(chess.F7, chess.E8) in move_actions):
                    # move = chess.Move.from_uci('f7e8')
                    # #self.board.push(move)
                    # return move
            else:
                try:
                    self.board.turn = self.color
                    #self.board.clear_stack()
                    print(self.board) 
                    if(self.board.is_valid()):
                        result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
                        print(result.move)
                        if result.move in move_actions:
                            return result.move
                    
                    return random.choice(move_actions + [None])
                        
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))
                
        else:
            if self.move_number < len(self.black_move):
                print(self.board)
                #print(self.move_number)
                self.move_number += 1
                print(self.black_move[self.move_number - 1])
                #self.board.push(self.black_move[self.move_number - 1])
                if(self.black_move[self.move_number-1] in move_actions):
                    return self.black_move[self.move_number - 1]
                else:
                    self.move_number = 10
                    
            # elif self.move_number == 4:
                # print("Move 4")
                # self.move_number += 1
                
                # if(chess.Move.from_uci('c5f2') in move_actions):
                    # move = chess.Move.from_uci('c5f2')
                    # #self.board.push(move)
                    # return move

                # elif(chess.Move.from_uci('f7e8') in move_actions):
                    # move = chess.Move.from_uci('f7e8')
                    # #self.board.push(move)
                    # return move
            else:
                self.move_number += 1
                print(self.board)
                try:
                    print("Board valid - ", self.board.is_valid())
                    if(self.board.is_valid()):
                        result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
                        print(result)
                        if result.move in move_actions:
                            return result.move                        
                    
                    move = random.choice(move_actions + [None])
                    print(move)
                        
                    return move
                except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
                    print('Engine bad state at "{}"'.format(self.board.fen()))
        return random.choice(move_actions + [None])

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if taken_move is not None:
            print("In handle move result")
            self.board.push(chess.Move.null())
            self.board.push(taken_move)
        else:
            if(requested_move != None):
                self.board.push(chess.Move.null())
                self.board.push(requested_move)
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        self.engine.quit()
