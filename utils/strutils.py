import re

def striphtml(raw_html):
	cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def striptabs(string):
	#return re.search(r'\d+', string).group(0)
	return re.compile(r'[\n\r\t]').sub("", string)

