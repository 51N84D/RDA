import json
import csv
import sys
from collections import OrderedDict

def prettyPrint(body):
	for i in body:
		print i


#---------------------------- Control Flow --------------------------#

def printTree(treeList):
	for node in treeList:
		print node.typeString, node.uniqueID, node.lineNum
		if len(node.children) > 0:
			printTree(node.children)




def getElseStmt(currNode):
	for child in currNode.children:
		if child.isElseStmt == True:
			return child
def getLastElse(currNode):
	for child in currNode.children:
		if child.lastElse:
			return child

def setConditional(currNode, conditionalType):
	for child in currNode.children:
		if child.typeString.find('NULL') == -1:
			child.conditional = True
			child.conditionalType = conditionalType
			return child

def setLastChild(currNode):
	for child in currNode.children[::-1]:
		if (child.typeString.find('NULL') == -1 and child.isElseStmt == False):
			child.lastChild = True
			return child

def getConditionalParent(currNode):

	if currNode == None:
		return None

	elif currNode.conditional == True:
		#print 'Conditional: ', currNode.typeString
		return currNode

	else:
		if currNode.parent != None:
			for child in currNode.parent.children:
				if child.conditional == True:
					return child
			return getConditionalParent(currNode.parent)


def getNextSibling(currNode):
	parent = currNode.parent
	currNodeCheck = False
	nextSibling = None
	if (parent != None):
		for child in parent.children:
			if currNodeCheck:
				nextSibling = child
				break
			if child == currNode:
				currNodeCheck = True
	return nextSibling

def getNextNonElseSibling(currNode):
	parent = currNode.parent
	currNodeCheck = False
	nextSibling = None
	if (parent != None):
		for child in parent.children:
			if currNodeCheck and child.isElseStmt == False:
				nextSibling = child
				break
			if child == currNode:
				currNodeCheck = True
	return nextSibling

forwardFlow = []
visitedList = []
def getForwardFlow(rootNode):
	currNode = rootNode
	tempList = [currNode.uniqueID]
	nextList = []

	if currNode not in visitedList:

		visitedList.append(currNode)

		if currNode.typeString == 'FunctionDeclaration' and len(currNode.children) > 0:
			nextList.append(currNode.children[0])
			#nextNode = currNode.children[0]

		
		#------------------While Statement----------------------------------------#
		elif currNode.typeString == 'BlockStatement' and len(currNode.children) > 0:
			nextList.append(currNode.children[0])
			setLastChild(currNode)

		elif currNode.lastChild and currNode.parent.typeString == 'BlockStatement':
			nextList.append(getNextSibling(currNode.parent))

		

		#------------------While Statement----------------------------------------#
		elif currNode.typeString == 'WhileStatement':
			nextList.append(setConditional(currNode, 'WhileStatement'))
			setLastChild(currNode)

				
		elif currNode.conditional == True and currNode.parent.typeString == 'WhileStatement':
			nextList.append(getNextSibling(currNode))
			
			
			if currNode.parent.lastChild == True:
				conditionalParent = getConditionalParent(currNode.parent)
				if conditionalParent != None:
					if (conditionalParent.conditionalType == 'WhileStatement'):
						nextList.append(conditionalParent)
					else:
						nextList.append(getNextSibling(currNode.parent))
				else:
					nextList.append(getNextSibling(currNode.parent))

			else:
				nextList.append(getNextSibling(currNode.parent))

		elif currNode.lastChild == True and currNode.parent.typeString == 'WhileStatement':
			#Go back to the conditional
			nextList.append(getConditionalParent(currNode))

		#----------------------------------------------------------#


		#------------------If Statement----------------------------------------#

		#******************EXPERIMENT
		
		elif currNode.typeString == 'IfStatement':
			nextList.append(setConditional(currNode, 'IfStatement'))
			#Sets the last non-else statement
			setLastChild(currNode)
		
		#For conditionals
		elif (currNode.conditional == True and currNode.parent.typeString == 'IfStatement'):
			nextList.append(getNextSibling(currNode))
			if currNode.parent.hasElseStmt == False:
				nextList.append(getNextSibling(currNode.parent))
			else:
				nextList.append(getElseStmt(currNode.parent))


		#For last child in if
		elif (currNode.lastChild == True and currNode.parent.typeString == 'IfStatement'):
			nextList.append(getNextNonElseSibling(currNode.parent))
			#print 'broh'
			#print currNode.parent.jsonObj
			#print getNextSibling(currNode.parent).jsonObj

		elif (currNode.isElseStmt and currNode.lastElse):
			nextList.append(getNextNonElseSibling(currNode.parent))
		
		#***************************


		#----------------------------------------------------------------------



		else:
			nextList.append(getNextSibling(currNode))
			#nextNode = getNextSibling(currNode)

		#Go through next list and update temp
		for nextNode in nextList:
			if nextNode == None:
				tempList.append(None)
			else:
				tempList.append(nextNode.uniqueID)

		forwardFlow.append(tempList)
	

		for nextNode in nextList:
			if nextNode != None:
				getForwardFlow(nextNode)

def getReverseFlow(forwardFlow):
	reverseDict = OrderedDict()
	for subList in forwardFlow:
		#Pick out the first node of the sublist and check if it's in the dict
		prevNode = subList[0]
		if prevNode not in reverseDict:
			reverseDict[prevNode] = []
		if len(subList) > 1:
			for element in subList[1:]:
				if element == None:
					continue
				elif element not in reverseDict:
					reverseDict[element] = [prevNode]
				else:
					reverseDict[element].append(prevNode)
	
	#Convert to list:
	reverseFlow = []
	for key in reverseDict:
		subList = []
		subList.append(key)
		for item in reverseDict[key]:
			subList.append(item)

		#print subList
		reverseFlow.append(subList)
	#print reverseFlow
	return (reverseFlow)

def writeCSV(fcfgFile, rcfgFile,forwardFlow, reverseFlow):
	error = "MLSA: CControlFlow "
	try:	
		with open(fcfgFile, 'w') as wfile:
			writer = csv.writer(wfile)	
			writer.writerows(forwardFlow)
	except Exception:
		sys.exit(error + "file could not be written")

	try:	
		with open(rcfgFile, 'w') as ofile:
			writer = csv.writer(ofile)	
			writer.writerows(reverseFlow)
	except Exception:
		sys.exit(error + "file could not be written")	

#----------------------------------------------------------#

 
def main(inputFile, fileName, fcfgFile, rcfgFile, treeList):


	for i in treeList:
		getForwardFlow(i)

	reverseFlow = getReverseFlow(forwardFlow)

	writeCSV(fcfgFile, rcfgFile, forwardFlow, reverseFlow)









