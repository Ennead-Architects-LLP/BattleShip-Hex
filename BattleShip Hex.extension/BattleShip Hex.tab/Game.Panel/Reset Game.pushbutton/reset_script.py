
import GAME_RULE
import CAMERA


def reset_game():
    GAME_RULE.reset_map()
    CAMERA.return_to_title_screen()


if __name__ == "__main__":
    reset_game()
