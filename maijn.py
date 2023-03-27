from flask import Flask, request
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

animals_list = [
    'слон',
    'кролик'
]


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'animal': 0
        }

        res['response']['text'] = 'Привет! Купи ' + animals_list[sessionStorage[user_id]['animal']] + 'a!'
        res['response']['buttons'] = get_suggests(user_id, animals_list[sessionStorage[user_id]['animal']])
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        sessionStorage[user_id]['suggests'] = [
            "Не хочу.",
            "Не буду.",
            "Отстань!",
        ]
        if sessionStorage[user_id]['animal'] == len(animals_list) - 1:
            res['response']['text'] = animals_list[sessionStorage[user_id]['animal']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['animal'] += 1
            res['response']['end_session'] = True
        else:
            res['response']['text'] = animals_list[sessionStorage[user_id]['animal']] + 'а можно найти на Яндекс.Маркете!'
            sessionStorage[user_id]['animal'] += 1
            res['response']['text'] += ' А ' + animals_list[sessionStorage[user_id]['animal']] + 'a купишь? '
            res['response']['buttons'] = get_suggests(user_id, animals_list[sessionStorage[user_id]['animal']])
        return

    res['response']['text'] = ('Все говорят "%s", а ты купи ' + animals_list[sessionStorage[user_id]['animal']] + 'а!') % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id, animals_list[sessionStorage[user_id]['animal']])


def get_suggests(user_id, animal):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=" + animal,
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
