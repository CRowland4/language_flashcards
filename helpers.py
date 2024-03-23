import constants


def get_user_action(menu: dict) -> int:
    while True:
        print("\n" + constants.YELLOW, "*" * 100, constants.RESET + "\n")
        for key, value in menu.items():
            print(f"{key}: {value}")
        choice = input("\nEnter the number of the option you would like: ")
        if choice in [str(key) for key in menu.keys()]:
            return int(choice)
        else:
            print("Please choose an integer corresponding to one of the choices!\n")
            continue
