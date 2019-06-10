#! /usr/bin/env python3
# Someone on Wikipedia shortened "Disney Channel Original Movie" to DCOM
# and now I will do the same and you will suffer for it. Also it sounds
# kinda technical even though this is the furthest thing from good tech.

import bs4
import logging
import random
import re
import requests

CATEGORY_TITLE = "Category:Disney Channel Original Movie films"
WIKI_API = "https://en.wikipedia.org/w/api.php"
CITATION_REGEX = re.compile(r'\[\d+\]')

logger = logging.getLogger('DCOM')


def get_random_dcom():
    """Return the Wikipedia page for a random Disney Channel Original Movie."""
    params = {
        'action': "query",
        'list': "categorymembers",
        'cmtitle': CATEGORY_TITLE,
        'cmlimit': 200,
        'format': "json"
    }
    result = requests.get(WIKI_API, params)
    if result.status_code != 200:
        # IDK error handling sounds nice
        logger.critical("Error fetching movies from Wikipedia: {}", result)
        raise Exception
    # This also is a place where maybe there would be errors. YOLO
    pages = result.json()['query']['categorymembers']
    # NS 0 is normal Wikipedia. The other things returned are subcategories
    # TODO(dylan): films in subcategories are still DCOMs and we're missing
    # some of them! It appears many films are in both the main category and a
    # subcategory, so for instance, we have no danger of missing "High School
    # Musical 2" (and would in fact have it at least twice if we checked
    # subcategories), but we miss "High School Musical 3: Senior Year"
    films = [page for page in pages if page['ns'] == 0]

    # Return a random film.
    # TODO: filter out films that were made recently
    # XXX They made a live action Kim Possible movie. This software occasionally
    # will report the existence of that film. This is a violation of the Geneva
    # Convention, I think.
    return random.choice(films)


def _get_lede(page_id):
    params = {
        'action': "parse",
        'format': "json",
        'pageid': page_id,
        'prop': "text",
        'section': 0,
    }
    result = requests.get(WIKI_API, params)
    if result.status_code != 200:
        # IDK error handling sounds nice
        logger.critical("Error fetching page {} from Wikipedia: {}", page_id,
                        result)
        raise Exception
    returned_html = result.json()['parse']['text']['*']
    soup = bs4.BeautifulSoup(returned_html)
    # Get every paragraph
    paragraphs = [p.getText().strip() for p in soup.find_all('p')]
    # Filter out empty paragraphs and citation tags
    paragraphs = [CITATION_REGEX.sub("", p) for p in paragraphs if p.strip()]
    # Return the first non empty paragraph
    return paragraphs[0]


def _get_plot(page_id):
    # TODO similar to get lede code should merge
    params = {
        'action': "parse",
        'format': "json",
        'pageid': page_id,
        'prop': "text",
        'section': 1,
    }
    result = requests.get(WIKI_API, params)
    if result.status_code != 200:
        # IDK error handling sounds nice
        logger.critical("Error fetching page {} from Wikipedia: {}", page_id,
                        result)
        raise Exception
    returned_html = result.json()['parse']['text']['*']
    soup = bs4.BeautifulSoup(returned_html)
    # HACK: Just see if the first section header has the word Plot in it. We
    # could try all sections but the first section is almost always the Plot
    if soup.h2.getText().find('Plot') == -1:
        # If it doesn't have the word plot throw the section away
        return None

    # Get non empty paragraphs, filtered of citation tags
    paragraphs = [p.getText().strip() for p in soup.find_all('p')]
    # Filter out empty paragraphs and citation tags
    paragraphs = [CITATION_REGEX.sub("", p) for p in paragraphs if p.strip()]

    # Add a quote
    paragraphs = ['> ' + p for p in paragraphs]

    return '\n>\n'.join(paragraphs)


def get_dcom_data(dcom):
    page_id = dcom['pageid']
    lede = _get_lede(page_id)
    plot = _get_plot(page_id)
    if plot:
        return lede + '\n\n' + plot
    else:
        return lede
