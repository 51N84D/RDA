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


#----------------------------------------------------------#

 
def main(astfile):
	

	with open(astfile, 'r') as f:
		programList = json.load(f)

	root = id(programList['body'][0])
	getNodeList(programList, root, None)
	return nodeList, treeList


#main()







