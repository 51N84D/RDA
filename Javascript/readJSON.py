import json
import csv
import sys
from collections import OrderedDict

#Definition for AST node class
class ASTEntry(object):
	def __init__(self):
		self.typeString = ""	
		self.uniqueID = -1		
		self.lineNum = -1		
		self.treeLevel = -1		
		self.children = []		
		self.parent = None 		
		self.index = -1	
		self.jsonObj = None
		self.conditional = False
		self.conditionalType = ''
		self.lastChild = False

		#For ifs
		self.isElseStmt = False
		self.hasElseStmt = False
		self.firstElse = False
		self.lastElse = False


def prettyPrint(body):
	for i in body:
		print i



nodeList = []
treeList = []
def getNodeList(textList, root, parent):
	if 'body' in textList:
		trueTextList = textList['body']
	else:
		trueTextList = textList

	if not isinstance(trueTextList, list):
		trueTextList = [trueTextList]

	for i in trueTextList: # i = item
		#Create astEntry and fill in information
		astItem = ASTEntry()
		astItem.jsonObj = i
		astItem.typeString = i['type']
		astItem.lineNum = i['loc']['start']['line']
		astItem.uniqueID = id(i) - root
		


		if parent == None:
			treeList.append(astItem)
		else:
			parent.children.append(astItem)
			astItem.parent = parent

			if parent.typeString == 'IfStatement' and parent.hasElseStmt == True:
				#Search to see if astItem is an else statement
				if 'body' in parent.jsonObj['alternate']:
					for line in parent.jsonObj['alternate']['body']:
						if astItem.jsonObj == line:
							astItem.isElseStmt = True
				else:
					if astItem.jsonObj == parent.jsonObj['alternate']:
						astItem.isElseStmt = True
						astItem.firstElse = True
						astItem.lastElse = True
						
				#Check to see if first
				if astItem.isElseStmt and ('body' in parent.jsonObj['alternate']) and (astItem.jsonObj == parent.jsonObj['alternate']['body'][0]):
					astItem.firstElse = True
				if astItem.isElseStmt and ('body' in parent.jsonObj['alternate']) and (astItem.jsonObj == parent.jsonObj['alternate']['body'][-1]):
					astItem.lastElse = True



		nodeList.append(astItem)

		if astItem.typeString == 'FunctionDeclaration':
			getNodeList(i['body'], root, astItem)

		if astItem.typeString == 'BlockStatement':
			getNodeList(i['body'], root, astItem)


		if astItem.typeString == 'IfStatement':
			#Put first arg in list so that iteration works in beginning
			getNodeList([astItem.jsonObj['test']], root, astItem)
			getNodeList(astItem.jsonObj['consequent'], root, astItem)
			#Check for else:
			if astItem.jsonObj['alternate'] != None:
				astItem.hasElseStmt = True
				getNodeList(astItem.jsonObj['alternate'], root, astItem)

		if astItem.typeString == 'WhileStatement':
			getNodeList([astItem.jsonObj['test']], root, astItem)
			getNodeList(astItem.jsonObj['body'], root, astItem)





def AssignmentCollector(nodeList):
	assignmentList = []

	for item in nodeList:
		subList = []
		#For scope information
		if item.typeString == 'FunctionDeclaration':
			start = item.jsonObj['loc']['start']['line']
			end = item.jsonObj['loc']['end']['line']
			funcId = item.uniqueID
			funcScope = (start, end, funcId)
			



		if item.typeString == 'VariableDeclaration':
			#Check if it is an assignment
			if item.jsonObj['declarations'][0]['init'] != None:
				#Get name
				name = str(item.jsonObj['declarations'][0]['id']['name'])
				#Get value
				value = item.jsonObj['declarations'][0]['init']['value']
				#Get line number
				lineNum = item.jsonObj['loc']['start']['line']
				#Get scope (later, first check if the variable is global)
				scope = (lineNum, -1)
				if (lineNum >= funcScope[0] and lineNum <= funcScope[1]):
					scope = funcScope
				subList = [item.uniqueID, name, scope, value]
				assignmentList.append(subList)

		if item.typeString == 'ExpressionStatement':
			expressionType = item.jsonObj['expression']['type']
			#Check if expression is an assignment
			if expressionType == 'AssignmentExpression':
				#Get name:
				name = str(item.jsonObj['expression']['left']['name'])
				#Check if value is variable:
				if item.jsonObj['expression']['right']['type'] == 'Literal':
					value = item.jsonObj['expression']['right']['value']
					if type(value) == unicode:
						value = str(value)
				#Later, check if it's a variable or an expression
				else:
					value = '??'
				#Get line numbers
				lineNum = item.jsonObj['loc']['start']['line']
				scope = (lineNum, -1)
				if (lineNum >= funcScope[0] and lineNum <= funcScope[1]):
					scope = funcScope
				subList = [item.uniqueID, name, scope, value]
				assignmentList.append(subList)

		if item.typeString == 'AssignmentExpression':
				#Get name:
				name = str(item.jsonObj['left']['name'])
				
				#Check if value is variable:
				if item.jsonObj['right']['type'] == 'Literal':
					value = item.jsonObj['right']['value']
					if type(value) == unicode:
						value = str(value)
				#Later, check if it's a variable or an expression
				else:
					value = '??'
				#Get line numbers
				lineNum = item.jsonObj['loc']['start']['line']
				scope = (lineNum, -1)
				if (lineNum >= funcScope[0] and lineNum <= funcScope[1]):
					scope = funcScope
				subList = [item.uniqueID, name, scope, value]
				assignmentList.append(subList)
				





	return assignmentList

def writeCSV(assignmentList, fileName):
	error = "MLSA: JSAssignmentCollector "

	try:	
		with open(fileName, 'w') as ofile:
			writer = csv.writer(ofile)	
			writer.writerows(assignmentList)
	except Exception:
		sys.exit(error + "file " + "could not be written")

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
	tempList = [currNode.lineNum]
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
				tempList.append(nextNode.lineNum)

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

#----------------------------------------------------------#

 
def main():
	jsFile = 'lineAfterIWI.js'
	astfile = jsFile + '_ast.json'
	varsFile = jsFile + '_vars.csv'



	with open(astfile, 'r') as f:
		programList = json.load(f)

	root = id(programList['body'][0])
	getNodeList(programList, root, None)

	printTree(treeList)
	print ''

	assignmentList = AssignmentCollector(nodeList)

	print assignmentList
	print ''
	
	for i in treeList:
		getForwardFlow(i)

	reverseFlow = getReverseFlow(forwardFlow)
	prettyPrint(forwardFlow)
	writeCSV(assignmentList, varsFile)
	
main()







