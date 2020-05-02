import requests
from bs4 import BeautifulSoup as soup
import json
from Exception.custom_exceptions import NoSchemaResultSet

global parse_url

schemaDataMapping = {
    "name": "name",
    "description": "description",
    "url": "url",
    "author": "author",
    "published": "datePublished",
    "preparationTime": "prepTime",
    "cookingTime": "cookTime",
    "totalTime": "cookTime",
    "yieldsFor": "recipeYield",
    "ingredients": "recipeIngredient",
    "instructions": "recipeInstructions",
    "tags": "keywords",
    "nutrition": {
        "nutrition": {
            "calories": "calories",
            "calorieCount": "calorieContent",
            "carbohydrate": "carbohydrateContent",
            "cholesterol": "cholesterolContent",
            "fat": "fatContent",
            "fiber": "fiberContent",
            "protein": "proteinContent",
            "saturatedFat": "saturatedFatContent",
            "sodium": "sodiumContent",
            "sugar": "sugarContent",
            "transFat": "transFatContent",
            "unsaturatedFat": "unsaturatedFatContent"
        }
    }
}

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
        raise NoSchemaResultSet
    refinedData['name'] = recipeData['name']
    refinedData['description'] = recipeData['description'] if 'description' in recipeData else None
    refinedData['url'] = recipeData['url'] if 'url' in recipeData else parse_url
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
            refinedData['author'] = recipeData['author']
    else:
        refinedData['author'] = recipeData['author'] if 'author' in recipeData else None
    
    #recipeIngredient
    if 'recipeIngredient' in recipeData and (isinstance(recipeData['recipeIngredient'], dict) or isinstance(recipeData['recipeIngredient'], list)):
        refinedData['recipeIngredient'] = list(map(str.strip, recipeData['recipeIngredient']))
    elif 'recipeIngredient' in recipeData and (isinstance(recipeData['recipeIngredient'], dict) ):
        refinedData['recipeIngredient'] = list(map(str.strip, recipeData['recipeIngredient'].split(',')))
    else:
        refinedData['recipeIngredient'] = [recipeData['recipeIngredient']] if 'recipeIngredient' in recipeData else None
    if isinstance(refinedData['recipeIngredient'], dict) and len(refinedData['recipeIngredient']):
        refinedData['recipeIngredient'] = [i for i in recipeData['recipeIngredient'] if i]

    #recipeInstructions
    if 'recipeInstructions' in recipeData and (isinstance(recipeData['recipeInstructions'], dict) or isinstance(recipeData['recipeInstructions'], list)):
        refinedData['recipeInstructions'] = []
        for instruction in recipeData['recipeInstructions']:
            if 'text' in instruction:
                refinedData['recipeInstructions'].append(instruction['text'].strip())
    elif 'recipeInstructions' in recipeData and isinstance(recipeData['recipeInstructions'], str):
        refinedData['recipeInstructions'] = []
        if "<ol" in recipeData['recipeInstructions'] or "<ul" in recipeData['recipeInstructions']:
            html_soup = soup(recipeData['recipeInstructions'], "html.parser")
            ultag = html_soup.find('ul')
            oltag = html_soup.find('ol')
            if ultag != None:
                for litag in ultag.find_all('li'):
                    refinedData['recipeInstructions'].append((litag.text).strip())
            elif oltag != None:
                for litag in oltag.find_all('li'):
                    refinedData['recipeInstructions'].append((litag.text).strip())
            else:
                refinedData['recipeInstructions'] = [recipeData['recipeInstructions']]
        elif "\n" in recipeData['recipeInstructions']:
            refinedData['recipeInstructions'] = list(map(str.strip, recipeData['recipeInstructions'].split("\n")))
        else:
            refinedData['recipeInstructions'] = [recipeData['recipeInstructions']]
    else:
        refinedData['recipeInstructions'] = None
    if isinstance(refinedData['recipeInstructions'], dict) and len(refinedData['recipeInstructions']):
        refinedData['recipeInstructions'] = [i for i in refinedData['recipeInstructions'] if i]

    #keywords
    if 'keywords' in recipeData and isinstance(recipeData['keywords'], str):
        refinedData['keywords'] = list(map(str.strip, recipeData['keywords'].split(',')))
    elif 'keywords' in recipeData and (isinstance(recipeData['keywords'], dict) or isinstance(recipeData['keywords'], list)):
        refinedData['keywords'] = list(map(str.strip, recipeData['keywords']))
    else:
        refinedData['keywords'] = []
    if isinstance(refinedData['keywords'], dict) and len(refinedData['keywords']):
        refinedData['keywords'] = [i for i in refinedData['keywords'] if i] if len(refinedData['keywords']) else None

    #nutrition
    if 'nutrition' in recipeData and (isinstance(recipeData['nutrition'], dict) or isinstance(recipeData['nutrition'], list)):
        refinedData['nutrition'] = dict()
        refinedData['nutrition']['calories'] = recipeData['nutrition']['calories'] if 'calories' in recipeData['nutrition'] else None
        refinedData['nutrition']['carbohydrateContent'] = recipeData['nutrition']['carbohydrateContent'] if 'carbohydrateContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['cholesterolContent'] = recipeData['nutrition']['cholesterolContent'] if 'cholesterolContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['fatContent'] = recipeData['nutrition']['fatContent'] if 'fatContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['fiberContent'] = recipeData['nutrition']['fiberContent'] if 'fiberContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['proteinContent'] = recipeData['nutrition']['proteinContent'] if 'proteinContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['saturatedFatContent'] = recipeData['nutrition']['saturatedFatContent'] if 'saturatedFatContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['servingSizevolume'] = recipeData['nutrition']['servingSizevolume'] if 'servingSizevolume' in recipeData['nutrition'] else None
        refinedData['nutrition']['sodiumContent'] = recipeData['nutrition']['sodiumContent'] if 'sodiumContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['sugarContent'] = recipeData['nutrition']['sugarContent'] if 'sugarContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['transFatContent'] = recipeData['nutrition']['transFatContent'] if 'transFatContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['unsaturatedFatContent'] = recipeData['nutrition']['unsaturatedFatContent'] if 'unsaturatedFatContent' in recipeData['nutrition'] else None
        refinedData['nutrition']['calorieContent'] = int(''.join(filter(str.isdigit, refinedData['nutrition']['calories'])))
    else:
        refinedData['nutrition'] = dict()

    return refinedData


def transformSchemaToResponse(data):
    transformedData = dict()
    for key in schemaDataMapping:
        if isinstance(schemaDataMapping[key], dict):
            transformedData[key] = dict()
            for k in schemaDataMapping[key].values():
                for j in k:
                    transformedData[key][j] = data[key][schemaDataMapping[key][key][j]] if (key in data and schemaDataMapping[key][key][j] in data[key]) else None
        else:
            transformedData[key] = data[schemaDataMapping[key]]
    return transformedData

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