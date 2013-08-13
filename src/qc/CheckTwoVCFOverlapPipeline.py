#!/usr/bin/env python
"""
Examples:
	%s
	
	dirPrefix=AlignmentToCallPipeline_4HighCovVRC_isq_15_18_vs_524_top4Contigs_single_sample_condor_20111105T0143/556_
	%s -i $dirPrefix\gatk/ -I $dirPrefix\samtools/ -l condorpool -j condorpool
		-o dags/CheckTwoVCF/4HighCovVRC_isq_15_18_vs_524_top804Contigs_gatk_vs_samtools_overlap_stat.xml -z uclaOffice -u yh -k genome
		-C 100
	
	#2012.8.3 compare two VCF on hcondor, do per-sample checking
	%s -i AlignmentToCall_ISQ643_646_vs_524_Contig731.2012.8.2T1530/samtools/
		-I AlignmentToCall_ISQ643_646_vs_524_method7Contig731Sites.2012.8.2T1610/samtools/
		-l hcondor -j hcondor -o dags/CheckTwoVCF/CheckTwoVCF_ISQ643_646_vs_524_MultiSample_vs_Method7ROICalling_Contig731.xml
		-z localhost -u yh -k genome -C 1
		-e /u/home/eeskin/polyacti/  -t /u/home/eeskin/polyacti/NetworkData/vervet/db/ -D /u/home/eeskin/polyacti/NetworkData/vervet/db/
		--perSampleMatchFraction
	
Description:
	2011-11-7 pegasus workflow that compares overlap between two vcf files (mapper/CheckTwoVCFOverlap.py),
			calculate mismatch rate, pi statistics based on the intersection
"""
import sys, os, math
__doc__ = __doc__%(sys.argv[0], sys.argv[0], sys.argv[0])

bit_number = math.log(sys.maxint)/math.log(2)
if bit_number>40:	   #64bit
	sys.path.insert(0, os.path.expanduser('~/lib64/python'))
	sys.path.insert(0, os.path.join(os.path.expanduser('~/script64')))
else:   #32bit
	sys.path.insert(0, os.path.expanduser('~/lib/python'))
	sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import subprocess, cStringIO
from Pegasus.DAX3 import File, Executable, PFN
from pymodule import ProcessOptions, getListOutOfStr, PassingData, GenomeDB, NextGenSeq
from pymodule.pegasus import yh_pegasus
from vervet.src import VervetDB, AbstractVervetWorkflow

class CheckTwoVCFOverlapPipeline(AbstractVervetWorkflow):
	__doc__ = __doc__
	option_default_dict = AbstractVervetWorkflow.option_default_dict.copy()
	option_default_dict.pop(('inputDir', 0, ))
	option_default_dict.update({
						('vcf1Dir', 1, ): ['', 'i', 1, 'input folder that contains vcf or vcf.gz files', ],\
						('vcf2Dir', 1, ): ['', 'I', 1, 'input folder that contains vcf or vcf.gz files', ],\
						('perSampleMatchFraction', 0, ): [0, '', 0, 'whether calculating per-sample mismatch fraction or not.', ],\
						})

	def __init__(self,  **keywords):
		"""
		"""
		AbstractVervetWorkflow.__init__(self, **keywords)
	
	def registerCustomExecutables(self, workflow):
		"""
		2011-11-28
		"""
		namespace = workflow.namespace
		version = workflow.version
		operatingSystem = workflow.operatingSystem
		architecture = workflow.architecture
		clusters_size = workflow.clusters_size
		site_handler = workflow.site_handler
		vervetSrcPath = self.vervetSrcPath
		
		
	
	def run(self):
		"""
		"""
		
		if self.debug:
			import pdb
			pdb.set_trace()
		
		#without commenting out db_vervet connection code. schema "genome" wont' be default path.
		db_genome = GenomeDB.GenomeDatabase(drivername=self.drivername, db_user=self.db_user,
						db_passwd=self.db_passwd, hostname=self.hostname, dbname=self.dbname, schema="genome")
		db_genome.setup(create_tables=False)
		chr2size = db_genome.getTopNumberOfChomosomes(contigMaxRankBySize=80000, contigMinRankBySize=1, tax_id=60711, sequence_type_id=9)
		
		# Create a abstract dag
		workflowName = os.path.splitext(os.path.basename(self.outputFname))[0]
		workflow = self.initiateWorkflow(workflowName)
		
		self.registerJars(workflow)
		self.registerCommonExecutables(workflow)
		self.registerCustomExecutables(workflow)
		
		
		statOutputDir = "statDir"
		statOutputDirJob = yh_pegasus.addMkDirJob(workflow, mkdir=workflow.mkdirWrap, outputDir=statOutputDir)
		
		import re
		chr_pattern = re.compile(r'(\w+\d+).*')
		input_site_handler = self.input_site_handler
		
		counter = 1
		
		
		plotOutputDir = "%sPlot"%(self.pegasusFolderName)
		plotOutputDirJob = yh_pegasus.addMkDirJob(workflow, mkdir=workflow.mkdirWrap, outputDir=plotOutputDir)
		counter += 1
		
		overlapStatF = File('overlapSites.perChromosome.stat.tsv')
		overlapSitesByChromosomeMergeJob=self.addStatMergeJob(statMergeProgram=workflow.mergeSameHeaderTablesIntoOne, \
					outputF=overlapStatF, parentJobLs=None, \
					extraDependentInputLs=None, transferOutput=True, extraArguments=None)
		counter += 1
		
		overlapSitesMergeJob=self.addStatMergeJob(statMergeProgram=workflow.mergeSameHeaderTablesIntoOne, \
					outputF=File("overlapSites.tsv"), parentJobLs=None, \
					extraDependentInputLs=None, transferOutput=True, extraArguments=None)
		counter += 1
		
		perSampleMatchFractionFile = File('perSampleMatchFraction.tsv')
		perSampleMatchFractionReduceJob = self.addStatMergeJob(statMergeProgram=workflow.ReduceMatrixBySumSameKeyColsAndThenDivide, \
					outputF=perSampleMatchFractionFile, extraDependentInputLs=[], transferOutput=True, \
					extraArguments='-k 0 -v 1-2')
		outputFile = File( os.path.join(plotOutputDir, 'perSampleMatchFraction_Hist.png'))
		#no spaces or parenthesis or any other shell-vulnerable letters in the x or y axis labels (whichColumnPlotLabel, xColumnPlotLabel)
		self.addDrawHistogramJob(workflow=workflow, executable=workflow.DrawHistogram, inputFileList=[perSampleMatchFractionFile], \
							outputFile=outputFile, \
					whichColumn=None, whichColumnHeader="no_of_matches_by_no_of_non_NA_pairs", whichColumnPlotLabel="matchFraction", \
					logY=None, logCount=True, valueForNonPositiveYValue=50,\
					minNoOfTotal=10,\
					figureDPI=100, samplingRate=1,\
					parentJobLs=[plotOutputDirJob, perSampleMatchFractionReduceJob ], \
					extraDependentInputLs=None, \
					extraArguments=None, transferOutput=True,  job_max_memory=2000)
		counter += 2
		
		overlapStatSumF = File('overlapSites.wholeGenome.stat.tsv')
		overlapStatSumJob = self.addStatMergeJob(statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
						outputF=overlapStatSumF, extraDependentInputLs=[], transferOutput=True, \
						extraArguments='-k 1000000 -v 1-25000')	#The key column (-k 1000000) doesn't exist.
						# essentially merging every rows into one 
						##25000 is a random big upper limit. 100 monkeys => 101*3 + 9 => 312 columns
						#2012.8.17 the number of columns no longer expand as the number of samples because it's split into perSampleMatchFractionFile.
		self.addInputToStatMergeJob(statMergeJob=overlapStatSumJob, inputF=overlapStatF, \
							parentJobLs=[overlapSitesByChromosomeMergeJob])
		counter += 1
		
		vcfFileID2object_1 = self.getVCFFileID2object(self.vcf1Dir)
		vcfFileID2object_2 = self.getVCFFileID2object(self.vcf2Dir)
		sharedVCFFileIDSet = set(vcfFileID2object_1.keys())&set(vcfFileID2object_2.keys())
		sys.stderr.write("%s shared vcf files.\n"%(len(sharedVCFFileIDSet)))
		
		for vcfFileID in sharedVCFFileIDSet:
			gatkVCFAbsPath = vcfFileID2object_1.get(vcfFileID).vcfFilePath
			samtoolsVCFAbsPath = vcfFileID2object_2.get(vcfFileID).vcfFilePath
			if not NextGenSeq.isVCFFileEmpty(gatkVCFAbsPath) and not NextGenSeq.isVCFFileEmpty(samtoolsVCFAbsPath, \
									checkContent=self.checkEmptyVCFByReading):	#make sure the samtools vcf is not empty
				gatkVCFFileBaseName = os.path.basename(gatkVCFAbsPath)
				chromosome = vcfFileID
				chr_size = chr2size.get(chromosome)
				if chr_size is None:
					sys.stderr.write("size for chromosome %s is unknown. set it to 1000.\n"%(chromosome))
					chr_size = 1000
				
				vcf1 = File(os.path.join('vcf1', gatkVCFFileBaseName))	#relative path
				vcf1.addPFN(PFN("file://" + gatkVCFAbsPath, input_site_handler))
				workflow.addFile(vcf1)
				
				vcf2 = File(os.path.join('vcf2', os.path.basename(samtoolsVCFAbsPath)))	#relative path
				vcf2.addPFN(PFN("file://" + samtoolsVCFAbsPath, input_site_handler))
				workflow.addFile(vcf2)
				
				
				outputFnamePrefix = os.path.join(statOutputDir, os.path.splitext(gatkVCFFileBaseName)[0])
				checkTwoVCFOverlapJob = self.addCheckTwoVCFOverlapJob(workflow, executable=workflow.CheckTwoVCFOverlap, \
						vcf1=vcf1, vcf2=vcf2, chromosome=chromosome, chrLength=chr_size, \
						outputFnamePrefix=outputFnamePrefix, parentJobLs=[statOutputDirJob], \
						extraDependentInputLs=[], transferOutput=False, extraArguments=" -m %s "%(self.minDepth),\
						perSampleMatchFraction=self.perSampleMatchFraction,\
						job_max_memory=1000)
				
				self.addInputToStatMergeJob(statMergeJob=overlapSitesByChromosomeMergeJob, \
							inputF=checkTwoVCFOverlapJob.output, \
							parentJobLs=[checkTwoVCFOverlapJob], extraDependentInputLs=[])
				self.addInputToStatMergeJob(statMergeJob=overlapSitesMergeJob, \
							inputF=checkTwoVCFOverlapJob.overlapSitePosFile, \
							parentJobLs=[checkTwoVCFOverlapJob], extraDependentInputLs=[])
				self.addInputToStatMergeJob(statMergeJob=perSampleMatchFractionReduceJob, \
							inputF=checkTwoVCFOverlapJob.perSampleFile, \
							parentJobLs=[checkTwoVCFOverlapJob], extraDependentInputLs=[])
				counter += 1
		sys.stderr.write("%s jobs.\n"%(counter+1))
		
		# Write the DAX to stdout
		outf = open(self.outputFname, 'w')
		workflow.writeXML(outf)
		


	
if __name__ == '__main__':
	main_class = CheckTwoVCFOverlapPipeline
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	instance = main_class(**po.long_option2value)
	instance.run()
