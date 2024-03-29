#!/usr/bin/env python
"""
Examples:
	# run the program on crocea and output a local condor workflow
	%s -i ~/NetworkData/vervet/VRC/ -t /u/home/eeskintmp/polyacti/NetworkData/vervet/db/ 
		--bamFname2MonkeyIDMapFname ~/script/vervet/data/VRC_sequencing_20110802.tsv
		-u yh --commit -z dl324b-1.cmb.usc.edu -o /tmp/condorpool.xml

	#2011-8-26	generate a list of all bam file physical paths through find. (doing this because they are not located on crocea)
	find /u/home/eeskintmp/polyacti/NetworkData/vervet/raw_sequence/ -name *.bam  > /u/home/eeskintmp/polyacti/NetworkData/vervet/raw_sequence/bamFileList.txt
	# run the program on the crocea and output a hoffman2 workflow. (with db commit)
	%s -i ~/mnt/hoffman2/u/home/eeskintmp/polyacti/NetworkData/vervet/raw_sequence/bamFileList.txt
		-e /u/home/eeskin/polyacti/
		-t /u/home/eeskin/polyacti/NetworkData/vervet/db/ -u yh
		--bamFname2MonkeyIDMapFname ~/mnt/hoffman2/u/home/eeskintmp/polyacti/NetworkData/vervet/raw_sequence/xfer.genome.wustl.edu/gxfer3/46019922623327/Vervet_12_4X_README.tsv
		-z dl324b-1.cmb.usc.edu -l hoffman2
		-o unpackAndAdd12_2007Monkeys2DB_hoffman2.xml
		--commit 
	
	# 2011-8-28 output a workflow to run on local condorpool, no db commit (because records are already in db)
	%s -i /Network/Data/vervet/raw_sequence/xfer.genome.wustl.edu/gxfer3/
		--bamFname2MonkeyIDMapFname ~/mnt/hoffman2/u/home/eeskintmp/polyacti/NetworkData/vervet/raw_sequence/xfer.genome.wustl.edu/gxfer3/46019922623327/Vervet_12_4X_README.tsv
		 --minNoOfReads 4000000 -u yh --commit
		-z dl324b-1.cmb.usc.edu -j condorpool -l condorpool -o dags/AddReads2DB/DownloadUnpackReads/unpackAndAdd12_2007Monkeys2DB_condor.xml
	
	# 2012.4.30 run on hcondor, to import McGill 1X data (-y2), (-e) is not necessary because it's running on hoffman2 and can recognize home folder.
	#. --needSSHDBTunnel means it needs sshTunnel for db-interacting jobs.
	%s -i ~/NetworkData/vervet/raw_sequence/McGill96_1X/ -z localhost -u yh -j hcondor -l hcondor --commit
		-o dags/AddReads2DB/unpackMcGill96_1X.xml -y2 --needSSHDBTunnel 
		-D /u/home/eeskin/polyacti/NetworkData/vervet/db/ -t /u/home/eeskin/polyacti/NetworkData/vervet/db/
		-e /u/home/eeskin/polyacti
	
	# 2012.6.2 add 18 south-african monkeys RNA read data (-y3), sequenced by Joe DeYoung's core (from Nam's folder),
	# later manually changed its tissue id to distinguish them from DNA data (below) 
	%s -i ~namtran/panasas/Data/HiSeqRaw/Ania/SIVpilot/by.Charles.Demultiplexed/ -z localhost -u yh -j hcondor -l hcondor
		--commit -o dags/AddReads2DB/unpack20SouthAfricaSIVmonkeys.xml -y3 --needSSHDBTunnel
		-D /u/home/eeskin/polyacti/NetworkData/vervet/db/
		-t /u/home/eeskin/polyacti/NetworkData/vervet/db/ -e /u/home/eeskin/polyacti 
		--bamFname2MonkeyIDMapFname ~namtran/panasas/Data/HiSeqRaw/Ania/SIVpilot/by.Charles.Demultiplexed/sampleIds.txt
		--minNoOfReads 4000000
	
	# 2012.6.3 add 24 south-african monkeys DNA read data (-y4), sequenced by Joe DeYoung's core (from Nam's folder)
	# --minNoOfReads 4000000
	%s -i ~namtran/panasas/Data/HiSeqRaw/Ania/SIVpilot/LowpassWGS/Demultiplexed/
		-z localhost -u yh -j hcondor -l hcondor --commit -o dags/AddReads2DB/unpack20SouthAfricaSIVmonkeysDNA.xml
		-y4 --needSSHDBTunnel
		-D /u/home/eeskin/polyacti/NetworkData/vervet/db/ -t /u/home/eeskin/polyacti/NetworkData/vervet/db/
		-e /u/home/eeskin/polyacti/
		--minNoOfReads 4000000
		
	# 2013.04.04 added one VRC, a few Gambia, SK/Nevis monkeys' read data (-y5), sequenced by Joe DeYoung's core (from Nam's folder),
	%s -i ~namtran/panasas/Data/Ania/PCR_FreeBeta/2013-029A/ -z localhost -u yh -j hcondor -l hcondor
		--commit -o dags/AddReads2DB/AddVRCGambiaSKNevis_UNGCReadData2DB.xml -y5 --needSSHDBTunnel
		-D /u/home/eeskin/polyacti/NetworkData/vervet/db/
		-t /u/home/eeskin/polyacti/NetworkData/vervet/db/ -e /u/home/eeskin/polyacti 
		--bamFname2MonkeyIDMapFname ~/NetworkData/vervet/raw_sequence/2013.03.042013-029ASampleSheet-2013-029A.csv
		--minNoOfReads 4000000
	
Description:
	2011-8-2
		input:
			input (if directory, recursively go and find all bam files; if file, each line is path to bam),
			tsv file (map bam filename to monkey ID),
		
		this program
			1. queries db if individual record for that monkey is already in db, or not. create a new entry in db if not
			2. queries db if individual_sequence record for that monkey is already in db. create one new entry if not.
				update individual_sequence.path if it's none
			3. if commit, the db action would be committed
			4. outputs the whole unpack workflow to an xml output file.
		
		This program has to be run on the pegasus submission host.
		option "--commit" commits the db transaction.
	
	The bamFname2MonkeyIDMapFname contains a map from monkey ID to the bam filename (only base filename is used, relative directory is not used).
	Example ("Library" and "Bam Path" are required):
		FlowCell	Lane	Index Sequence	Library	Common Name	Bam Path	MD5
		64J6AAAXX	1	TGACCA	VCAC-2007002-1-lib1	African Green Monkey	gerald_64J6AAAXX_1.bam	gerald_64J6AAAXX_1.bam.md5
	
	1. Be careful with the db connection setting as it'll be passed to the db-registration job.
		Make sure all computing nodes have access to the db.
	2. The workflow has to be run on nodes where they have direct db and db-affiliated file-storage access.
"""
import sys, os, math
__doc__ = __doc__%(sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])

sys.path.insert(0, os.path.expanduser('~/lib/python'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import copy, re, csv
from pymodule import ProcessOptions, PassingData, MatrixFile
from pymodule.utils import getColName2IndexFromHeader
from pymodule.pegasus import yh_pegasus
from Pegasus.DAX3 import *
from vervet.src import AbstractVervetWorkflow

class UnpackAndAddIndividualSequence2DB(AbstractVervetWorkflow):
	__doc__ = __doc__
	option_default_dict = copy.deepcopy(AbstractVervetWorkflow.option_default_dict)
	option_default_dict.update({
						('input', 1, ): ['', 'i', 1, 'if it is a folder, take all .bam/.sam/.fastq files recursively. If it is a file, every line should be a path to the input file.', ],\
						('bamFname2MonkeyIDMapFname', 0, ): ['', '', 1, 'a tsv version of WUSTL xls file detailing what monkey is in which bam file.', ],\
						('minNoOfReads', 1, int): [8000000, '', 1, 'minimum number of reads in each split fastq file. This is actually the maxNoOfReads.\
								 The upper limit in each split file is 2*minNoOfReads.', ],\
						("sequencer_name", 1, ): ["GA", '', 1, 'choices: 454, GA, Sanger, PopGenSimulation. column Sequencer.short_name'],\
						("sequence_type_name", 1, ): ["100BPPairedEnd", '', 1, 'table column: SequenceType.short_name ...'],\
						("sequence_format", 1, ): ["fastq", 'f', 1, 'fasta, fastq, etc.'],\
						('inputType', 1, int): [1, 'y', 1, 'input type. 1: bam files from WUSTL. \n\
	2: fastq files from McGill (paired ends are split.). \n\
	3: fastq files from Charles Bloom demultiplexed SouthAfrican RNA data(sequenced by DeYoung core),\n\
	4: fastq files of SouthAfrican DNA read data (sequenced by DeYoung core, demultiplexed by Joe), \n\
	5: 2013.04.04 fastq files from UNGC core (DeYoung core, demultiplexed by Nam) addJobsToProcessUNGCVervetData', ],\
						})
	#('jobFileDir', 0, ): ['', 'j', 1, 'folder to contain qsub scripts', ],\
	
	def __init__(self,  **keywords):
		"""
		2011-8-3
		"""
		AbstractVervetWorkflow.__init__(self, **keywords)
		self.addJobsDict = {1: self.addJobsToProcessWUSTLData,\
						2: self.addJobsToProcessMcGillData,\
						3: self.addJobsToProcessSouthAfricanRNAData,\
						4: self.addJobsToProcessSouthAfricanDNAData,\
						5: self.addJobsToProcessUNGCVervetData}
	
	def getBamBaseFname2MonkeyID_WUSTLDNAData(self, inputFname, ):
		"""
		2011-8-3
			from WUSTL
			the input looks like this:
			#	FlowCell	Lane	Index Sequence	Library	Common Name	Bam Path	MD5
			1	64J6AAAXX	1	VCAC-2007002-1-lib1	African	Green	Monkey	/gscmnt/sata755/production/csf_111215677/gerald_64J6AAAXX_1.bam	/gscmnt/sata755/production/csf_111215677/gerald_64J6AAAXX_1.bam.md5
			2	64J6AAAXX	2	VCAC-2007006-1-lib1	African	Green	Monkey	/gscmnt/sata751/production/csf_111215675/gerald_64J6AAAXX_2.bam	/gscmnt/sata751/production/csf_111215675/gerald_64J6AAAXX_2.bam.md5
		"""
		sys.stderr.write("Getting bamBaseFname2MonkeyID dictionary ...")
		bamBaseFname2MonkeyID = {}
		reader = csv.reader(open(inputFname), delimiter='\t')
		header = reader.next()
		col_name2index = getColName2IndexFromHeader(header, skipEmptyColumn=True)
		monkeyIDIndex = col_name2index.get("Library")
		if monkeyIDIndex is None:	#2012.6.7
			monkeyIDIndex = col_name2index.get("library")
		bamFnameIndex = col_name2index.get("Bam Path")
		if bamFnameIndex is None:	#2012.2.9
			bamFnameIndex = col_name2index.get("BAM Path")
		if bamFnameIndex is None:	#2012.2.9
			bamFnameIndex = col_name2index.get("BAM")
		if bamFnameIndex is None:	#2012.6.7
			bamFnameIndex = col_name2index.get("bam pathway")
		#monkeyIDPattern = re.compile(r'\w+-(\w+)-\d+-\w+')	# i.e. VCAC-2007002-1-lib1
		monkeyIDPattern = re.compile(r'\w+-(\w+)-\w+-\w+')	# 2012.5.29 i.e. VCAC-VGA00006-AGM0075-lib1 ,
		# VCAC-VZC1014-AGM0055-lib1, VCAC-1996031-VRV0265-lib2a, VCAC-VKD7-361-VKD7-361-lib1 (VKD7 is to be taken),
		for row in reader:
			monkeyID = row[monkeyIDIndex]
			pa_search = monkeyIDPattern.search(monkeyID)
			if pa_search:
				monkeyID = pa_search.group(1)
			else:
				sys.stderr.write("Warning: could not parse monkey ID from %s. Ignore.\n"%(monkeyID))
				continue
			bamFname = row[bamFnameIndex]
			bamBaseFname = os.path.split(bamFname)[1]
			bamBaseFname2MonkeyID[bamBaseFname] = monkeyID
		sys.stderr.write("%s entries.\n"%(len(bamBaseFname2MonkeyID)))
		return bamBaseFname2MonkeyID
	
	def getAllBamFiles(self, inputDir, bamFnameLs=[]):
		"""
		2011-8-3
			recursively going through the directory to get all bam files
			
		"""
		
		for inputFname in os.listdir(inputDir):
			#get the absolute path
			inputFname = os.path.join(inputDir, inputFname)
			if os.path.isfile(inputFname):
				prefix, suffix = os.path.splitext(inputFname)
				if suffix=='.bam' or suffix=='.sam':
					bamFnameLs.append(inputFname)
			elif os.path.isdir(inputFname):
				self.getAllBamFiles(inputFname, bamFnameLs)
		
	def addMonkeySequence(self, db_vervet=None, monkeyID=None, sequencer_name='GA', sequence_type_name='100BPPairedEnd', sequence_format='fastq',\
						path_to_original_sequence=None, data_dir=None):
		"""
		2012.4.30
			add argument data_dir
		2011-8-3
		"""
		individual = db_vervet.getIndividual(code=monkeyID)
		individual_sequence = db_vervet.getIndividualSequence(individual_id=individual.id, sequencer_name=sequencer_name, \
						sequence_type_name=sequence_type_name, sequence_format=sequence_format, \
						path_to_original_sequence=path_to_original_sequence, tissue_name=None, coverage=None,\
						subFolder='individual_sequence', data_dir=data_dir, sequence_batch_id=None, \
						filtered=0, version=None, is_contaminated=0, outdated_index=0)
		
		return individual_sequence
	
	def writeQsubJob(self, jobFname, bamFname, outputDir, vervet_path):
		"""
		2011-8-3
		"""
		bamBaseFname = os.path.split(bamFname)[1]
		bamBaseFnamePrefix = os.path.splitext(bamBaseFname)[0]
		outputFnamePrefix = os.path.join(outputDir, bamBaseFnamePrefix)
		commandline="%s/convertBamToFastqAndGzip.sh %s %s"%(vervet_path, bamFname, outputFnamePrefix)
		
		jobF = open(jobFname, 'w')
		jobF.write("""#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -o $JOB_NAME.joblog.$JOB_ID
#$ -j y
#$ -l time=23:00:00
#$ -r n

mkdir %s	#create the output directory
echo %s
%s"""%(outputDir, commandline, commandline))
		jobF.close()
	
	def registerCustomExecutables(self, workflow=None):
		"""
		2012.1.3
		"""
		self.addOneExecutableFromPathAndAssignProperClusterSize(path=os.path.join(self.vervetSrcPath, 'shell/convertBamToFastqAndGzip.sh'), \
										name='convertBamToFastqAndGzip', clusterSizeMultipler=0.05)
		
		self.addOneExecutableFromPathAndAssignProperClusterSize(path=os.path.join(self.vervetSrcPath, 'shell/SplitReadFileWrapper.sh'), \
										name='SplitReadFileWrapper', clusterSizeMultipler=0.05)
		self.addOneExecutableFromPathAndAssignProperClusterSize(path=os.path.join(self.vervetSrcPath, 'db/input/RegisterAndMoveSplitSequenceFiles.py'), \
										name='RegisterAndMoveSplitSequenceFiles', clusterSizeMultipler=0.05)
		self.addOneExecutableFromPathAndAssignProperClusterSize(path=self.javaPath, \
										name='SamToFastqJava', clusterSizeMultipler=0.05)
		
	def addConvertBamToFastqAndGzipJob(self, workflow=None, executable=None, \
							inputF=None, outputFnamePrefix=None, \
							parentJobLs=None, job_max_memory=2000, walltime = 800, extraDependentInputLs=None, \
							transferOutput=False, **keywords):
		"""
		2013.04.03 use addGenericJob()
		2012.1.3
			walltime is in minutes (max time allowed on hoffman2 is 24 hours).
			The executable should be convertBamToFastqAndGzip.
			
		"""
		if workflow is None:
			workflow = self
		if extraDependentInputLs is None:
			extraDependentInputLs = []
		if executable is None:
			executable = self.SamToFastqJava
		extraArgumentList = [outputFnamePrefix]
		output1 = File("%s_1.fastq"%(outputFnamePrefix))
		output2 = File("%s_2.fastq"%(outputFnamePrefix))
		extraOutputLs= [output1, output2]
		
		job = self.addGenericJavaJob(executable=self.SamToFastqJava, jarFile=self.SamToFastqJar, \
					inputFile=inputF, inputArgumentOption="", \
					inputFileList=None, argumentForEachFileInInputFileList=None,\
					outputFile=None, outputArgumentOption="",\
					parentJobLs=parentJobLs, transferOutput=transferOutput, job_max_memory=job_max_memory,\
					frontArgumentList=None, extraArguments=None, extraArgumentList=extraArgumentList, extraOutputLs=extraOutputLs, \
					extraDependentInputLs=extraDependentInputLs, no_of_cpus=None, \
					walltime=walltime, sshDBTunnel=None, **keywords)
		
		"""
		#2013.04.04 old way through a shell wrapper
		
		job = self.addGenericJob(executable=self.convertBamToFastqAndGzip, inputFile=inputF, inputArgumentOption="", \
					outputFile=None, outputArgumentOption=None, \
					inputFileList=None, argumentForEachFileInInputFileList=None, \
					parentJob=None, parentJobLs=parentJobLs, extraDependentInputLs=extraDependentInputLs, \
					extraOutputLs=extraOutputLs, transferOutput=transferOutput, \
					frontArgumentList=None, \
					extraArguments=None, extraArgumentList=extraArgumentList, \
					job_max_memory=job_max_memory,  sshDBTunnel=None, \
					key2ObjectForJob=None, objectWithDBArguments=None, no_of_cpus=None, walltime=walltime)
		"""
		job.output1 = output1
		job.output2 = output2
		return job
	
	def addSplitReadFileJob(self, workflow=None, executable=None, \
							inputF=None, outputFnamePrefix=None, outputFnamePrefixTail="",\
							minNoOfReads=5000000, logFile=None, parentJobLs=None, job_max_memory=2000, walltime = 800, \
							extraDependentInputLs=None, \
							transferOutput=False, **keywords):
		"""
		2013.04.03 use addGenericJob()
		2012.2.9
			argument outputFnamePrefixTail is now useless.
		2012.1.24
			executable is shell/SplitReadFileWrapper.sh
			
			which calls "wc -l" to count the number of reads beforehand to derive a proper minNoOfReads (to avoid files with too few reads).
			
			run SplitReadFile and generate the output directly into the db-affiliated folders
			
			a log file is generated and registered for transfer (so that pegasus won't skip it)
		
			walltime is in minutes (max time allowed on hoffman2 is 24 hours).
			
		"""
		if workflow is None:
			workflow = self
		if extraDependentInputLs is None:
			extraDependentInputLs = []
		frontArgumentList = [self.javaPath, repr(job_max_memory), workflow.SplitReadFileJar]
		extraArgumentList = [outputFnamePrefix, repr(minNoOfReads)]
		extraDependentInputLs.append(workflow.SplitReadFileJar)
		if logFile:
			extraArgumentList.append(logFile)
		
		job = self.addGenericJob(executable=executable, inputFile=inputF, inputArgumentOption="", \
					outputFile=None, outputArgumentOption="-o", \
					inputFileList=None, argumentForEachFileInInputFileList=None, \
					parentJob=None, parentJobLs=parentJobLs, extraDependentInputLs=extraDependentInputLs, \
					extraOutputLs=[logFile], transferOutput=transferOutput, \
					frontArgumentList=frontArgumentList, \
					extraArguments=None, extraArgumentList=extraArgumentList, \
					job_max_memory=job_max_memory,  sshDBTunnel=None, \
					key2ObjectForJob=None, objectWithDBArguments=None, no_of_cpus=None, walltime=walltime)
		return job
	
	def addRegisterAndMoveSplitFileJob(self, workflow=None, executable=None, \
							inputDir=None, outputDir=None, relativeOutputDir=None, logFile=None,\
							individual_sequence_id=None, bamFile=None, library=None, mate_id=None, \
							parentJobLs=None, job_max_memory=100, walltime = 60, \
							commit=0, sequence_format='fastq',\
							extraDependentInputLs=None, extraArguments=None, \
							transferOutput=False, sshDBTunnel=1, **keywords):
		"""
		2013.04.03 call addGenericFile2DBJob() instead
		2012.04.30
			add argument extraArguments, sshDBTunnel
		2012.01.24
			walltime is in minutes (max time allowed on hoffman2 is 24 hours).
			
		"""
		if extraDependentInputLs is None:
			extraDependentInputLs = []
		extraArgumentList =['--inputDir', inputDir, '--outputDir', outputDir, '--relativeOutputDir', relativeOutputDir,\
						'--library', library, '--individual_sequence_id %s'%individual_sequence_id, \
						'--sequence_format', sequence_format]
		if mate_id:
			extraArgumentList.append('--mate_id %s'%(mate_id))
		if bamFile:
			extraArgumentList.extend(['--bamFilePath', bamFile])
			extraDependentInputLs.append(bamFile)
		
		job = self.addGenericFile2DBJob(executable=executable, inputFile=None, inputArgumentOption="-i", \
					outputFile=None, outputArgumentOption="-o", inputFileList=None, \
					data_dir=None, logFile=logFile, commit=commit,\
					parentJobLs=parentJobLs, extraDependentInputLs=extraDependentInputLs, \
					extraOutputLs=None, transferOutput=transferOutput, \
					extraArguments=extraArguments, extraArgumentList=extraArgumentList, \
					job_max_memory=job_max_memory,  sshDBTunnel=sshDBTunnel, walltime=walltime,\
					key2ObjectForJob=None, objectWithDBArguments=self)
		return job
	
	def getInputFnameLsFromInput(self, input=None, suffixSet=set(['.fastq']), fakeSuffix='.gz'):
		"""
		2012.4.30
			this function supercedes self.getAllBamFiles() and it's more flexible.
		"""
		inputFnameLs = []
		if os.path.isdir(input):
			self.getFilesWithSuffixFromFolderRecursive(inputFolder=input, suffixSet=suffixSet, fakeSuffix=fakeSuffix, \
												inputFnameLs=inputFnameLs)
		elif os.path.isfile(input):
			inf = open(input)
			for line in inf:
				inputFnameLs.append(line.strip())
			del inf
		else:
			sys.stderr.write("%s is neither a folder nor a file.\n"%(input))
			sys.exit(4)
		return inputFnameLs

	def getMonkeyID2FastqObjectLsForSouthAfricanDNAData(self, fastqFnameLs=None):
		"""
		2012.6.2
			similar to getMonkeyID2FastqObjectLsForMcGillData() (which is for McGill data)
			
			In pairs like this:
				VSAA2015_1.fastq.gz
				VSAA2015_2.fastq.gz
		"""
		sys.stderr.write("Passing monkeyID2FastqObjectLs from %s files ..."%(len(fastqFnameLs)))
		monkeyID2FastqObjectLs = {}
		import random
		filenameSignaturePattern = re.compile(r'(?P<monkeyID>[a-zA-Z0-9]+)_(?P<mateID>\d).fastq')
		counter = 0
		real_counter = 0
		libraryKey2UniqueLibrary = {}	#McGill's library ID , 7_Index-11, is not unique enough.
		for fastqFname in fastqFnameLs:
			counter += 1
			monkeyIDSearchResult = filenameSignaturePattern.search(fastqFname)
			if monkeyIDSearchResult:
				real_counter += 1
				monkeyID = monkeyIDSearchResult.group('monkeyID')
				mateID = monkeyIDSearchResult.group('mateID')
				filenameSignature = (monkeyID)
					
				#concoct a unique library ID
				libraryKey = (monkeyID)	#this combination insures two ends from the same library are grouped together
				if libraryKey not in libraryKey2UniqueLibrary:
					uniqueLibrary = '%s_%s'%(monkeyID, repr(random.random())[2:])
					libraryKey2UniqueLibrary[libraryKey] = uniqueLibrary
				
				uniqueLibrary = libraryKey2UniqueLibrary[libraryKey]
				fastqObject = PassingData(library=uniqueLibrary, monkeyID=monkeyID, mateID=mateID, absPath=fastqFname)
				if monkeyID not in monkeyID2FastqObjectLs:
					monkeyID2FastqObjectLs[monkeyID] = []
				monkeyID2FastqObjectLs[monkeyID].append(fastqObject)
			else:
				sys.stderr.write("Error: can't parse monkeyID, library, mateID out of %s.\n"%fastqFname)
				sys.exit(4)
		sys.stderr.write(" %s monkeys and %s files in the dictionary.\n"%(len(monkeyID2FastqObjectLs), real_counter))
		return monkeyID2FastqObjectLs

	def addJobsToProcessSouthAfricanDNAData(self, workflow=None, db_vervet=None, bamFname2MonkeyIDMapFname=None, input=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2012.6.2
			input fastq files could be gzipped or not. doesn't matter.
			data generated by Joe DeYoung's core, demultiplexed by ICNN
		"""
		fastqFnameLs = self.getInputFnameLsFromInput(input, suffixSet=set(['.fastq']), fakeSuffix='.gz')	#doesn't matter if fastq is not gzipped
		monkeyID2FastqObjectLs = self.getMonkeyID2FastqObjectLsForSouthAfricanDNAData(fastqFnameLs=fastqFnameLs)
		self.addJobsToSplitAndRegisterSequenceFiles(workflow=workflow, db_vervet=db_vervet, monkeyID2FastqObjectLs=monkeyID2FastqObjectLs, data_dir=data_dir, \
									minNoOfReads=minNoOfReads, commit=commit,\
									sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, sequence_format=sequence_format)		
	
	def addJobsToProcessUNGCVervetData(self, workflow=None, db_vervet=None, bamFname2MonkeyIDMapFname=None, input=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2013.04.04
			UNGC = UCLA Neuroscience Genomics Core
			
			input fastq files could be gzipped or not. doesn't matter.
			data generated by Joe DeYoung's core, demultiplexed by ICNN
		"""
		sampleID2IndividualData = self.getSampleID2IndividualData_UNGC(bamFname2MonkeyIDMapFname)

		fastqFnameLs = self.getInputFnameLsFromInput(input, suffixSet=set(['.fastq']), fakeSuffix='.gz')	#doesn't matter if fastq is not gzipped
		monkeyID2FastqObjectLs = self.getMonkeyID2FastqObjectLsFromUNGCData(fastqFnameLs=fastqFnameLs, \
																	sampleID2IndividualData=sampleID2IndividualData)
		self.addJobsToSplitAndRegisterSequenceFiles(workflow=workflow, db_vervet=db_vervet, monkeyID2FastqObjectLs=monkeyID2FastqObjectLs, \
									data_dir=data_dir, \
									minNoOfReads=minNoOfReads, commit=commit,\
									sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, sequence_format=sequence_format)
	
	def getSampleID2IndividualData_UNGC(self, inputFname=None):
		"""
		2013.04.04
			Format is like this from UNGC  = UCLA Neuroscience Genomics Core:
			FCID	Lane	sample ID	sample code	sample name	Index	Description	SampleProject
			D1HYNACXX	1	Ilmn Human control pool ( 4plex)	IP1			INDEX IS UNKNOWN prepared by Illumina (4 plex pool)	2013-029A
			D1HYNACXX	2	UNGC Human Sample 1	S1	AS001A	ATTACTCG	TruSeq DNA PCR Free beta kit	2013-029A
		"""
		sys.stderr.write("Getting  sampleID2IndividualData from %s ..."%(inputFname))
		sampleID2IndividualData = {}
		
		reader = MatrixFile(inputFname, openMode='r', delimiter=',')
		reader.constructColName2IndexFromHeader()
		sampleIDIndex = reader.getColIndexGivenColHeader("sample ID")
		sampleNameIndex = reader.getColIndexGivenColHeader("sample name")
		libraryIndexIndex = reader.getColIndexGivenColHeader("Index")
		
		for row in reader:
			sampleID = row[sampleIDIndex].replace(' ', '_')	#2013.04.04 stupid quirks
			sampleName = row[sampleNameIndex]
			libraryIndex = row[libraryIndexIndex]
			if sampleID not in sampleID2IndividualData:
				sampleID2IndividualData[sampleID] = PassingData(sampleName=sampleName, libraryIndexList=[])
			if sampleName!=sampleID2IndividualData[sampleID].sampleName:
				sys.stderr.write("Error: sampleID %s is associated with two different sample names (%s, %s).\n"%\
								(sampleID, sampleName, sampleID2IndividualData[sampleID].sampleName))
				raise
			sampleID2IndividualData[sampleID].libraryIndexList.append(libraryIndex)
		
		sys.stderr.write("%s entries.\n"%(len(sampleID2IndividualData)))
		return sampleID2IndividualData
	
	def getMonkeyID2FastqObjectLsFromUNGCData(self, fastqFnameLs=None, sampleID2IndividualData=None):
		"""
		2013.04.05 bugfix. this ensures two ends from same library have same library.
		2013.04.04
			UNGC  = UCLA Neuroscience Genomics Core
			In pairs like this:
				UNGC_Vervet_Sample_11_1.fastq.gz
				UNGC_Vervet_Sample_11_2.fastq.gz
		"""
		sys.stderr.write("Passing monkeyID2FastqObjectLs from %s files ..."%(len(fastqFnameLs)))
		monkeyID2FastqObjectLs = {}
		import re, random
		filenameSignaturePattern = re.compile(r'(?P<sampleID>[\w\d]+)_(?P<mateID>\d).fastq')
		counter = 0
		real_counter = 0
		libraryKey2UniqueLibrary = {}	#McGill's library ID , 7_Index-11, is not unique enough.
		for fastqFname in fastqFnameLs:
			counter += 1
			monkeyIDSearchResult = filenameSignaturePattern.search(fastqFname)
			if monkeyIDSearchResult:
				real_counter += 1
				sampleID = monkeyIDSearchResult.group('sampleID')
				mateID = monkeyIDSearchResult.group('mateID')
				if sampleID in sampleID2IndividualData:
					individualData = sampleID2IndividualData.get(sampleID)
					monkeyID = individualData.sampleName
					library = '_'.join(individualData.libraryIndexList)
					
					libraryKey = (monkeyID, library)
					if libraryKey not in libraryKey2UniqueLibrary:	#2013.04.05 bugfix. this ensures two ends from same library have same library.
						uniqueLibrary = '%s_%s_%s'%(monkeyID, library, repr(random.random())[2:])
						libraryKey2UniqueLibrary[libraryKey] = uniqueLibrary
					else:
						sys.stderr.write("libraryKey %s of %s is already in libraryKey2UniqueLibrary with unique library = %s.\n"%\
										(libraryKey, fastqFname, libraryKey2UniqueLibrary[libraryKey]))
					
					uniqueLibrary = libraryKey2UniqueLibrary[libraryKey]
					fastqObject = PassingData(library=uniqueLibrary, monkeyID=monkeyID, mateID=mateID, absPath=fastqFname)
					if monkeyID not in monkeyID2FastqObjectLs:
						monkeyID2FastqObjectLs[monkeyID] = []
					monkeyID2FastqObjectLs[monkeyID].append(fastqObject)
				else:
					sys.stderr.write("sampleID %s not in sampleID2IndividualData.\n"%(sampleID))
			else:
				sys.stderr.write("Error: can't parse sampleID, mateID out of %s.\n"%fastqFname)
				raise
		sys.stderr.write(" %s monkeys and %s files in the dictionary.\n"%(len(monkeyID2FastqObjectLs), real_counter))
		return monkeyID2FastqObjectLs
	
	
	def getFilenameSignature2MonkeyID_SouthAfricanRNAData(self, inputFname=None):
		"""
		2012.6.2 inputFname is tab-delimited, looks like this
		
			VSAC1012_R      ATCACG  sample2
			VSAF1009_R      ATCACG  sample1
			VSAB2009_RN     TAGCTT  sample2
			VSAB2011_R      TAGCTT  sample1
			VSAB3001_RN     GGCTAC  sample2
			VSAB5004_R      GGCTAC  sample1
			VSAA2015_RN     CTTGTA  sample2
		"""
		sys.stderr.write("Getting filenameSignature2MonkeyID dictionary from %s ..."%(inputFname))
		filenameSignature2MonkeyID = {}
		reader = csv.reader(open(inputFname), delimiter='\t')
		monkeyIDIndex = 0
		folderNameIndex = 1
		subSampleNameIndex = 2
		monkeyIDPattern = re.compile(r'(\w+)_R[\w]*')	# 2012.6.2 VSAA2015_RN or VSAB5004_R
		for row in reader:
			monkeyID = row[monkeyIDIndex]
			pa_search = monkeyIDPattern.search(monkeyID)
			if pa_search:
				monkeyID = pa_search.group(1)
			else:
				sys.stderr.write("Warning: could not parse monkey ID from %s. Ignore.\n"%(monkeyID))
				continue
			folderName = row[folderNameIndex]
			subSampleName = row[subSampleNameIndex]
			filenameSignature = (folderName, subSampleName)
			if filenameSignature in filenameSignature2MonkeyID:
				sys.stderr.write("Error: filenameSignature %s already in filenameSignature2MonkeyID.\n"%(filenameSignature))
				sys.exit(3)
			filenameSignature2MonkeyID[filenameSignature] = monkeyID
		sys.stderr.write("%s entries.\n"%(len(filenameSignature2MonkeyID)))
		return filenameSignature2MonkeyID
	
	def getMonkeyID2FastqObjectLsForSouthAfricanRNAData(self, fastqFnameLs=None, filenameSignature2MonkeyID=None):
		"""
		2012.6.2
			similar to getMonkeyID2FastqObjectLsForMcGillData() (which is for McGill data)
			
			In pairs like this:
			.../GCCAAT/tile_1101_sample1_end1.fastq
			.../GCCAAT/tile_1101_sample1_end2.fastq
		"""
		sys.stderr.write("Passing monkeyID2FastqObjectLs from %s files ..."%(len(fastqFnameLs)))
		monkeyID2FastqObjectLs = {}
		import re, random
		filenameSignaturePattern = re.compile(r'/(?P<folderName>[ACGT]{6})/(?P<library>[\w]+)_(?P<subSampleName>sample[12])_end(?P<mateID>\d).fastq')
		counter = 0
		real_counter = 0
		libraryKey2UniqueLibrary = {}	#McGill's library ID , 7_Index-11, is not unique enough.
		for fastqFname in fastqFnameLs:
			counter += 1
			monkeyIDSearchResult = filenameSignaturePattern.search(fastqFname)
			if monkeyIDSearchResult:
				real_counter += 1
				library = monkeyIDSearchResult.group('library')	#tile_1101
				folderName = monkeyIDSearchResult.group('folderName')
				subSampleName = monkeyIDSearchResult.group('subSampleName')
				mateID = monkeyIDSearchResult.group('mateID')
				filenameSignature = (folderName, subSampleName)
				if filenameSignature in filenameSignature2MonkeyID:
					monkeyID = filenameSignature2MonkeyID.get(filenameSignature)
					
					#concoct a unique library ID
					libraryKey = (folderName, library)	#this combination insures two ends from the same library are grouped together
					if libraryKey not in libraryKey2UniqueLibrary:
						uniqueLibrary = '%s_%s_%s'%(folderName, library, repr(random.random())[2:])
						libraryKey2UniqueLibrary[libraryKey] = uniqueLibrary
					
					uniqueLibrary = libraryKey2UniqueLibrary[libraryKey]
					fastqObject = PassingData(library=uniqueLibrary, monkeyID=monkeyID, mateID=mateID, absPath=fastqFname)
					if monkeyID not in monkeyID2FastqObjectLs:
						monkeyID2FastqObjectLs[monkeyID] = []
					monkeyID2FastqObjectLs[monkeyID].append(fastqObject)
				else:
					sys.stderr.write("%s not in filenameSignature2MonkeyID.\n"%(filenameSignature))
			else:
				sys.stderr.write("Error: can't parse monkeyID, library, mateID out of %s.\n"%fastqFname)
				sys.exit(4)
		sys.stderr.write(" %s monkeys and %s files in the dictionary.\n"%(len(monkeyID2FastqObjectLs), real_counter))
		return monkeyID2FastqObjectLs
	
	def addJobsToProcessSouthAfricanRNAData(self, workflow, db_vervet=None, bamFname2MonkeyIDMapFname=None, input=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2012.6.1
			input fastq files could be gzipped or not. doesn't matter.
			data generated by Joe DeYoung's core, demultiplexed by ICNN (Charles in particular)
		"""
		filenameSignature2MonkeyID = self.getFilenameSignature2MonkeyID_SouthAfricanRNAData(bamFname2MonkeyIDMapFname)
		
		fastqFnameLs = self.getInputFnameLsFromInput(input, suffixSet=set(['.fastq']), fakeSuffix='.gz')	#doesn't matter if fastq is not gzipped
		monkeyID2FastqObjectLs = self.getMonkeyID2FastqObjectLsForNamSouthAfricanRNAData(fastqFnameLs=fastqFnameLs, \
																	filenameSignature2MonkeyID=filenameSignature2MonkeyID)
		self.addJobsToSplitAndRegisterSequenceFiles(workflow=workflow, db_vervet=db_vervet, monkeyID2FastqObjectLs=monkeyID2FastqObjectLs, data_dir=data_dir, \
									minNoOfReads=minNoOfReads, commit=commit,\
									sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, sequence_format=sequence_format)		
	
	def getMonkeyID2FastqObjectLsForMcGillData(self, fastqFnameLs=None,):
		"""
		2013.1.30 add fixed monkey ID prefixes (VWP, VGA, etc.) into monkeyIDPattern due to new not-all-number monkey IDs.
		
HI.0628.001.D701.VGA00010_R1.fastq.gz  HI.0628.004.D703.VWP00384_R1.fastq.gz  HI.0628.007.D703.VWP10020_R1.fastq.gz
HI.0628.001.D701.VGA00010_R2.fastq.gz  HI.0628.004.D703.VWP00384_R2.fastq.gz  HI.0628.007.D703.VWP10020_R2.fastq.gz
		2012.4.30
			each fastq file looks like 7_Index-11.2006013_R1.fastq.gz, 7_Index-11.2006013_R2.fastq.gz,
				7_Index-10.2005045_replacement_R1.fastq.gz, 7_Index-10.2005045_replacement_R2.fastq.gz
			
			The data from McGill is dated 2012.4.27.
			Each monkey is sequenced at 1X. There are 96 of them. Each library seems to contain 2 monkeys.
				But each monkey has only 1 library.
			
			8_Index_23.2008126_R1.fastq.gz
			8_Index_23.2008126_R2.fastq.gz
			8_Index_23.2009017_R1.fastq.gz
			8_Index_23.2009017_R2.fastq.gz

		"""
		sys.stderr.write("Passing monkeyID2FastqObjectLs from %s files ..."%(len(fastqFnameLs)))
		monkeyID2FastqObjectLs = {}
		import re, random
		#monkeyIDPattern = re.compile(r'(?P<library>[-\w]+)\.(?P<monkeyID>\d+)((_replacement)|(_pool)|())_R(?P<mateID>\d).fastq.gz')
		monkeyIDPattern = re.compile(r'(?P<library>[-\w]+)\.(?P<monkeyID>((VWP)|(VGA)|(VSA)|())\d+)((_replacement)|(_pool)|())_R(?P<mateID>\d).fastq.gz')
		counter = 0
		real_counter = 0
		libraryKey2UniqueLibrary = {}	#McGill's library ID , 7_Index-11, is not unique enough.
		for fastqFname in fastqFnameLs:
			counter += 1
			monkeyIDSearchResult = monkeyIDPattern.search(fastqFname)
			if monkeyIDSearchResult:
				real_counter += 1
				library = monkeyIDSearchResult.group('library')
				monkeyID = monkeyIDSearchResult.group('monkeyID')
				mateID = monkeyIDSearchResult.group('mateID')
				#concoct a unique library ID
				if library not in libraryKey2UniqueLibrary:
					libraryKey2UniqueLibrary[library] = '%s_%s'%(library, repr(random.random())[2:])
				uniqueLibrary = libraryKey2UniqueLibrary[library]
				fastqObject = PassingData(library=uniqueLibrary, monkeyID=monkeyID, mateID=mateID, absPath=fastqFname)
				if monkeyID not in monkeyID2FastqObjectLs:
					monkeyID2FastqObjectLs[monkeyID] = []
				monkeyID2FastqObjectLs[monkeyID].append(fastqObject)
			else:
				sys.stderr.write("Error: can't parse monkeyID, library, mateID out of %s.\n"%fastqFname)
				sys.exit(4)
		sys.stderr.write(" %s monkeys and %s files in the dictionary.\n"%(len(monkeyID2FastqObjectLs), real_counter))
		return monkeyID2FastqObjectLs
	
	def addJobsToSplitAndRegisterSequenceFiles(self, workflow=None, db_vervet=None, monkeyID2FastqObjectLs=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2012.6.2
			split out of addJobsToProcessMcGillData(), used also in addJobsToProcessDeYoungCoreData().
			
		"""
		if workflow is None:
			workflow = self
		sys.stderr.write("Adding split-read & register jobs ...")
		filenameKey2PegasusFile = {}
		for monkeyID, fastqObjectLs in monkeyID2FastqObjectLs.iteritems():
			individual_sequence = self.addMonkeySequence(db_vervet=db_vervet, monkeyID=monkeyID, \
								sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, \
								sequence_format=sequence_format, data_dir=data_dir)
			
			sequenceOutputDir = os.path.join(data_dir, individual_sequence.path)
			sequenceOutputDirJob = self.addMkDirJob(outputDir=sequenceOutputDir)
			
			splitOutputDir = '%s'%(individual_sequence.id)
			#same directory containing split files from both mates is fine as RegisterAndMoveSplitSequenceFiles could pick up.
			splitOutputDirJob = self.addMkDirJob( outputDir=splitOutputDir)
			
			
			
			for fastqObject in fastqObjectLs:
				library = fastqObject.library
				mateID = fastqObject.mateID
				fastqPath = fastqObject.absPath
				filenameKey = (library, os.path.basename(fastqPath))
				if filenameKey in filenameKey2PegasusFile:
					fastqFile = filenameKey2PegasusFile.get(filenameKey)
					sys.stderr.write("Error: file %s has been registered with monkey %s. Can't happen.\n"%(fastqFile.monkeyID))
					sys.exit(3)
					import pdb
					pdb.set_trace()
					continue
				else:
					fastqFile = self.registerOneInputFile(workflow, fastqPath, folderName=library)
					fastqFile.monkeyID = monkeyID
					fastqFile.fastqObject= fastqObject
					filenameKey2PegasusFile[filenameKey] = fastqFile
			
				splitFastQFnamePrefix = os.path.join(splitOutputDir, '%s_%s_%s'%(individual_sequence.id, library, mateID))
				logFile = File('%s_%s_%s.split.log'%(individual_sequence.id, library, mateID))
				splitReadFileJob1 = self.addSplitReadFileJob(workflow, executable=workflow.SplitReadFileWrapper, \
								inputF=fastqFile, outputFnamePrefix=splitFastQFnamePrefix, \
								outputFnamePrefixTail="", minNoOfReads=minNoOfReads, \
								logFile=logFile, parentJobLs=[splitOutputDirJob], \
								job_max_memory=2000, walltime = 800, \
								extraDependentInputLs=[], transferOutput=True)
				
				logFile = File('%s_%s_%s.register.log'%(individual_sequence.id, library, mateID))
				# 2012.4.30 add '--mate_id_associated_with_bam' to RegisterAndMoveSplitSequenceFiles so that it will be used to distinguish IndividualSequenceFileRaw
				registerJob1 = self.addRegisterAndMoveSplitFileJob(workflow, executable=workflow.RegisterAndMoveSplitSequenceFiles, \
								inputDir=splitOutputDir, outputDir=sequenceOutputDir, relativeOutputDir=individual_sequence.path, logFile=logFile,\
								individual_sequence_id=individual_sequence.id, bamFile=fastqFile, library=library, mate_id=mateID, \
								parentJobLs=[splitReadFileJob1, sequenceOutputDirJob], job_max_memory=100, walltime = 60, \
								commit=commit, sequence_format=sequence_format, extraDependentInputLs=[], \
								extraArguments='--mate_id_associated_with_bam', \
								transferOutput=True, sshDBTunnel=self.needSSHDBTunnel)
			
		sys.stderr.write("%s jobs.\n"%(self.no_of_jobs))
	
	def addJobsToProcessMcGillData(self, workflow=None, db_vervet=None, bamFname2MonkeyIDMapFname=None, input=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2012.4.30
		"""
		fastqFnameLs = self.getInputFnameLsFromInput(input, suffixSet=set(['.fastq']), fakeSuffix='.gz')
		monkeyID2FastqObjectLs = self.getMonkeyID2FastqObjectLsForMcGillData(fastqFnameLs)
		
		self.addJobsToSplitAndRegisterSequenceFiles(workflow=workflow, db_vervet=db_vervet, \
									monkeyID2FastqObjectLs=monkeyID2FastqObjectLs, data_dir=data_dir, \
									minNoOfReads=minNoOfReads, commit=commit,\
									sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, sequence_format=sequence_format)
		
	
	def addJobsToProcessWUSTLData(self, workflow, db_vervet=None, bamFname2MonkeyIDMapFname=None, input=None, data_dir=None, \
			minNoOfReads=None, commit=None,\
			sequencer_name=None, sequence_type_name=None, sequence_format=None):
		"""
		2012.4.30
		"""
		bamBaseFname2MonkeyID = self.getBamBaseFname2MonkeyID_WUSTLDNAData(bamFname2MonkeyIDMapFname)
		bamFnameLs = self.getInputFnameLsFromInput(input, suffixSet=set(['.bam', '.sam']), fakeSuffix='.gz')
		
		sys.stderr.write("%s total bam files.\n"%(len(bamFnameLs)))
		
		sam2fastqOutputDir = 'sam2fastq'
		sam2fastqOutputDirJob = self.addMkDirJob(outputDir=sam2fastqOutputDir)
		
		for bamFname in bamFnameLs:
			bamBaseFname = os.path.split(bamFname)[1]
			if bamBaseFname not in bamBaseFname2MonkeyID:
				sys.stderr.write("%s doesn't have monkeyID affiliated with.\n"%(bamFname))
				continue
			monkeyID = bamBaseFname2MonkeyID.get(bamBaseFname)
			individual_sequence = self.addMonkeySequence(db_vervet=db_vervet, monkeyID=monkeyID, \
								sequencer_name=sequencer_name, sequence_type_name=sequence_type_name, \
								sequence_format=sequence_format, data_dir=data_dir)
			#2012.2.10 stop passing path_to_original_sequence=bamFname to self.addMonkeySequence()
			
			"""
			#2012.2.10 temporary, during transition from old records to new ones.
			newISQPath = individual_sequence.constructRelativePathForIndividualSequence()
			newISQPath = '%s_split'%(newISQPath)
			if individual_sequence.path is None or individual_sequence.path !=newISQPath:
				individual_sequence.path = newISQPath
				session.add(individual_sequence)
				session.flush()
			"""
			
			sequenceOutputDir = os.path.join(data_dir, individual_sequence.path)
			sequenceOutputDirJob = self.addMkDirJob(outputDir=sequenceOutputDir)
			
			bamInputF = yh_pegasus.registerFile(workflow, bamFname)
			
			bamBaseFname = os.path.split(bamFname)[1]
			bamBaseFnamePrefix = os.path.splitext(bamBaseFname)[0]
			library = bamBaseFnamePrefix
			
			outputFnamePrefix = os.path.join(sam2fastqOutputDir, '%s_%s'%(individual_sequence.id, library))
			
			convertBamToFastqAndGzip_job = self.addConvertBamToFastqAndGzipJob(executable=workflow.SamToFastqJava, \
							inputF=bamInputF, outputFnamePrefix=outputFnamePrefix, \
							parentJobLs=[sam2fastqOutputDirJob], job_max_memory=2000, walltime = 800, \
							extraDependentInputLs=[], \
							transferOutput=False)
			
			splitOutputDir = '%s_%s'%(individual_sequence.id, library)
			#same directory containing split files from both mates is fine as RegisterAndMoveSplitSequenceFiles could pick up.
			splitOutputDirJob = self.addMkDirJob( outputDir=splitOutputDir)
			
			
			mate_id = 1
			splitFastQFnamePrefix = os.path.join(splitOutputDir, '%s_%s_%s'%(individual_sequence.id, library, mate_id))
			logFile = File('%s_%s_%s.split.log'%(individual_sequence.id, library, mate_id))
			splitReadFileJob1 = self.addSplitReadFileJob(workflow, executable=workflow.SplitReadFileWrapper, \
							inputF=convertBamToFastqAndGzip_job.output1, outputFnamePrefix=splitFastQFnamePrefix, \
							outputFnamePrefixTail="", minNoOfReads=minNoOfReads, \
							logFile=logFile, parentJobLs=[convertBamToFastqAndGzip_job, splitOutputDirJob], \
							job_max_memory=2000, walltime = 800, \
							extraDependentInputLs=[], transferOutput=True)
			
			logFile = File('%s_%s_%s.register.log'%(individual_sequence.id, library, mate_id))
			registerJob1 = self.addRegisterAndMoveSplitFileJob(workflow, executable=workflow.RegisterAndMoveSplitSequenceFiles, \
							inputDir=splitOutputDir, outputDir=sequenceOutputDir, relativeOutputDir=individual_sequence.path, logFile=logFile,\
							individual_sequence_id=individual_sequence.id, bamFile=bamInputF, library=library, mate_id=mate_id, \
							parentJobLs=[splitReadFileJob1, sequenceOutputDirJob], job_max_memory=100, walltime = 60, \
							commit=commit, sequence_format=sequence_format, extraDependentInputLs=[], \
							transferOutput=True, sshDBTunnel=self.needSSHDBTunnel)
			#handle the 2nd end
			mate_id = 2
			splitFastQFnamePrefix = os.path.join(splitOutputDir, '%s_%s_%s'%(individual_sequence.id, library, mate_id))
			logFile = File('%s_%s_%s.split.log'%(individual_sequence.id, library, mate_id))
			splitReadFileJob2 = self.addSplitReadFileJob(workflow, executable=workflow.SplitReadFileWrapper, \
							inputF=convertBamToFastqAndGzip_job.output2, outputFnamePrefix=splitFastQFnamePrefix, \
							outputFnamePrefixTail="", minNoOfReads=minNoOfReads, \
							logFile=logFile, parentJobLs=[convertBamToFastqAndGzip_job, splitOutputDirJob], \
							job_max_memory=2000, walltime = 800, \
							extraDependentInputLs=[], transferOutput=True)
			
			logFile = File('%s_%s_%s.register.log'%(individual_sequence.id, library, mate_id))
			registerJob1 = self.addRegisterAndMoveSplitFileJob(workflow, executable=workflow.RegisterAndMoveSplitSequenceFiles, \
							inputDir=splitOutputDir, outputDir=sequenceOutputDir, relativeOutputDir=individual_sequence.path, logFile=logFile,\
							individual_sequence_id=individual_sequence.id, bamFile=bamInputF, library=library, mate_id=mate_id, \
							parentJobLs=[splitReadFileJob2, sequenceOutputDirJob], job_max_memory=100, walltime = 60, \
							commit=commit, sequence_format=sequence_format, extraDependentInputLs=[], \
							transferOutput=True, sshDBTunnel=self.needSSHDBTunnel)
			
			"""
			
			jobFname = os.path.join(self.jobFileDir, 'job%s.bam2fastq.sh'%(monkeyID))
			self.writeQsubJob(jobFname, bamFname, os.path.join(self.data_dir, individual_sequence.path), self.vervet_path)
			commandline = 'qsub %s'%(jobFname)
			if self.commit:	#qsub only when db transaction will be committed.
				return_data = runLocalCommand(commandline, report_stderr=True, report_stdout=True)
			"""
		sys.stderr.write("%s jobs.\n"%(self.no_of_jobs))
	
	def run(self):
		"""
		2011-8-3
		"""
		if self.debug:
			import pdb
			pdb.set_trace()
		
		db_vervet = self.db_vervet
		session = db_vervet.session
		session.begin()
		
		if not self.data_dir:
			self.data_dir = db_vervet.data_dir
		
		if not self.local_data_dir:
			self.local_data_dir = db_vervet.data_dir
		
		workflow = self.initiateWorkflow()
		
		self.registerJars()
		self.registerExecutables()
		self.registerCustomExecutables(workflow=workflow)
		
		self.addJobsDict[self.inputType](workflow, db_vervet=db_vervet, bamFname2MonkeyIDMapFname=self.bamFname2MonkeyIDMapFname, \
											input=self.input, \
					data_dir=self.data_dir, minNoOfReads=self.minNoOfReads, commit=self.commit,\
					sequencer_name=self.sequencer_name, sequence_type_name=self.sequence_type_name, sequence_format=self.sequence_format)
		# Write the DAX to stdout
		outf = open(self.outputFname, 'w')
		self.writeXML(outf)
		if self.commit:
			session.commit()
		else:
			session.rollback()
		
if __name__ == '__main__':
	main_class = UnpackAndAddIndividualSequence2DB
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	instance = main_class(**po.long_option2value)
	instance.run()
