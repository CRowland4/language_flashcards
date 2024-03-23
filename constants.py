import colorama

MAIN_MENU = {
    1: 'Add flashcards',
    2: 'Review flashcards',
    3: 'Quick Review',
    4: 'Quit'
}

REVIEW_METHOD_MENU = {
    1: 'Default',
    2: 'Review newest cards',
    3: 'Review most frequently missed',
    4: 'Review missed',
    5: 'Review most recent batch',
    6: 'Review by missed-to-reviewed ratio'
}

CARD_ORDER_MENU = {
    1: 'English -> Spanish',
    2: 'Spanish -> English',
    3: 'Random'
}

CATEGORY_MENU = {
    1: 'All',
    2: 'Materials',
    3: 'Tools and Weapons',
    4: 'Outdoors',
    5: 'Body and Physical Bodily Actions',
    6: 'Clothing',
    7: 'Animals',
    8: 'People',
    9: 'Infrequently used',
    10: 'Back to Main Menu'
}


# Quick Review settings
QR_METHOD = 1
QR_CARD_ORDER = 3
QR_CATEGORY = 1
QR_CARD_COUNT = 10


# Colors
RESET = colorama.Fore.RESET
BLUE = colorama.Fore.BLUE
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
CYAN = colorama.Fore.CYAN
YELLOW = colorama.Fore.YELLOW
