#!/usr/bin/env python
# MLSA Multilingual Software Analysis
# This program is part of the MLSA package under development at Fordham University Department of Computer and Information Science.
# <This program converts the csv file generated by the ControlFlow program into a python list>
# Author: <Sunand Raghupathi>
# Date: <6/20/17>
# This code can be copied or used and is without warrenty or support, but this header needs to be coppied along with the program FU2017
# Input: <the csv file written by the ControlFlow program>
# Output: A python list of the form: <(lineNumber, [controlFlow])>


import csv
import sys


def main(inputfile):
	error = "MLSA: getControlFlow "
	
	cf = []

	try:
		with open(inputfile, 'r') as f:
			csv_f = csv.reader(f)

			for line in csv_f:
				subList = []
				subCouple = ()
				if len(line) > 1:
					for j in line[1:]:
						subList.append(j)

				else:
					subList.append('')


				subCouple = (line[0], subList)
		
				cf.append(subCouple)

	except Exception:
		sys.exit(error + "file " + '"' + inputfile + '"' + " not found")


	if len(cf) == 0:
		sys.exit(error + "control flow is empty")
	return cf 

#print getControlFlow('if.c_rcfg.csv')

