import random
from datetime import datetime
from pprint import pprint

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import TOKEN_BOT
from db import insert_data, insert_user_to_db, is_user_in_db

vk_bot = vk_api.VkApi(token=TOKEN_BOT)
longpoll = VkLongPoll(vk_bot)


def get_client_info(vk, user_id):
    params = {
        'user_ids': user_id,
        'fields': 'age, sex, city, relation, bdate',
    }
    rs = vk.execute_method('users.get', params)
    try:
        profile_info = rs.json()['response'][0]
    except :
        return None


    # todo проверяем ответ от VK есть ли такой пользователь
    # если пользователя нет, то возвращаем из функции None
    # return None

    client_info = {
        'sex': profile_info['sex'],
        'bdate': profile_info['bdate'],
        'city': profile_info['city']['id'],
        'relation': profile_info['relation'],
        'client_user_id': profile_info['id']
    }

    return client_info


def get_match(vk, db, client_info):
    bdate = client_info['bdate']
    year = int(bdate.split('.')[-1])
    current = datetime.now().year
    age = current - year

    if client_info['sex'] == 1:
        match_sex = 2
    else:
        match_sex = 1

    params = {
        'sex': match_sex,
        'city': client_info['city'],
        'status': client_info['relation'],
        'has_photo': 1,
        'age_from': age,
        'age_to': age,
        'count': 100
    }
    rs = vk.execute_method('users.search', params)
    users = rs.json()['response']['items']

    while True:
        user = random.choice(users)
        if user['is_closed']:
            continue
        if not is_user_in_db(db, user['id'], client_info['client_user_id']):
            break

    user_info = {
        'sex': match_sex,
        'age': age,
        'city': client_info['city'],
        'relation': client_info['relation'],
        'user_id': user['id']
    }
    insert_user_to_db(db, client_info, user['id'])
    return user_info


def get_photos(vk, match_user_id):
    params = {
        'owner_id': match_user_id['user_id'],
        'album_id': 'profile',
        'extended': 1,
        'count': 100
    }
    rs = vk.execute_method('photos.get', params)
    photos_info = rs.json()['response']['items']

    photos = []
    for photo_info in photos_info:
        photo = {
            'url': photo_info['sizes'][-1]['url'],
            'rank': photo_info['likes']['count'] + photo_info['comments']['count']
        }
        photos.append(photo)

    sorted_photos = sorted(photos, key=lambda photo: photo['rank'], reverse=True)
    photo_urls = [item['url'].split('//')[-1] for item in sorted_photos[:3]]
    return photo_urls


def write_msg(chat_id, message):
    vk_bot.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id': 0})


def run_bot(vk, db):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            chat_id = event.chat_id
            # write_msg(chat_id,'Приветствую тебя!\n Если ты зашел в беседу и мне написал, значит ты одинок и хочешь найти себе пару. '
            #                   '\n Чтобы начать напиши привет')
            if request == "привет":
                write_msg(chat_id,
                          'Ищем пару?')
            elif request == "да":
                write_msg(chat_id,
                          'Я тебе помогу!!! Для этого тебе необходимо ввести свой id:')
            else:
                # todo проверка user_name()
                client_info = get_client_info(vk, request)
                if client_info is None:
                    write_msg(chat_id, 'Не правильно введен айди. Попробуйте еще раз')
                    continue
                match_user = get_match(vk, db, client_info)
                photo_urls = get_photos(vk, match_user)
                insert_data(db, match_user, photo_urls)
                write_msg(chat_id, 'https://vk.com/id' + f'{match_user["user_id"]}')
                photo_url = '\n'.join(photo_urls)
                write_msg(chat_id, f'{photo_url}')
