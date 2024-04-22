import chess

# Function to check if a state is consistent with the window observation
def is_consistent_with_window(fen: str, sense_window: str):
    board = chess.Board(fen)  # Initialize chess board with FEN string
    squares = sense_window.split(";")  # Split the window description into individual squares

    for square_str in squares:
        square_info = square_str.split(":")  # Split square information into location and piece
        square_location = chess.parse_square(square_info[0])
        if square_info[1] == "?":  # If the piece is unknown
            if board.piece_at(square_location) is not None:
                return False  # Return False if there is a piece on the square
        else:  # If the piece is known
            if board.piece_at(square_location).symbol() != square_info[1]:
                return False  # Return False if the piece on the square does not match the observed piece

    return True  # Return True if all squares are consistent with the observation

def main():
    input_num_states = int(input()) 
    input_fen_states = []

    for _ in range(input_num_states):
        input_fen_str = input()
        input_fen_states.append(input_fen_str)

    input_sense_window = input() 

    input_fen_states.sort()  
    for state_fen in input_fen_states:
        if is_consistent_with_window(state_fen, input_sense_window):
            print(state_fen) 

if __name__ == "__main__":
    main()
