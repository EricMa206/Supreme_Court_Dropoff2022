# Tic Tac Toe - 3 x 3 expandable


def display_game(gamestate):
    print("   0  1  2")
    for row, position in enumerate(game):
        print(row, position)


def win(check):
    if check[0] != 0 and check.count(check[0]) == len(check):
        print("Winner!")
        # play_again = input("Play again? y/n ")
        # if play_again == 'n'


def winstate(gamestate):
    # Horizontally
    for row in gamestate:
        win(row)
    # Vertically
    for col in range(len(gamestate)):
        column = []
        for position in gamestate:
            column.append(position[col])
        win(column)
    # Diagonal
    falling = []
    rising = []
    for row, position in enumerate(gamestate):
        falling.append(position[row])
        rev = list(reversed(position))
        rising.append(rev[row])
    win(falling)
    win(rising)


def move(gamestate, player):
    row = int(input(f"Player {player} select row 0, 1, 2: "))
    column = int(input(f"Player {player} select column 0, 1, 2: "))
    try:
        gamestate[row][column] = player
        display_game(gamestate)
        winstate(gamestate)
        return gamestate
    except IndexError as e:
        print("Please enter 0, 1, or 2", e)


game = [[1, 0, 2],
        [0, 2, 0],
        [2, 0, 1]]

display_game(game)
winstate(game)
