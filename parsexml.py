import json
from math import log2
import sys
import xml.etree.ElementTree
from collections import defaultdict
import numpy
import re
import pickle
import glob
from itertools import chain

xmlFiles = list(chain(*[ glob.glob(globName)  for globName in sys.argv[1:] ]))
print("Files as input:", xmlFiles)

docs = dict()

##############################
print("Parsing XML...")
##############################
for xmlFile in xmlFiles:
	pages = xml.etree.ElementTree.parse(xmlFile).getroot()

	for page in pages.findall("{http://www.mediawiki.org/xml/export-0.10/}page"):
		titles = page.findall("{http://www.mediawiki.org/xml/export-0.10/}title")
		revisions = page.findall("{http://www.mediawiki.org/xml/export-0.10/}revision")
	
		if titles and revisions:
			revision = revisions[0] # last revision
			contents = revision.findall("{http://www.mediawiki.org/xml/export-0.10/}text")
			if contents:
				docs[titles[0].text] = contents[0].text 



# Some regEx for parsing
cleanExtLinks = r"\[https?://[^\]]*\]"
linkRe = r"\[\[([^\]]*)\]\]"
removeLinkRe = r"\[\[[^\]]+\|([^\|\]]+)\]\]"
removeLink2Re =  r"\[\[([^\|\]]+)\]\]"
wordRe = r"[a-zA-Z\-]+"
stopWords = ["-"]




print("Extracting links, transforming links in text, tokenizing, and filling a tok-doc matrix...")
links = dict()
doctok = dict()
doclen = dict()
tokdoc = dict()
for idx,doc in enumerate(docs):
	if idx%(len(docs)//20) == 0:
		print("Progress " + str(int(idx*100/len(docs)))  +"%")
	links[doc] = list()	
	for link in re.finditer(linkRe,docs[doc]):
		target = link.group(1).split('|')[0]
		if target in docs.keys():
			#print(doc + " --> " + target)
			links[doc] += [target]
			
	cleanDoc = re.sub(cleanExtLinks,"",docs[doc])

	# transform links to text
	docs[doc] = re.sub(removeLinkRe,r"\1",cleanDoc)
	docs[doc] = re.sub(removeLink2Re,r"\1",docs[doc])
	
	doclen[doc] = 0

	# fill the doctok matrix
	doctok[doc] = list()
	for wordre in re.finditer(wordRe,cleanDoc):
		word = wordre.group(0).lower()
		if word not in stopWords:
			doctok[doc] += [word]
			# tokdoc
			if word not in tokdoc:
				tokdoc[word] = dict()
			if doc not in tokdoc[word]:
				tokdoc[word][doc] = 0
			tokdoc[word][doc] += 1
			doclen[doc] += 1



print("done.")

print("Building tf-idf table...")
docList = doctok.keys()
Ndocs = len(docList)
tokList = tokdoc.keys()

tokInfo = defaultdict(float) # tokInfo[tok] contains the information in bits of the token
tf = dict() # tf[doc][tok] contains the frequency of the token tok in document doc
for id_doc,doc in enumerate(docs):
	if id_doc%(len(docs)//20) == 0:
		print("Progress " + str(int(id_doc*100/len(docs)))  +"%")
	tf[doc] = dict()
	for id_tok,tok in enumerate(doctok[doc]):
		tf[doc][tok] = tokdoc[tok][doc] / doclen[doc] if doc in tokdoc[tok] else 0
		tokInfo[tok] = - log2(len(tokdoc[tok]) / len(docs))
print("done.")

print("creating tf-idf...",end="")
tfidf = defaultdict(dict) # this should be in reverse sparse format
for id_tok,tok in enumerate(tokList):
	if id_tok%(len(tokList)//20) == 0:
		print("Progress " + str(int(id_tok*100/len(tokList)))  +"%")
	for doc in tokdoc[tok]:
		tfidf[tok][doc] = tokInfo[tok] * tf[doc][tok]
print("done.")

print("Saving the links and the tfidf as pickle objects...")
with open("links.dict",'wb') as fileout:
	pickle.dump(links, fileout, protocol=pickle.HIGHEST_PROTOCOL)

with open("tfidf.dict",'wb') as fileout:
	pickle.dump(tfidf, fileout, protocol=pickle.HIGHEST_PROTOCOL)

with open("tokInfo.dict",'wb') as fileout:
	pickle.dump(tokInfo, fileout, protocol=pickle.HIGHEST_PROTOCOL)

with open("links.dict.json",'w') as fileout:
	json.dump(links, fileout, indent=2)

with open("tfidf.dict.json",'w') as fileout:
	json.dump(tfidf, fileout, indent=2)

with open("tokInfo.dict.json",'w') as fileout:
	json.dump(tokInfo, fileout, indent=2)
