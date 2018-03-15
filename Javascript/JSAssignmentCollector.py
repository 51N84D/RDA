import json
import csv
import sys
from collections import OrderedDict

def prettyPrint(body):
	for i in body:
		print i


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

 
def main(inputFile, varsFile, nodeList):

	assignmentList = AssignmentCollector(nodeList)

	writeCSV(assignmentList, varsFile)
	
#main()







