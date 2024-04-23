import chess.engine
import chess

engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', setpgrp=True)

fen_str = "k7/p2p1p2/P2P1P2/8/8/8/8/7K b - - 23 30"
board = chess.Board(fen_str)

board.clear_stack()
result = engine.play(board, chess.engine.Limit(time=0.5))

print(result.move)

engine.quit()