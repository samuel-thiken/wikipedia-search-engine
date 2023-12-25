from itertools import chain
from collections import defaultdict
import numpy
import pickle
import sys
import copy

with open("tfidf.dict",'rb') as f:
	tfidf = pickle.load(f)
	
with open("tokInfo.dict",'rb') as f:
	tokInfo = pickle.load(f)

with open("pageRank.dict",'rb') as f:
	pageRankDict = pickle.load(f)




print("Normalizing tf idf...",end="")
tfidfNorm = copy.deepcopy(tfidf)
 #TO COMPLETE
 #TO COMPLETE
 #TO COMPLETE
 #TO COMPLETE
		
 #TO COMPLETE
 #TO COMPLETE
 #TO COMPLETE
print("done.")



# Returns the topN documents by token relevance (vector model)
def getBestResults(queryStr, topN, tfidfMatrix):
	query = queryStr.split(" ")
	res = defaultdict(float)
	for tok in query:
		docs = tfidfMatrix[tok]
		for doc in docs:
			if doc.startswith("Category:"):
				continue
			if doc not in res:
				res[doc] = 0
			res[doc] += tfidfMatrix[tok][doc]
	top = sorted(res.keys(), key=lambda k: res[k], reverse=True)[:topN]
	return top


# Sorts a list of results according to their pageRank
def rankResults(results):
	return sorted(results, key=lambda doc: pageRankDict[doc], reverse=True)


def printResults(rankedResults):
	for idx,page in enumerate(rankedResults):
		print(str(idx+1) + ". " + page)



def search(query, top=15):
	print("Results for ",query,"\n===========")
	results = getBestResults(query,top,tfidf)
	printResults(results)

	print("\n\nResults after normalization for ",query,"\n===========")
	results = getBestResults(query,top,tfidfNorm)
	printResults(results)


	print("\n\nResults after ranking for ",query,"\n===========")
	results = rankResults(results)
	printResults(results)

	#bestPageSimilarity = list(reversed([ searchRes[i] for i in numpy.argsort(searchRes)[-10:] ]))
	#bestPageSimilarity


query = "darwin" # or sys.argv[1]
top = 15			 # number of results to show

search(query, top)
