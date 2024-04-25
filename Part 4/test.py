import random
from reconchess import *
import numpy as np
import chess.engine

class ImprovedBot(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        # track opponent's captured square location
        self.opponent_piece_captured_square = None
        # track opponent's predicted future move
        self.future_opponent_move = None

        # make sure there is actually a file
        stockfish_path = 'stockfish/stockfish.exe'

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)


    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.

        # if this square is replaced with an opponent's piece, handle_sense_result will add that piece to our board 
        
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)


    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
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

    # called after choose_sense()
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            if piece is None:
                self.board.remove_piece_at(square)
            else:
                self.board.set_piece_at(square, piece)

    # called after handle_sense_result()
    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                # assume/check if this is a possible move from the list parameter:
                return chess.Move(attacker_square, enemy_king_square)

        # otherwise, try to move with the stockfish chess engine
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            return result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(self.board.fen()))

        # else, choose random move
        return random.choice(move_actions + [None])

    # called after choose_move()
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board's move stack
        if taken_move is not None:
            self.board.push(taken_move)

        # predict opponent's next move and sense there during our next turn
        try:
            self.board.turn = not self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            self.future_opponent_move = result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(self.board.fen()))

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass