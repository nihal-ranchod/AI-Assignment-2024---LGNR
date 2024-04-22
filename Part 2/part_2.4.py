import chess

def valid_state_from_sense(fen: str, sense_window: str):
    board = chess.Board(fen)
    squares = sense_window.split(";")

    for square_str in squares:
        square_info = square_str.split(":")  
        square_location = chess.parse_square(square_info[0])
        if square_info[1] == "?":
            if board.piece_at(square_location) != None:
                return False
        else:
            if board.piece_at(square_location) == square_info[1]:
                return False

    return True  

def main():
    input_num_states = int(input())
    input_fen_states = []
    
    for i in range(input_num_states):
        input_fen_str = input()
        input_fen_states.append(input_fen_str)

    input_sense_window = input()

    input_fen_states.sort()
    for state_fen in input_fen_states:
        if valid_state_from_sense(state_fen, input_sense_window):
            print(state_fen)

if __name__ == "__main__":
    main()