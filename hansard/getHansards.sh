#!/bin/sh
#wget -w 3 -i hansard
for pdf in `ls | grep pdf`
do
	echo "Extracting "$pdf
	pdf2txt.py -o $pdf".txt" $pdf
done
