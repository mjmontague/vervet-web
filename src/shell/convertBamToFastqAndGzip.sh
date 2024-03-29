#!/bin/bash

if test $# -lt 2
then
	echo "Usage: $0 INPUTFNAME OUTPUTFnamePREFIX"
	echo
	echo "	Given a sam or bam (*.?am) file which contains paired-end reads,"
	echo "	  1. call picard to convert them to two fastq files. If one end file is empty, it'll be deleted."
	echo "	  2. gzip the fastq files"
	echo "Note:
		All existent files will be overriden."
	echo
	echo "Examples:	~/script//shell/convertBamToFastqAndGzip.sh ./fastq/gerald_81GPJABXX_5_TTAGGC.bam db/individual_sequence/1_3"
exit
fi

inputFname=$1
outputFnamePrefix=$2

parameter=''
#while test -n "$6"
#do
#parameter=$parameter' '$6
#shift
#done
picard_tool_path=$HOME/script/picard/dist/

#2013.04.03 bugfix. create these variables to avoid  putting "\" in the "" for the commandline variable. 
outputFname1=$outputFnamePrefix\_1.fastq
outputFname2=$outputFnamePrefix\_2.fastq
#2011-8-28 delete prior files regardless of whether they exist or not ("-w" is test for exist and writable file.)
if test -w $outputFname1
then
	echo "$outputFname1 already exists. Delete it now.\n"
	rm -f $outputFname1
fi
if test -w $outputFname2
then
	echo "$outputFname2 already exists. Delete it now.\n"
	rm -f $outputFname2
fi

commandline="java -jar $picard_tool_path/SamToFastq.jar INPUT=$inputFname F=$outputFname1 F2=$outputFname2"
date
echo commandline is $commandline
$commandline

#2013.04.03 immediately test if exit code from previous command is non-zero.
#commandExitCode=$?
#if test "$commandExitCode" != "0"
#then
#	echo "Non-zero exit after running picard's SamToFastq.jar."
#	exit $commandExitCode
#fi
#date
#
#2011-8-28 delete prior files regardless of whether they exist or not
#if test -w $outputFname1.gz
#then
#	echo "$outputFname1.gz already exists. Delete it now.\n"
#	rm -f $outputFname1.gz
#fi
#
#if test -w $outputFname2.gz
#then
#	echo "$outputFname2.gz already exists. Delete it now.\n"
#	rm -f $outputFname2.gz
#fi
#
#if test -s $outputFname1
#then
#	echo -n "gzipping $outputFname1 ..."
#	gzip $outputFname1
#	#2013.04.03 immediately test if exit code from previous command is non-zero.
#	commandExitCode=$?
#	if test "$commandExitCode" != "0"
#	then
#		echo "Non-zero exit after running picard's SamToFastq.jar."
#		exit $commandExitCode
#	fi
#	
#	echo " ."
#else	#delete it if it's an empty file
#	rm -f $outputFname1
#fi
#
#if test -s $outputFname2
#then
#	echo -n "gzipping $outputFname2 ..."
#	gzip $outputFname2
#	#2013.04.03 immediately test if exit code from previous command is non-zero.
#	commandExitCode=$?
#	if test "$commandExitCode" != "0"
#	then
#		echo "Non-zero exit after running picard's SamToFastq.jar."
#		exit $commandExitCode
#	fi
#	
#	echo " ."
#else	#delete it if it's an empty file
#	rm -f $outputFname2
#fi


#for i in `ls $inputDir/*.?am`; do echo $i;
#	fname_prefix=`echo $i|awk -F . '{print $1}'`
#	if test -z $fname_prefix	# . is the first letter in the directory name
#	then
#		fname_prefix=.`echo $i|awk -F . '{print $2}'`
#	fi
#	input_fname=$i
#	output_prefix=$fname_prefix
#	java -jar ~/script/vervet/bin/picard-tools/SamToFastq.jar INPUT=$input_fname F=$output_prefix\_1.fastq F2=$output_prefix\_2.fastq
#done
#
#for i in `ls $inputDir/*.fastq`; do echo $i;
#	input_fname=$i
#	gzip $input_fname
#done
