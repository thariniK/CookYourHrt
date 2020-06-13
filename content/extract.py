import requests
from bs4 import BeautifulSoup as soup
import json
import extruct
from w3lib.html import get_base_url
from Exception.custom_exceptions import NoSchemaResultSet
from utils.strutils import striphtml, striptabs

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
	"image": "image",
	"ingredients": "recipeIngredient",
	"instructions": "recipeInstructions",
	"tags": "keywords",
	"category": "recipeCategory",
	"cuisine": "recipeCuisine",
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
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
	}
	res = requests.get(url, headers=headers)
	return res.text


def refineAllTypesRecipeData(recipeData):
	global parse_url
	refinedData = dict()
	refinedData['name'] = recipeData['name'][0] if isinstance(recipeData['name'], list) else recipeData['name']
	refinedData['description'] = recipeData['description'] if 'description' in recipeData else None
	refinedData['url'] = recipeData['url'] if 'url' in recipeData else parse_url
	refinedData['datePublished'] = recipeData['datePublished'] if 'datePublished' in recipeData else None
	refinedData['prepTime'] = recipeData['prepTime'] if 'prepTime' in recipeData else None
	refinedData['cookTime'] = recipeData['cookTime'] if 'cookTime' in recipeData else None
	refinedData['totalTime'] = recipeData['totalTime'] if 'totalTime' in recipeData else None
	refinedData['recipeYield'] = recipeData['recipeYield'] if 'recipeYield' in recipeData else None

	# image
	if 'image' in recipeData:
		if isinstance(recipeData['image'], dict):
			refinedData['image'] = recipeData['image']['url'] if 'url' in recipeData['image'] else None
		elif isinstance(recipeData['image'], list):
			refinedData['image'] = recipeData['image'][0] if len(recipeData['image']) else None
		elif isinstance(recipeData['image'], str):
			refinedData['image'] = recipeData['image']
	else:
		refinedData['image'] = None

	if 'thumbnailUrl' in recipeData:
		if isinstance(recipeData['thumbnailUrl'], dict):
			refinedData['thumbnailUrl'] = recipeData['thumbnailUrl']['url'] if 'url' in recipeData[
				'thumbnailUrl'] else None
	else:
		refinedData['thumbnailUrl'] = recipeData['thumbnailUrl'] if 'thumbnailUrl' in recipeData else None

	# author
	refinedData['author'] = []
	if 'author' in recipeData:
		if isinstance(recipeData['author'], dict) or isinstance(recipeData['author'], list):
			if isinstance(recipeData['author'], list):
				for a in recipeData['author']:
					refinedData['author'].append(a['name'] if 'name' in a else None)
			elif isinstance(recipeData['author'], dict):
				refinedData['author'].append(recipeData['author']['name'] if 'name' in recipeData['author'] else None)
			else:
				refinedData['author'].append(recipeData['author'])
		else:
			refinedData['author'].append(recipeData['author'])
	else:
		refinedData['author'] = None

	# recipeIngredient
	ingredient_key = 'recipeIngredient' if 'recipeIngredient' in recipeData else 'ingredients'
	if ingredient_key in recipeData and (
			isinstance(recipeData[ingredient_key], dict) or isinstance(recipeData[ingredient_key], list)):
		refinedData['recipeIngredient'] = list(map(str.strip, recipeData[ingredient_key]))
	elif ingredient_key in recipeData and (isinstance(recipeData[ingredient_key], str)):
		refinedData['recipeIngredient'] = list(map(str.strip, recipeData[ingredient_key].split(',')))
	else:
		refinedData['recipeIngredient'] = [recipeData[ingredient_key]] if ingredient_key in recipeData else None
	if (isinstance(refinedData['recipeIngredient'], dict) or isinstance(refinedData['recipeIngredient'], list)) and len(
			refinedData['recipeIngredient']):
		refinedData['recipeIngredient'] = [striptabs(striphtml(i)) for i in recipeData[ingredient_key] if i]

	# recipeInstructions
	if 'recipeInstructions' in recipeData and (
			isinstance(recipeData['recipeInstructions'], dict) or isinstance(recipeData['recipeInstructions'], list)):
		refinedData['recipeInstructions'] = []
		if isinstance(recipeData['recipeInstructions'][0], list):
			for instruction in recipeData['recipeInstructions'][0]:
				if isinstance(instruction, dict) and 'text' in instruction:
					refinedData['recipeInstructions'].append(instruction['text'].strip())
				elif isinstance(instruction, str):
					refinedData['recipeInstructions'].append(instruction.strip())
		else:
			for instruction in recipeData['recipeInstructions']:
				if isinstance(instruction, dict) and 'text' in instruction:
					refinedData['recipeInstructions'].append(instruction['text'].strip())
				elif isinstance(instruction, str):
					refinedData['recipeInstructions'].append(instruction.strip())
	elif 'recipeInstructions' in recipeData and isinstance(recipeData['recipeInstructions'], str):
		refinedData['recipeInstructions'] = []
		if "<ol" in recipeData['recipeInstructions'] or "<ul" in recipeData['recipeInstructions']:
			html_soup = soup(recipeData['recipeInstructions'], "html.parser")
			ultag = html_soup.find('ul')
			oltag = html_soup.find('ol')
			if ultag is not None:
				for litag in ultag.find_all('li'):
					refinedData['recipeInstructions'].append((litag.text).strip())
			elif oltag is not None:
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
	if (isinstance(refinedData['recipeInstructions'], dict) or isinstance(refinedData['recipeInstructions'], list)) and len(refinedData['recipeInstructions']):
		refinedData['recipeInstructions'] = [striptabs(striphtml(i)) for i in refinedData['recipeInstructions'] if i]

	# keywords
	if 'keywords' in recipeData and isinstance(recipeData['keywords'], str):
		refinedData['keywords'] = list(map(str.strip, recipeData['keywords'].split(',')))
	elif 'keywords' in recipeData and (
			isinstance(recipeData['keywords'], dict) or isinstance(recipeData['keywords'], list)):
		refinedData['keywords'] = list(map(str.strip, recipeData['keywords']))
	else:
		refinedData['keywords'] = []
	if isinstance(refinedData['keywords'], dict) and len(refinedData['keywords']):
		refinedData['keywords'] = [i for i in refinedData['keywords'] if i] if len(refinedData['keywords']) else None

	# category
	if 'recipeCategory' in recipeData and isinstance(recipeData['recipeCategory'], str):
		refinedData['recipeCategory'] = list(map(str.strip, recipeData['recipeCategory'].split(',')))
	elif 'recipeCategory' in recipeData and (
			isinstance(recipeData['recipeCategory'], dict) or isinstance(recipeData['recipeCategory'], list)):
		refinedData['recipeCategory'] = list(map(str.strip, recipeData['recipeCategory']))
	else:
		refinedData['recipeCategory'] = []

	# cuisine
	if 'recipeCuisine' in recipeData and isinstance(recipeData['recipeCuisine'], str):
		refinedData['recipeCuisine'] = list(map(str.strip, recipeData['recipeCuisine'].split(',')))
	elif 'recipeCuisine' in recipeData and (
			isinstance(recipeData['recipeCuisine'], dict) or isinstance(recipeData['recipeCuisine'], list)):
		refinedData['recipeCuisine'] = list(map(str.strip, recipeData['recipeCuisine']))
	else:
		refinedData['recipeCuisine'] = []

	# nutrition
	if 'nutrition' in recipeData and (
			isinstance(recipeData['nutrition'], dict) or isinstance(recipeData['nutrition'], list)):
		refinedData['nutrition'] = dict()
		refinedData['nutrition']['calories'] = recipeData['nutrition']['calories'] if 'calories' in recipeData[
			'nutrition'] else None
		refinedData['nutrition']['carbohydrateContent'] = recipeData['nutrition'][
			'carbohydrateContent'] if 'carbohydrateContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['cholesterolContent'] = recipeData['nutrition'][
			'cholesterolContent'] if 'cholesterolContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['fatContent'] = recipeData['nutrition']['fatContent'] if 'fatContent' in recipeData[
			'nutrition'] else None
		refinedData['nutrition']['fiberContent'] = recipeData['nutrition']['fiberContent'] if 'fiberContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['proteinContent'] = recipeData['nutrition']['proteinContent'] if 'proteinContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['saturatedFatContent'] = recipeData['nutrition'][
			'saturatedFatContent'] if 'saturatedFatContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['servingSize'] = recipeData['nutrition']['servingSize'] if 'servingSize' in recipeData['nutrition'] else None
		refinedData['nutrition']['sodiumContent'] = recipeData['nutrition']['sodiumContent'] if 'sodiumContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['sugarContent'] = recipeData['nutrition']['sugarContent'] if 'sugarContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['transFatContent'] = recipeData['nutrition']['transFatContent'] if 'transFatContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['unsaturatedFatContent'] = recipeData['nutrition'][
			'unsaturatedFatContent'] if 'unsaturatedFatContent' in recipeData['nutrition'] else None
		refinedData['nutrition']['calorieContent'] = int(
			''.join(filter(str.isdigit, refinedData['nutrition']['calories'])))
	else:
		refinedData['nutrition'] = dict()
	return refinedData


def extractSchemaJson(html):
	page_soup = soup(html, 'html.parser')
	extracted_data = []
	data = page_soup.find_all("script", {"type": "application/ld+json"})
	if isinstance(data, list):
		i = 0
		for d in data:
			dt = d.string
			if dt != None and isinstance(dt, str):
				jsonDt = json.loads("".join(dt), strict=False)
				if isinstance(jsonDt, list) and jsonDt[0] != None:
					for jd in jsonDt:
						extracted_data.insert(i, jd)
						i = i + 1
				else:
					extracted_data.insert(i, jsonDt)
					i = i + 1
	else:
		jsonDt = json.loads("".join(data.contents), strict=False)
		if isinstance(jsonDt, list) and jsonDt[0] != None:
			extracted_data = jsonDt
		else:
			extracted_data[0] = jsonDt
	return extracted_data


def refineJSONSchema(data):
	global parse_url
	recipeData = False
	isRecipeFound = False
	isGraphPresent = False
	for d in data:
		if '@graph' in d:
			isGraphPresent = True
			for value in d['@graph']:
				if isinstance(value['@type'], str) and value['@type'].strip().lower() == 'recipe':
					recipeData = value
					isRecipeFound = True
					break
		else:
			if isinstance(d['@type'], str) and d['@type'].strip().lower() == 'recipe':
				recipeData = d
				isRecipeFound = True
				break

	if isGraphPresent and isRecipeFound == False:
		for d in data:
			if isinstance(d['@type'], str) and d['@type'].strip().lower() == 'recipe':
				recipeData = d
				isRecipeFound = True
				break

	if isRecipeFound == False or len(recipeData) == 0:
		return False
	refinedData = refineAllTypesRecipeData(recipeData)

	return refinedData


def transformSchemaToResponse(data):
	transformedData = dict()
	for key in schemaDataMapping:
		if isinstance(schemaDataMapping[key], dict):
			transformedData[key] = dict()
			for k in schemaDataMapping[key].values():
				for j in k:
					transformedData[key][j] = data[key][schemaDataMapping[key][key][j]] if (
								key in data and schemaDataMapping[key][key][j] in data[key]) else None
		else:
			transformedData[key] = data[schemaDataMapping[key]]
	return transformedData


def embeddedSchema(url):
	r = requests.get(url)
	base_url = get_base_url(r.text, r.url)
	data = extruct.extract(r.text, base_url=base_url, syntaxes=['microdata'])
	return data['microdata']


def refineEmbeddedSchema(data):
	if len(data) == 0:
		return False
	recipeData = dict()
	for d in data:
		if 'type' in d and 'recipe' in d['type'].lower():
			recipeData = d['properties'] if 'properties' in d else d
	if len(recipeData) == 0:
		return False

	# if nutrition data is present and is defined in its 'properties'
	if 'nutrition' in recipeData and 'properties' in recipeData['nutrition']:
		nutrition_data = recipeData['nutrition']['properties']
		del recipeData['nutrition']
		recipeData['nutrition'] = nutrition_data

	# image property modification
	if 'image' in recipeData and 'properties' in recipeData['image']:
		image_data = recipeData['image']['properties']
		del recipeData['image']
		recipeData['image'] = image_data

	refinedData = refineAllTypesRecipeData(recipeData)
	return refinedData


def extractData(url):
	global parse_url
	parse_url = url
	# Find if page has inline schema data
	data = embeddedSchema(url)
	# Find if page has inline schema data that is recipe data
	refinedData = refineEmbeddedSchema(data)
	# If inline schema is not available, look for json-ld
	if not refinedData:
		html = getPageSource(url)
		data = extractSchemaJson(html)
		# if no json-ld schema is available, throw no schema error
		if len(data) != 0:
			refinedData = refineJSONSchema(data)
	# if neither embedded schema or json-ld schema is available, throw no schema error
	if not refinedData:
		raise NoSchemaResultSet
	# Transform raw schema set to response format
	if len(refinedData) != 0:
		finalResult = transformSchemaToResponse(refinedData)
	else:
		return False
	return finalResult
