#!/usr/bin/env python
import generateJSTree
import JSControlFlow
import JSAssignmentCollector
import jsRDA

def main(inputFile, fileName, outputFile):
	#FileName conventions:
	fcfgFile = fileName + '_fcfg.csv'
	rcfgFile = fileName + '_rcfg.csv'
	varsFile = fileName + '_vars.csv'

	nodeList, treeList = generateJSTree.main(inputFile)
	print '-----------'
	for i in nodeList:
		print i.typeString, i.lineNum, i.uniqueID
	#Generate controlFlow files (fcfg and rcfg)
	JSControlFlow.main(inputFile, fileName, fcfgFile, rcfgFile, treeList)
	JSAssignmentCollector.main(inputFile, varsFile, nodeList)
	jsRDA.main(rcfgFile, varsFile, outputFile)
	

main('funcCall.js_ast.json', 'funcCall.js', 'funcCall.js_rda.csv')
