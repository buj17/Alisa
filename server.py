from __future__ import annotations

import logging
from typing import Any

from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

session_storage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {repr(request.json)}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    return jsonify(response)


def handle_dialog(req: dict[str, Any], response: dict[str, Any]):
    user_id = req['session']['user_id']

    if req['session']['new']:
        session_storage[user_id] = {
            'suggests': [
                'Не хочу.',
                'Не буду.',
                'Отстань!'
            ]
        }

        response['response']['text'] = 'Привет! Купи слона'
        response['response']['buttons'] = get_suggests(user_id)

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        response['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        response['response']['end_session'] = True
        return

    else:
        response['response']['text'] = 'Все говорят "{}", а ты купи слона!'.format(req['request']['original_utterance'])
        response['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id: int):
    session = session_storage[user_id]

    suggests: list[dict[str, Any]] = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    session_storage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            'title': 'Ладно',
            'url': 'https://market.yandex.ru/search?text=слон',
            'hide': True
        })

    return suggests


if __name__ == '__main__':
    app.run()
