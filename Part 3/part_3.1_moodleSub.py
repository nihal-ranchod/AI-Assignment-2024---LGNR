import chess.engine
import random
from reconchess import *

class Agent(Player):

    def __init__(self):
        # Initialize Stockfish engine
        stockfish_path = '/opt/stockfish/stockfish'
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        # Initialize variables and store own piece squares
        self.board = board
        self.color = color
        self.own_piece_squares = {square for square, piece in self.board.piece_map().items() if piece.color == self.color}

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

def main():
    fen_str = input()
    bot = Agent()
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
