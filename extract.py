#!/usr/bin/env python3

# from gsheets import Sheets
# url = 'https://docs.google.com/spreadsheets/d/1dR13B3Wi_KJGUJQ0BZa2frLAVxhZnbz0hpwCcWSvb20'
# s = sheets.get(url)

import collections
import functools
import operator
import pandas as pd
import os, subprocess
from math import isnan
from re import findall
from json import loads


def get_last_code(n):
	snipped = 0
	snipped_len = 25

	for i in range(1, snipped_len):
		try:
			nan = isnan(df[f'Code Snippet {i}'][n])

			if nan:
				snipped = i - 1
				break
		except:
			pass

	if snipped:
		return df[f'Code Snippet {snipped}'][n]
	else:
		return False

def run_pycefr(dirname):
	# python3 ~/pycefr/pycerfl.py directory output

	pycefr_path = "/home/attacker/pycefr/pycerfl.py"
	process = subprocess.check_output(["python3", pycefr_path, "directory", dirname])
	level = findall("Elements of level (.*?)\n", process.decode())
	data = {}

	for lv in level:
		l = lv.split(":")
		data.update({l[0]:int(l[1])})

	return data

def run_ncdsearch(dirname):
	# java -jar ~/NCDSearch/target/ncdsearch.jar /mnt/c/Users/Attacker/Documents/NAIST/outputbak -lang py -full -e identifier

	ncdsearch_path = "/home/attacker/NCDSearch/target/ncdsearch.jar"
	# process = subprocess.check_output(["java", "-jar", ncdsearch_path, dirname, "-json", "-lang", "py", "-full", "-e", "identifier"])
	pass

def get_sum_result(data):
	return dict(functools.reduce(operator.add, map(collections.Counter, data)))

def main():
	gsearch = []
	chatgpt = []
	sovrflw = []

	print(f"[INFO] Writing extracted file from excel")
	print(f"[INFO] Running tools to analyze file")
	# print(f"[INFO] {fname}")

	for i in range(len(df)):
		solved = df['Solved? Please tick the box if it is solved'][i]
		se = df['Assistant Name'][i].replace(" ", "")
		user = df['Participant'][i]
		eid = df['Exercise ID'][i].split(":")[-1].strip()
		last_code = get_last_code(i)

		if last_code:
			fname = f"{out}/{se}_{user}_{eid}.py"

			with open(fname, "w") as w:
				w.write(last_code)
				w.close()

			fname_bak = f"{out_ncd}/{se}_{user}_{eid}.py"

			with open(fname_bak, "w") as w:
				w.write(last_code)
				w.close()

			pycefr_check = run_pycefr(out)
			os.remove(fname)

			if se == "GoogleSearch":
				gsearch.append(pycefr_check)
			elif se == "StackOverflow":
				sovrflw.append(pycefr_check)
			elif se == "ChatGPT":
				chatgpt.append(pycefr_check)
			else:
				print("[INFO] Unkown Assistant Name")
			

	google_search = get_sum_result(gsearch)
	openai_chtgpt = get_sum_result(chatgpt)
	stack_ovrflow = get_sum_result(sovrflw)

	final_results = {
		"GoogleSearch": google_search,
		"ChatGPT": openai_chtgpt,
		"StackOverflow": stack_ovrflow
	}

	print(f"[INFO] RESULTS: {final_results}")


if __name__ == '__main__':
	try:
		fn = "Dataset.xlsx"
		df = pd.read_excel(fn)
		out = "output"
		out_ncd = "outforncd"

		if not os.path.isdir(out):
			os.mkdir(out)

		if not os.path.isdir(out_ncd):
			os.mkdir(out_ncd)

		main()
	except Exception as e:
		exit(f"[ERROR] {e}")


