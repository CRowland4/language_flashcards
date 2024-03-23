import database.my_connect as my
import helpers
import constants


conn = my.get_connection()
query = """SELECT * FROM spanish_vocab.vocab WHERE category = 1"""
flashcards = my.get_response_object(conn, query)
conn.close()


params = []
for card in flashcards:
    print(f"{constants.YELLOW}*** CARD ***\n{card['spanish_word']} --- {card['english_word']}{constants.RESET}\n\n")
    category = helpers.get_user_action(constants.CATEGORY_MENU)
    print('\n\n')
    params.append((category, card['id']))


update = """UPDATE spanish_vocab.vocab SET category = %s where id = %s"""

conn = my.get_connection()
cursor = conn.cursor()
cursor.executemany(update, params)
conn.commit()
conn.close()
