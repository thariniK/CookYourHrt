import requests
from bs4 import BeautifulSoup as soup
import json

global parse_url

def getPageSource(url):
    res = requests.get(url)
    return res.text


def extractSchemaJson(html):
    page_soup = soup(html, 'html.parser')
    data = page_soup.find("script", {"type": "application/ld+json"})
    oJson = json.loads("".join(data.contents))
    return oJson


def refineSchema(data, isGraph=None):
    global parse_url
    recipeData = False
    refinedData = dict()
    if (isGraph):
        for value in data['@graph']:
            if value['@type'] == 'Recipe':
                recipeData = value
    else:
        if data['@type'] == 'Recipe':
            recipeData = data
    if len(data) == 0:
        return False
    refinedData['name'] = recipeData['name']
    refinedData['url'] = recipeData['url'] if 'url' in recipeData else parse_url
    refinedData['recipeIngredient'] = list(map(str.strip, recipeData['recipeIngredient'])) if 'recipeIngredient' in recipeData else None
    refinedData['datePublished'] = recipeData['datePublished'] if 'datePublished' in recipeData else None
    refinedData['prepTime'] = recipeData['prepTime'] if 'prepTime' in recipeData else None
    refinedData['cookTime'] = recipeData['cookTime'] if 'cookTime' in recipeData else None
    refinedData['totalTime'] = recipeData['totalTime'] if 'totalTime' in recipeData else None
    refinedData['recipeYield'] = recipeData['recipeYield'] if 'recipeYield' in recipeData else None

    #image
    if 'image' in recipeData:
        if isinstance(recipeData['image'], dict):
            refinedData['image'] = recipeData['image']['url'] if 'url' in recipeData['image'] else None
    else:
        refinedData['image'] = recipeData['image'] if 'image' in recipeData else None
    
    #autor
    if 'author' in recipeData:
        if isinstance(recipeData['author'], dict):
            refinedData['author'] = recipeData['author']['name'] if 'name' in recipeData['author'] else None
    else:
        refinedData['author'] = recipeData['author'] if 'author' in recipeData else None

    #recipeInstructions
    if 'recipeInstructions' in recipeData and (isinstance(recipeData['recipeInstructions'], dict) or isinstance(recipeData['recipeInstructions'], list)):
        refinedData['recipeInstructions'] = []
        for instruction in recipeData['recipeInstructions']:
            if 'text' in instruction:
                refinedData['recipeInstructions'].append(instruction['text'].strip())
    elif 'recipeInstructions' in recipeData and isinstance(recipeData['recipeInstructions'], str):
        refinedData['recipeInstructions'] = []
        if "ol" in refinedData['recipeInstructions'] or "ul" in refinedData['recipeInstructions']:
            html_soup = soup(refinedData['recipeInstructions'], "html.parser")
            ultag = html_soup.find('ul')
            oltag = html_soup.find('ol')
            print(oltag)
            if ultag != None:
                for litag in ultag.find_all('li'):
                    refinedData['recipeInstructions'].append((litag.text).strip())
            elif oltag != None:
                for litag in oltag.find_all('li'):
                    print(litag)
                    refinedData['recipeInstructions'].append((litag.text).strip())
        elif "\n" in refinedData['recipeInstructions']:
            refinedData['recipeInstructions'] = list(map(str.strip, refinedData['recipeInstructions'].split("\n")))
        else:
            refinedData['recipeInstructions'] = [recipeData['recipeInstructions']]
    else:
        refinedData['recipeInstructions'] = None

    #keywords
    if 'keywords' in recipeData and isinstance(recipeData['keywords'], str):
        refinedData['keywords'] = list(map(str.strip, recipeData['keywords'].split(',')))
    elif 'keywords' in recipeData and (isinstance(recipeData['keywords'], dict) or isinstance(recipeData['keywords'], list)):
        refinedData['keywords'] = list(map(str.strip, recipeData['keywords']))
    else:
        refinedData['keywords'] = None
    return refinedData


def transformSchemaToResponse(data):
    return data


def extractData(url):
    global parse_url
    parse_url = url
    html = getPageSource(url)
    data = extractSchemaJson(html)
    if len(data) == 0:
        return False
    if "@graph" in data:
        refinedData = refineSchema(data, True)
    else:
        refinedData = refineSchema(data)
    if len(refinedData) != 0:
        finalResult = transformSchemaToResponse(refinedData)
    else:
        return False
    return finalResult