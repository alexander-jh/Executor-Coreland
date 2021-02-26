#!/bin/bash

runner=$1

if test -f Main.py
then
	runner="python3 Main.py"
elif test -f Main.java
then
	echo "Attempting to compile..."
	javac *.java
	runner="java Main"
fi

score=0
error=0

for value in {1..26}
do
	echo ""
	echo "Running ${value}.code"
	timeout 5 ${runner} Correct/${value}.code Correct/${value}.data > Correct/${value}.student
	echo "Running diff with ${value}.expected"
	if cmp -s "Correct/${value}.expected" "Correct/${value}.student"; then
		echo "Print looks good"
		score=$(($score + 1))
	else
		echo "Student output and expected output are different"
	fi
done

echo "Running error cases:"
echo ""
echo "Running 01.error:"
timeout 5 ${runner} Error/01.code Error/01.data
read -n 1 -p "Error is .data file not having enough values. Error message related to that? (y/n)" mainmenuinput
if [ $mainmenuinput = "y" ]; then
	error=$(($error + 1))
fi
echo ""
echo "Running 02.error:"
timeout 5 ${runner} Error/02.code Error/02.data
read -n 1 -p "Error is uninitialized variable. Error message related to that? (y/n)" mainmenuinput
if [ $mainmenuinput = "y" ]; then
	error=$(($error + 1))
fi

echo "Correct cases score out of 26:"
echo $score
echo "Error cases score out of 2:"
echo $error

echo "Done!"