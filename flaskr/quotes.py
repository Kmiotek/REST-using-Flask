import asyncio
import functools

import aiohttp
import random as rand

from error import Error

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('quotes', __name__, url_prefix='/quotes')


async def get_response(url):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as response:
            resp = await response.json()
            if response.status != 200:
                raise Error(response.status,
                            "Couldn't get a quote. Most likely servers are down.")
            return resp


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()
        error = None

        if not name:
            error = 'PLease enter a name and a surname.'

        if error is None:
            url = f'https://programming-quotes-api.herokuapp.com/quotes/author/{name}'
            asyncio.set_event_loop(asyncio.new_event_loop())
            response = asyncio.run(get_response(url))
            if len(response) < 1:
                raise Error(727,
                            "Couldn't get a quote. There are no quotes available for this person.")
            actual = response[rand.randrange(0, len(response))]
            name2 = name.replace(' ', '%20')
            url2 = f'https://en.wikipedia.org/w/api.php?action=query&titles={name2}&prop=extracts&format=json&exintro=1'
            asyncio.set_event_loop(asyncio.new_event_loop())
            info = asyncio.run(get_response(url2))
            key = (list(info['query']['pages'].keys())[0])
            inserted_info = "This person doesn't have a site on wikipedia."
            if int(key) >= 0:
                inserted_info = info['query']['pages'][key]['extract']
            # names = name.split(' ')
            # url3 = f'https://api.hunter.io/v2/email-finder?domain=reddit.com&first_name={names[0]}&last_name' \
            #        f'={names[-1]}&api_key=612f6737ece648a633dcddc33cb0770708a137e5 '
            # email = requests.get(url3).json()
            # print(email)
            try:
                db.execute(
                    "INSERT INTO person (name, quote, image) VALUES (?, ?, ?)",
                    (actual['author'], actual['en'], inserted_info),
                )
                db.commit()

            except db.IntegrityError:
                raise Error(728, "Database error, probably database was corrupted.")
            else:
                return redirect(url_for('poke.index'))

        flash(error)

    return render_template('quotes/register.html')


@bp.route('/random', methods=('GET', 'POST'))
def random():
    db = get_db()
    url = f'https://programming-quotes-api.herokuapp.com/quotes/random'
    asyncio.set_event_loop(asyncio.new_event_loop())
    response = asyncio.run(get_response(url))
    name = response['author']
    name2 = name.replace(' ', '%20')
    url2 = f'https://en.wikipedia.org/w/api.php?action=query&titles={name2}&prop=extracts&format=json&exintro=1'
    asyncio.set_event_loop(asyncio.new_event_loop())
    info = asyncio.run(get_response(url2))
    key = (list(info['query']['pages'].keys())[0])
    inserted_info = "This person doesn't have a site on wikipedia."
    if int(key) >= 0:
        inserted_info = info['query']['pages'][key]['extract']
    try:
        db.execute(
            "INSERT INTO person (name, quote, image) VALUES (?, ?, ?)",
            (response['author'], response['en'], inserted_info),
        )
        db.commit()

    except db.IntegrityError:
        raise Error(728, "Database error, probably database was corrupted.")
    else:
        return redirect(url_for('poke.index'))
