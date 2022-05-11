from chat_bot import run_bot
from config import TOKEN_VK, DB_NAME
from db import DB
from vk_info import VkInfo


def main():
    db.create_table()
    run_bot(vk, db)


if __name__ == '__main__':
    vk = VkInfo(TOKEN_VK)
    db = DB(DB_NAME)

    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        db.close()
