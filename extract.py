#!/usr/bin/python
import codecs
from datetime import datetime
import math
import os
import re
import sys
import zlib
division = codecs.open('defaultdiv.html', 'w', 'utf-8')

if not os.path.exists("index"):
	os.mkdir("index")

index = codecs.open("index/assembly.html", 'w', 'utf-8')
index.write(" <meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\">\n")
index.write("<a href=\"http://vicvote.review\">Victorian Website</a>\n\t<b><center>List of Queensland Legislative Assembly Divisions</center></b>\n")


files = []

for file in os.listdir("hansard"):
	if file.endswith(".txt"):
		files.append("hansard/" + file)

files.sort()

for file in files:
	found = 0
	votes = "none"
	titlesearch = 0
	linenum = 0
	title = ""

	day = datetime.strptime(file, "hansard/%Y_%m_%d_WEEKLY.pdf.txt")
	strdate = day.strftime("%Y%m%d")
	humandate = day.strftime("%e %B %Y")
	year = day.strftime("%Y")

	index.write("</p>\n\t<p>\n\t\t<i>" + humandate + "</i><br />")

	if not os.path.exists("divisions"):
		os.mkdir("divisions")
	os.chdir("divisions")
	if not os.path.exists(strdate):
		os.mkdir(strdate)
	os.chdir(strdate)

	f = codecs.open("../../" + file, 'r', 'utf-8')
	ayesdict = {"LNP": 0, "ALP": 0, "KAP": 0, "INDEPENDENT": 0}
	noesdict = {"LNP": 0, "ALP": 0, "KAP": 0, "INDEPENDENT": 0}
	parties = ["LNP","ALP","KAP","INDEPENDENT"]
	colors = {"LNP": "blue", "ALP": "red", "KAP": "lightcoral", "INDEPENDENT": "gray"}
	speaker = "none"
	fullvotes = ""

	for line in f:
		if titlesearch == 1:
			if line[0].isalpha():
				title = title + line[:len(line)-2]
			elif line[0].isdigit():
				titlesearch = 0

		if found == 1 and line[:len(line)-2].isdigit():
			title = ""
			titlesearch = 1

		if "AYES," in line:
			adler = format(zlib.adler32(bytes(str(linenum) + title, 'utf-8')), '02x')
			index.write("\n\t\t<a href=\"../divisions/" + strdate)
			index.write("/" + adler + ".html\" >" + title)
			index.write("</a><br/>")

			division = codecs.open(adler + ".html", "w", 'utf-8')
			division.write("<meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\">\n")
			division.write("<a href=\"../../index/assembly.html\">List of QLD divisions</a>\n")
			division.write("<a href=\"http://vicvote.review\">Victorian Website</a>\n")
			division.write("<b><center>")
			division.write(title)
			division.write(" (" + humandate + ")")
			division.write("</center></b>\n")
			division.write("<a href=\"https://www.parliament.qld.gov.au/documents/hansard/")
			division.write(year)
			division.write("/" + file.split(".txt")[0].split("hansard/")[1] + "\">")
			division.write("View in Hansard")
			division.write("</a>\n")
			division.write("<a href=\"https://duckduckgo.com/?q=")
			division.write(title)
			division.write("\">Search on DuckDuckGo</a>\n")
			division.write("<img src=\"")
			division.write(adler + ".svg")
			division.write("\" width=\"40%\" height=\"70%\" style=\"float: right; width: 49%;\" alt=\"Coloured circles representing parties with \'Ayes\' on the left and \'Noes\' on the right\"/>")
			svg = open(adler + ".svg", "w")
			votes = "ayes"
		elif "NOES," in line:
			votes = "noes"
		elif "Resolved" in line and votes == "noes":
			ayestotal = 0
			noestotal = 0
			for party in parties:
				ayestotal = ayestotal + ayesdict[party]
				noestotal = noestotal + noesdict[party]
			height = 515 - (math.ceil(max(ayestotal, noestotal) / 5)*25)
			svg.write("<svg viewBox=\"0 ")
			svg.write(str(height))
			svg.write(" 300 " + str(575-height) + "\" style=\"background: white\" xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\">")
			y = 550
			x = 125
			for party in parties:
				count = 1
				while count <= ayesdict[party]:
					svg.write("\n\t<circle cx=\"")
					svg.write(str(x))
					svg.write("\" cy=\"")
					svg.write(str(y))
					svg.write("\" r=\"10\" fill=\"")
					svg.write(colors[party])
					svg.write("\" />")
					if x <= 25:
						x = 125
						y = y - 25
					else:
						x = x - 25
					count = count + 1

			oldy = y
			y = 550
			x = 175
			for party in parties:
				count = 1
				while count <= noesdict[party]:
					svg.write("\n\t<circle cx=\"")
					svg.write(str(x))
					svg.write("\" cy=\"")
					svg.write(str(y))
					svg.write("\" r=\"10\" fill=\"")
					svg.write(colors[party])
					svg.write("\" />")
					if x >= 275:
						x = 175
						y = y - 25
					else:
						x = x + 25
					count = count + 1

			if speaker != "none":
				if speaker == "aye":
					x = 125
				else:
					x = 175
				svg.write("\n\t<circle cx=\"")
				svg.write(str(x))
				svg.write("\" cy=\"")
				svg.write(str(min(oldy, y) - 35))
				svg.write("\" r=\"10\" fill=\"gray\" />")

			svg.write("</svg>")

			division.write("<div style=\"clear: both;\">")
			division.write(fullvotes)
			division.write("</div>\n")

			ayesdict = {"LNP": 0, "ALP": 0, "KAP": 0, "INDEPENDENT": 0}
			noesdict = {"LNP": 0, "ALP": 0, "KAP": 0, "INDEPENDENT": 0}
			speaker = "none"
			votes = "none"
			fullvotes = ""


		if votes != "none" and line[0].isalpha():
			if line[1].isupper() or "Pair" in line or "Speaker" in line or "SPEAKER" in line:
				division.write("<p>\n")

			if "Speaker" in line or "SPEAKER" in line:
				if "ayes" in line:
					division.write("The Speaker broke the tie by voting Aye")
					speaker = "aye"
				elif "noes" in line:
					division.write("The Speaker broke the tie by voting No")
					speaker = "no"

			numlist = re.findall(r'\b\d+\b', line)
			if len(numlist) > 0:
				votecount = int(numlist[0])
			else:
				votecount = 0
			
			for party in parties:
				if party in line:
					if votes == "ayes":
						ayesdict[party] = votecount
					elif votes == "noes":
						noesdict[party] = votecount

			if "AYES" in line or "NOES" in line:
				division.write("<u>")
				#There was only one conscience vote, so I'm
				#entering it in manually
				if ":" not in line and (adler == "3d151845" or adler == "3c0e1841"):
					ayesdict = {"LNP": 20, "ALP": 43, "KAP": 0, "INDEPENDENT": 1}
					noesdict = {"LNP": 20, "ALP": 0, "KAP": 2, "INDEPENDENT": 0}
			pos = 0
			if len(line) >= 2 and not("Speaker" in line or "SPEAKER" in line or "Pair" in line):
				while line[1].isupper() and pos < len(line) - 1 and (line[pos].isupper() or line[pos].isdigit() or line[pos] == ' ' or line[pos] == "," or line[pos] == ":"):
					division.write(line[pos])
					pos = pos + 1
				if line.split(",")[0].isupper():
					fullvotes = fullvotes + "<p>\n"
				fullvotes = fullvotes + line

			if "Pair" in line:
				division.write(line)

			if "AYES" in line or "NOES" in line:
				division.write("</u>")


		found = 0

		if "\f" in line:
			found = 1

		linenum = linenum + 1

	os.chdir("../..")

