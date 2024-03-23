import copy

import constants as c
import database.my_connect as my
import helpers
from review_session import ReviewSession, QuickReviewSession
import random


def main():
    while True:
        action = helpers.get_user_action(c.MAIN_MENU)
        if action == 1:
            add_flashcards()
        elif action == 2:
            review_flashcards()
        elif action == 3:
            review_flashcards(quick_review=True)
        elif action == 4 or action == '':
            return


def add_flashcards() -> None:
    print("*" * 100 + "\n")
    print("Enter 'q' or 'quit' at any time to exit card_creation\n")
    exit_words = ('q', 'quit')

    new_flashcards = []
    while True:
        category = helpers.get_user_action(c.CATEGORY_MENU)
        if category == 10:
            break

        english_word = input("Enter the English word: ")
        if english_word in exit_words:
            break

        spanish_word = input("Enter the Spanish translation: ")
        if spanish_word in exit_words:
            break

        spanish_example1 = input("Enter example sentence 1 (optional): ")
        if spanish_example1 in exit_words:
            break

        flashcard = {'category': category,
                     'english_word': english_word,
                     'spanish_word': spanish_word,
                     'spanish_example1': spanish_example1
                     }
        print("")
        new_flashcards.append(flashcard)

    if new_flashcards:
        new_flashcards = remove_duplicates(new_flashcards)
        add_flashcards_to_database(new_flashcards)

    return


def remove_duplicates(new_flashcards: list[dict]) -> list:
    all_existing_flashcards = get_all_existing_flashcards()

    all_english_words = [card['english_word'] for card in all_existing_flashcards]
    all_spanish_words = [card['spanish_word'] for card in all_existing_flashcards]

    for new_card in new_flashcards:
        if new_card['english_word'] in all_english_words:
            print(f'{c.YELLOW}Card already exists for {new_card["english_word"]}{c.RESET}')
            new_flashcards.remove(new_card)
        elif new_card['spanish_word'] in all_spanish_words:
            print(f'{c.YELLOW}Card already exists for {new_card["spanish_word"]}{c.RESET}')
            new_flashcards.remove(new_card)

    return new_flashcards


def update_reviewed_date(session: ReviewSession) -> None:
    if not session.answered_correctly_ids:
        return

    conn = my.get_connection()
    update = f"""UPDATE spanish_vocab.vocab SET last_reviewed = CURRENT_TIMESTAMP
                 WHERE id IN ({','.join(['%s'] * len(session.answered_correctly_ids))})"""
    params = (*session.answered_correctly_ids,)
    my.update(conn, update, params)
    conn.close()
    return


def get_flashcards(session: ReviewSession) -> list[dict]:
    # TODO move this functionality somehow to the session classes
    conn = my.get_connection()
    if session.review_method == 4:
        query = """SELECT * FROM spanish_vocab.missed"""
        flashcards = my.get_response_object(conn, query)
        conn.close()
        return flashcards
    else:
        query = """SELECT * FROM spanish_vocab.vocab"""
        flashcards = my.get_response_object(conn, query)
        conn.close()
        flashcards = filter_flashcards_by_session_options(flashcards, session)

    if type(session) == QuickReviewSession:
        count = c.QR_CARD_COUNT
    else:
        count = get_number_of_cards(flashcards)

    return flashcards[:count]


def filter_flashcards_by_session_options(flashcards: list[dict], session: ReviewSession) -> list[dict]:
    flashcards = sort_by_review_method(flashcards, session)
    flashcards = filter_by_category(flashcards, session)
    return flashcards


def filter_by_category(flashcards: list[dict], session: ReviewSession) -> list[dict]:
    if session.category != 1:
        flashcards = [card for card in flashcards if card['category'] == session.category]

    if session.category != 9:
        flashcards = [card for card in flashcards if card['category'] != 9]

    return flashcards


def sort_by_review_method(flashcards: list[dict], session: ReviewSession) -> list[dict]:
    if session.review_method == 1:
        flashcards.sort(key=lambda card: (card['last_reviewed'], -card['times_missed']))
    elif session.review_method == 2:
        flashcards.sort(key=lambda card: card['date_added'], reverse=True)
    elif session.review_method == 3:
        flashcards.sort(key=lambda card: card['times_missed'], reverse=True)
    elif session.review_method == 5:
        flashcards.sort(key=lambda card: card['date_added'], reverse=True)
        most_recent_add_date = flashcards[0]['date_added'].date()
        flashcards = [card for card in flashcards if card['date_added'].date() == most_recent_add_date]
    elif session.review_method == 6:
        # The 'or 1' here avoids ZeroDivisionErrors for cards that haven't been reviewed yet at all
        flashcards.sort(key=lambda card: card['times_missed'] / (card['review_count'] or 1), reverse=True)

    return flashcards


def get_all_existing_flashcards() -> list[dict]:
    conn = my.get_connection()
    query = """SELECT * FROM spanish_vocab.vocab"""
    all_flashcards = my.get_response_object(conn, query)
    conn.close()

    return all_flashcards


def add_flashcards_to_database(new_flashcards: list) -> None:
    conn = my.get_connection()
    insertion = """INSERT INTO spanish_vocab.vocab
            (english_word, spanish_word, spanish_example1, category)
            VALUES (%s, %s, %s, %s)"""

    params_list = []
    for card in new_flashcards:
        parameter_set = (card['english_word'], card['spanish_word'], card['spanish_example1'] or None, card['category'])
        params_list.append(parameter_set)

    cursor = conn.cursor()
    cursor.executemany(insertion, params_list)
    conn.commit()
    conn.close()
    return


def store_missed_cards(session: ReviewSession) -> None:
    if not session.missed_ids:
        return

    conn = my.get_connection()
    query = f"""INSERT INTO spanish_vocab.missed (
                        SELECT id, english_word, spanish_word, spanish_example1, spanish_example2, spanish_example3
                        FROM spanish_vocab.vocab WHERE id IN ({','.join(['%s'] * len(session.missed_ids))})
                        )"""
    params = (*session.missed_ids,)
    my.insert(conn, query, params)
    conn.close()
    return


def update_times_correct(session: ReviewSession) -> None:
    if not session.answered_correctly_ids:
        return

    conn = my.get_connection()
    update = f"""UPDATE spanish_vocab.vocab SET times_correct = times_correct + 1
                 WHERE id IN ({','.join(['%s'] * len(session.answered_correctly_ids))})"""
    params = (*session.answered_correctly_ids,)
    my.update(conn, update, params)
    conn.close()
    return None


def update_review_count(session: ReviewSession) -> None:
    reviewed_ids = session.missed_ids + session.answered_correctly_ids
    if not reviewed_ids:
        return

    conn = my.get_connection()
    update = f"""UPDATE spanish_vocab.vocab SET review_count = review_count + 1
                 WHERE id IN ({','.join(['%s'] * len(reviewed_ids))})"""
    params = (*reviewed_ids,)
    my.update(conn, update, params)
    conn.close()
    return None


def update_times_missed(session: ReviewSession) -> None:
    if not session.missed_ids:
        return

    conn = my.get_connection()
    update = f"""UPDATE spanish_vocab.vocab SET times_missed = times_missed + 1
                 WHERE id IN ({','.join(['%s'] * len(session.missed_ids))})"""
    params = (*session.missed_ids,)
    my.update(conn, update, params)
    conn.close()
    return None


def clear_missed(session: ReviewSession) -> None:
    if not session.answered_correctly_ids:
        return

    conn = my.get_connection()
    deletion = f"""DELETE FROM spanish_vocab.missed
                    WHERE id = %s
                    LIMIT 1"""
    param_list = [(card_id,) for card_id in session.answered_correctly_ids]
    cursor = conn.cursor()
    cursor.executemany(deletion, param_list)
    conn.commit()
    conn.close()
    return


def get_prompt_examples(flashcard: dict) -> str:
    prompt_examples = ''
    if flashcard['spanish_example1']:
        prompt_examples += f'Example 1: {flashcard["spanish_example1"]}\n'
    if flashcard['spanish_example2']:
        prompt_examples += f'Example 2: {flashcard["spanish_example2"]}\n'
    if flashcard['spanish_example3']:
        prompt_examples += f'Example 3: {flashcard["spanish_example3"]}\n'

    return prompt_examples


def review_flashcards(quick_review: bool = False) -> None:
    if quick_review:
        session = QuickReviewSession()
    else:
        session = ReviewSession()

    session.flashcards = get_flashcards(session)
    count = len(session.flashcards)

    # To be used to quickly repeat the same review
    flashcards_copy = copy.deepcopy(session.flashcards)

    while True:
        flashcard = random.choice(session.flashcards)
        print(f"{c.RED}{session.current_card_count}/{count}{c.RESET}")
        if answer_is_correct(flashcard, session.card_order):
            print(f"{c.GREEN}Correct! {flashcard['english_word']} = {flashcard['spanish_word']}\n{c.RESET}")
            session.answered_correctly_ids.append(flashcard['id'])
        else:
            print(f"{c.RED}Incorrect! {flashcard['english_word']} = {flashcard['spanish_word']}\n{c.RESET}")
            session.missed_ids.append(flashcard['id'])

        session.flashcards.remove(flashcard)
        session.current_card_count += 1

        if session.flashcards:
            continue
        else:
            print(f"\n\nYou answered {c.RED}{len(session.answered_correctly_ids)}/{count}{c.RESET} correctly!\n")
            end_review_session(session)

        if wants_to_repeat_review():
            session = reset_session_with_same_options(session, flashcards_copy)
            count = len(session.flashcards)
        else:
            break

    return


def reset_session_with_same_options(session: ReviewSession, flashcards: list) -> ReviewSession:
    """This function resets a ReviewSession, so the same cards can be reviewed again without re-selected all the
    options."""
    session.flashcards = copy.deepcopy(flashcards)
    session.missed_ids = []
    session.answered_correctly_ids = []
    session.current_card_count = 1
    return session


def end_review_session(session: ReviewSession) -> None:
    update_review_count(session)
    update_times_missed(session)
    update_times_correct(session)
    store_missed_cards(session)
    update_reviewed_date(session)

    if session.review_method == 4:
        clear_missed(session)
    return


def answer_is_correct(flashcard: dict, card_order: int) -> bool:
    if card_order == 1:
        front = flashcard['english_word']
        back = flashcard['spanish_word']
    elif card_order == 2:
        front = flashcard['spanish_word']
        back = flashcard['english_word']
    else:
        front = random.choice([flashcard['spanish_word'], flashcard['english_word']])
        back = flashcard['spanish_word'] if front == flashcard['english_word'] else flashcard['english_word']

    prompt = f"{c.CYAN}{front}{c.RESET}\n"
    prompt += get_prompt_examples(flashcard)

    answer = input(prompt + "Answer: ")
    if answer and answer.strip().lower() in back:
        return True
    else:
        return False


def get_number_of_cards(flashcards: list) -> int:
    while True:
        count = input(f"\nHow many cards would you like to review? Max {len(flashcards)}: ")
        if not count.isnumeric():
            print(f"{c.RED}Please enter an integer!{c.RESET}\n")
        elif not 0 < int(count) <= len(flashcards):
            print(f"{c.RED}Choose a number between 0 and {len(flashcards)}!")
        else:
            return int(count)


def wants_to_repeat_review() -> bool:
    to_continue = input("Would you like to review these cards again? ")
    if to_continue.lower() in ('y', 'yes'):
        return True
    else:
        print('\n\n\n')
        return False


if __name__ == '__main__':
    main()
