import constants as c
import helpers


class ReviewSession:
    def __init__(self):
        # For tracking flashcards
        self.flashcards = []
        self.missed_ids = []
        self.answered_correctly_ids = []
        self.current_card_count = 1

        # Type of review
        self.review_method = helpers.get_user_action(c.REVIEW_METHOD_MENU)
        self.card_order = helpers.get_user_action(c.CARD_ORDER_MENU)

        if self.review_method != 4:
            self.category = helpers.get_user_action(c.CATEGORY_MENU)


class QuickReviewSession:
    def __init__(self):
        self.flashcards = []
        self.missed_ids = []
        self.answered_correctly_ids = []
        self.current_card_count = 1

        # Type of review
        self.review_method = c.QR_METHOD
        self.card_order = c.QR_CARD_ORDER
        self.category = c.QR_CATEGORY
