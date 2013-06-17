#!/usr/bin/env python
"""
Examples:
	dirPrefix=./AlignmentToCallPipeline_4HighCovVRC_isq_15_18_vs_524_top4Contigs_multi_sample_condor_20111106T1554/;

	%s -I $dirPrefix\gatk/ -i $dirPrefix\samtools/ -l condorpool -j condorpool
		-o FilterVCF_4HighCovVRC_isq_15_18_vs_524_top4Contigs_multi_sample_condor.xml  -z uclaOffice -u yh
	
	#2011-11-11
	dirPrefix=./AlignmentToCallPipeline_4HighCovVRC_isq_15_18_vs_524_top804Contigs_multi_sample_condor_20111106T1554/;
	
	%s -I $dirPrefix\gatk/ -i $dirPrefix\samtools/ -l condorpool -j condorpool -a 524
		-o FilterVCF_4HighCovVRC_isq_15_18_vs_524_top804Contigs_multi_sample_condor.xml -z uclaOffice -u yh
		#--alnStatForFilterFname alnStatForFilter.tsv
	
	#2011-11-11
	dirPrefix=./AlignmentToCallPipeline_4HighCovVRC_isq_15_18_vs_524_top804Contigs_multi_sample_condor_20111106T1554/;	
	%s  -I $dirPrefix\gatk/ -i $dirPrefix\samtools/ -l condorpool -j condorpool -a 524
		-o FilterVCF_4HighCovVRC_isq_15_18_vs_524_top804Contigs_minGQ30_multi_sample_condor.xml -z uclaOffice -u yh
		--minGQ 30
	
	#2011.11.28 (--onlyKeepBiAllelicSNP = keep only bi-allelic SNPs), --checkEmptyVCFByReading
	dirPrefix=./AlignmentToCallLowPass_top7559Contigs_no12eVarFilter_2011.11.23T1620/
	%s  -I $dirPrefix\gatk -i $dirPrefix\call/ -l condorpool -j condorpool
		-o FilterVCF_LowPass_top7559Contigs_no12eVarFilter_minGQ1_maxSNPMisMatch0.1_minMAC5_maxSNPMissing0.25.xml
		-z uclaOffice -u yh
		--minGQ 1 --onlyKeepBiAllelicSNP --maxSNPMismatchRate 0.1 --minMAC 5 --maxSNPMissingRate 0.25 -a 524 -C 50 --checkEmptyVCFByReading
	
	#2011.12.9 to remove SNPs that are not in a file. no other filters.
	dirPrefix=./AlignmentToCallLowPass_top7559Contigs_no12eVarFilter_2011.11.23T1620/
	%s -I $dirPrefix\gatk -i $dirPrefix\call/ -l condorpool -j condorpool
		-o Keep_LowPass_top7559Contigs_no12eVarFilter_SNPs_PresentIn4HC_inter_minMAC4.xml
		-z uclaOfficeTemp -u yh --minGQ 0 --maxSNPMismatchRate 1 --minMAC 0
		--maxSNPMissingRate 1 --depthFoldChange 100000 -a 524 -C 50
		--keepSNPPosFname ./4HighCovVRC_inter_minMAC4_vs_LowPass_top7559Contigs_no12eVarFilter_inter.2011.12.9T0107/overlapPos.tsv
	
	#2011.12.19 run on hoffman2's condorpool
	%s ....
		-l hcondor -j hcondor -e /u/home/eeskin/polyacti/
		-t /u/home/eeskin/polyacti/NetworkData/vervet/db/ -D /u/home/eeskin/polyacti/NetworkData/vervet/db/
		
	#2012.5.1 filter trioCaller output with total depth (no minGQ filter anymore), minMAC=10 (--minMAC 10),
	# maxSNPMismatchRate=1 (--maxSNPMissingRate 1.0)
	# minMAF=0.05 (--minMAF 0.05), no depth-band filter (--depthFoldChange 0)
	%s -I AlignmentToTrioCallPipeline_VRC_top7559Contigs.2011.12.15T0057/trioCaller/ -l condorpool -j condorpool
		-z uclaOffice -u yh --minMAC 10 --maxSNPMissingRate 1.0
		--minMAF 0.05 --depthFoldChange 0 -a 524 -C 50 --checkEmptyVCFByReading -H
		-o FilterVCF_trioCallerTop7559Contigs.xml
	
	#2012.8.1 FilterGenotypeMethod5_ByMethod7Sites (--keepSNPPosFname ...) NoDepthFilter (--depthFoldChange 0) MaxSNPMissing0.5 (--maxSNPMissingRate 0.5)
	%s -I ~/NetworkData/vervet/db/genotype_file/method_5/
		--maxSNPMissingRate 0.5 -a 524  --checkEmptyVCFByReading -H
		-o dags/FilterVariants/FilterGenotypeMethod5_ByMethod7Sites_NoDepthFilter_MaxSNPMissing0.5.xml
		-l hcondor -j hcondor -t ~/NetworkData/vervet/db/ -D ~/NetworkData/vervet/db/
		-u yh -C 5 --keepSNPPosFname ./method7_sites.tsv --depthFoldChange 0
	
	#2012.8.1 FilterGenotypeMethod6_ByMaskingZeroDPSite (--minDepth 1) 2FoldDepthFilter (--depthFoldChange 2) MaxSNPMissing1.0 (--maxSNPMissingRate 1.0)
	# "-V 90 -x 100" are used to restrict contig IDs between 90 and 100.
	# "--minNeighborDistance 5" to the minimum distance between neighboring SNPs, "--minMAF 0.1", minMAF=0.1
	%s -I ~/NetworkData/vervet/db/genotype_file/method_6/
		--maxSNPMissingRate 1.0 -a 524 --checkEmptyVCFByReading -H
		-o dags/FilterVariants/FilterGenotypeMethod6_MinDP1_2FoldDepthFilter_MaxSNPMissing1.0MinNeighborDistance5MinMAF0.1.xml
		-l hcondor -j hcondor
		-t ~/NetworkData/vervet/db/ -D ~/NetworkData/vervet/db/
		-u yh -C 5 --minDepth 1 --depthFoldChange 2 --minNeighborDistance 5 --minMAF 0.1
		#-V 90 -x 100 
		--excludeFilteredSites 2
		--siteTotalCoverateINFOFieldName DP
	
Description:
	2012.9.12 pipeline that runs VCF2plink, plink Mendel, then filter VCF by max mendel error on top of filters by depth, GQ, MAC, 
		SNP missing rate.
	
"""
import sys, os, math
__doc__ = __doc__%(sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0]\
				, sys.argv[0], sys.argv[0])

sys.path.insert(0, os.path.expanduser('~/lib/python'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import subprocess, cStringIO
from pymodule import ProcessOptions, getListOutOfStr, PassingData, yh_pegasus, GenomeDB, NextGenSeq
from Pegasus.DAX3 import *
from vervet.src import VervetDB, AbstractVervetWorkflow
#from pymodule.pegasus.AbstractVCFWorkflow import AbstractVCFWorkflow

class FilterVCFPipeline(AbstractVervetWorkflow):
	__doc__ = __doc__
	option_default_dict = AbstractVervetWorkflow.option_default_dict.copy()
	common_filter_option_dict = {
						("onlyKeepBiAllelicSNP", 0, int): [0, 'K', 0, 'toggle this to remove all SNPs with >=3 alleles?'],\
						('keepSNPPosFname', 0, ): ['', '', 1, 'a tab-delimited file with 1st two columns as chr and pos.\
		should have a header.\
		to filter out SNPs that are absent in this file.\
		this step will be applied before all other filter jobs.\
		extra columns are fine.'],\
						}
	option_default_dict.update(common_filter_option_dict)
	option_default_dict.pop(('inputDir', 0, ))
	option_default_dict.update({
						('minGQ', 1, int): [50, 'G', 1, 'minimum GQ/GenotypeQuality for one genotype. 2012.5.1 no longer enforced in FilterVCFByDepth.java', ],\
						('depthFoldChange', 0, float): [0, '', 1, 'a variant is retained if its depth within this fold change of meanDepth,\
		set this to 0 or below to eliminate this step of filtering.', ],\
						("maxSNPMismatchRate", 0, float): [0, '', 1, 'maximum SNP mismatch rate between two vcf calls'],\
						("minMAC", 0, int): [None, 'n', 1, 'minimum MinorAlleleCount (by chromosome)'],\
						("minMAF", 0, float): [None, 'f', 1, 'minimum MinorAlleleFrequency (by chromosome)'],\
						("maxSNPMissingRate", 0, float): [1.0, 'L', 1, 'maximum SNP missing rate in one vcf (denominator is #chromosomes)'],\
						('minNeighborDistance', 0, int): [None, 'g', 1, 'minimum distance between two adjacent SNPs'],\
						('excludeFilteredSites', 0, int): [0, '', 1, '0: no such filter, 1: remove sites whose FILTER!=PASS, 2: remove sites whose FILTER!=PASS and is not a SNP (indels+MNP)', ],\
						('vcf1Dir', 1, ): ['', 'I', 1, 'input folder that contains vcf or vcf.gz files', ],\
						('vcf2Dir', 0, ): ['', 'i', 1, 'input folder that contains vcf or vcf.gz files. If not provided, filter vcf1Dir without applying maxSNPMismatchRate filter.', ],\
						('siteTotalCoverateINFOFieldName', 1, ): ['TC', '', 1, 'used in the depthFoldChange filter step,  by GATK SelectVariants to parse the depth of entire site.\n\
		SAMtools, GATK output uses DP, Platypus output uses TC', ],\
						})
	#('alnStatForFilterFname', 0, ): ['', 'q', 1, 'The alignment stat file for FilterVCFByDepthJava. tab-delimited: individual_alignment.id minCoverage maxCoverage minGQ'],\
	#	2013.06.13 alnStatForFilterFname is no longer used. 
	#("minDepthPerGenotype", 0, int): [0, 'Z', 1, 'mask genotype with below this depth as ./. (other fields retained), \
	#	esp. necessary for SAMtools, which output homozygous reference if no read for one sample.'],\
	def __init__(self,  **keywords):
		"""
		"""
		AbstractVervetWorkflow.__init__(self, **keywords)
		# 2012.8.3 relative path causes stage-in problem as the pegasus program can't find the files.
		if getattr(self, 'vcf1Dir', None):
			self.vcf1Dir = os.path.abspath(self.vcf1Dir)
		if getattr(self, 'vcf2Dir', None):
			self.vcf2Dir = os.path.abspath(self.vcf2Dir)
		"""
		if getattr(self, 'depthFoldChange', None) and self.depthFoldChange>0 and not self.alnStatForFilterFname:
			sys.stderr.write("Error: alnStatForFilterFname (%s) is nothing while depthFoldChange=%s.\n"%\
							(self.alnStatForFilterFname, self.depthFoldChange))
			sys.exit(3)
		"""
		self.minDepthPerGenotype = self.minDepth
	
	def registerVCFAndItsTabixIndex(self, workflow, vcfF, input_site_handler='local'):
		"""
		2011-11-11
			vcfF.absPath is path to its physical path
			register both vcf and its tabix
		"""
		vcfF.addPFN(PFN("file://" + vcfF.absPath, input_site_handler))
		workflow.addFile(vcfF)
		vcfF.tbi_F = File("%s.tbi"%vcfF.name)
		vcfF.tbi_F.addPFN(PFN("file://" + "%s.tbi"%vcfF.absPath, input_site_handler))
		workflow.addFile(vcfF.tbi_F)
	
	def registerCustomExecutables(self, workflow=None):
		"""
		2011-11-28
		"""
		if workflow is None:
			workflow = self
		
		namespace = workflow.namespace
		version = workflow.version
		operatingSystem = workflow.operatingSystem
		architecture = workflow.architecture
		clusters_size = workflow.clusters_size
		site_handler = workflow.site_handler
		vervetSrcPath = self.vervetSrcPath
		
		#in order for two different input's FilterVCFByDepth to be merged into different-named clustered jobs
		FilterVCFByDepth2Java = Executable(namespace=namespace, name="FilterVCFByDepth2", version=version, os=operatingSystem,\
											arch=architecture, installed=True)
		FilterVCFByDepth2Java.addPFN(PFN("file://" + self.javaPath, site_handler))
		FilterVCFByDepth2Java.addProfile(Profile(Namespace.PEGASUS, key="clusters.size", value="%s"%clusters_size))
		workflow.addExecutable(FilterVCFByDepth2Java)
		workflow.FilterVCFByDepth2Java = FilterVCFByDepth2Java
		
		CalculateSNPMismatchRateOfTwoVCF = Executable(namespace=namespace, name="CalculateSNPMismatchRateOfTwoVCF", \
							version=version, os=operatingSystem, arch=architecture, installed=True)
		CalculateSNPMismatchRateOfTwoVCF.addPFN(PFN("file://" + os.path.join(vervetSrcPath, "mapper/CalculateSNPMismatchRateOfTwoVCF.py"), site_handler))
		CalculateSNPMismatchRateOfTwoVCF.addProfile(Profile(Namespace.PEGASUS, key="clusters.size", value="%s"%clusters_size))
		workflow.addExecutable(CalculateSNPMismatchRateOfTwoVCF)
		workflow.CalculateSNPMismatchRateOfTwoVCF = CalculateSNPMismatchRateOfTwoVCF
		
		#2013.05.20
		self.setOrChangeExecutableClusterSize(executable=self.SelectVariantsJava, clusterSizeMultipler=1.0, \
									defaultClustersSize=self.clusters_size)
	
	def addJobsToFilterTwoVCFDir(self, workflow=None, vcf1Dir=None, vcf2Dir=None, registerReferenceData=None, \
							alnStatForFilterF=None, keepSNPPosF=None, onlyKeepBiAllelicSNP=True,\
							minMAC=None, minMAF=None, maxSNPMissingRate=None, maxSNPMismatchRate=None):
		"""
		2013.04.08 added argument maxSNPMismatchRate
		2012.5.10
			add extraArguments="--recode-INFO-all" to addFilterJobByvcftools()
		2012.1.14
		"""
		if workflow is None:
			workflow = self
		refFastaFList = registerReferenceData.refFastaFList
		refFastaF = refFastaFList[0]
		
		#name to distinguish between vcf1Dir, and vcf2Dir
		vcf1Name = self.findProperVCFDirIdentifier(vcf1Dir, defaultName='vcf1')
		vcf2Name = self.findProperVCFDirIdentifier(vcf2Dir, defaultName='vcf2')
		if vcf2Name==vcf1Name or not vcf2Name:
			vcf2Name = "vcf2"
		
		vcf1DepthFilterDir = "%s_DepthFilter"%(vcf1Name)
		vcf1DepthFilterDirJob = self.addMkDirJob(outputDir=vcf1DepthFilterDir)
		vcf2DepthFilterDir = "%s_DepthFilter"%(vcf2Name)
		vcf2DepthFilterDirJob = self.addMkDirJob(outputDir=vcf2DepthFilterDir)
		
		SNPMismatchStatDir = "SNPMismatchStat"
		SNPMismatchStatDirJob = self.addMkDirJob(outputDir=SNPMismatchStatDir)
		
		vcf1_vcftoolsFilterDir = "%s_vcftoolsFilter"%(vcf1Name)
		vcf1_vcftoolsFilterDirJob = self.addMkDirJob(outputDir=vcf1_vcftoolsFilterDir)
		vcf2_vcftoolsFilterDir = "%s_vcftoolsFilter"%(vcf2Name)
		vcf2_vcftoolsFilterDirJob = self.addMkDirJob(outputDir=vcf2_vcftoolsFilterDir)
		
		#import re
		#chr_pattern = re.compile(r'(\w+\d+).*')
		input_site_handler = self.input_site_handler
		
		counter = 0
		for inputFname in os.listdir(vcf1Dir):
			vcf1AbsPath = os.path.join(os.path.abspath(vcf1Dir), inputFname)
			vcf2AbsPath = os.path.join(os.path.abspath(vcf2Dir), inputFname)
			if NextGenSeq.isFileNameVCF(inputFname, includeIndelVCF=False) and not NextGenSeq.isVCFFileEmpty(vcf1AbsPath):
				if not NextGenSeq.isVCFFileEmpty(vcf2AbsPath, checkContent=self.checkEmptyVCFByReading):	#make sure the samtools vcf exists
					#chr = chr_pattern.search(inputFname).group(1)
					commonPrefix = inputFname.split('.')[0]
					vcf1 = File(os.path.join(vcf1Name, inputFname))	#relative path
					vcf1.absPath = vcf1AbsPath
					self.registerVCFAndItsTabixIndex(workflow, vcf1, input_site_handler)
					vcf2 = File(os.path.join(vcf2Name, inputFname))	#relative path
					vcf2.absPath = vcf2AbsPath
					self.registerVCFAndItsTabixIndex(workflow, vcf2, input_site_handler)
					
					if keepSNPPosF:
						#toss SNPs that are not in this keepSNPPosFname file
						outputFnamePrefix = os.path.join(vcf1_vcftoolsFilterDir, '%s.keepGivenSNP'%(commonPrefix))
						vcf1KeepGivenSNPByvcftoolsJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
								inputVCFF=vcf1, \
								outputFnamePrefix=outputFnamePrefix, \
								parentJobLs=[vcf1_vcftoolsFilterDirJob], \
								snpMisMatchStatFile=keepSNPPosF, \
								minMAC=None, minMAF=None, \
								maxSNPMissingRate=None,\
								extraDependentInputLs=[vcf1.tbi_F], extraArguments="--recode-INFO-all")
						
						vcf1KeepGivenSNPByvcftoolsGzip = File("%s.gz"%vcf1KeepGivenSNPByvcftoolsJob.output.name)
						vcf1KeepGivenSNPByvcftoolsBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf1KeepGivenSNPByvcftoolsJob, inputF=vcf1KeepGivenSNPByvcftoolsJob.output, \
							outputF=vcf1KeepGivenSNPByvcftoolsGzip, \
							transferOutput=True)
					
						outputFnamePrefix = os.path.join(vcf2_vcftoolsFilterDir, '%s.keepGivenSNP'%(commonPrefix))
						vcf2KeepGivenSNPByvcftoolsJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
								inputVCFF=vcf2, \
								outputFnamePrefix=outputFnamePrefix, \
								parentJobLs=[vcf2_vcftoolsFilterDirJob],
								snpMisMatchStatFile=keepSNPPosF, \
								minMAC=None, minMAF=None, \
								maxSNPMissingRate=None,\
								extraDependentInputLs=[vcf2.tbi_F], extraArguments="--recode-INFO-all")
						vcf2KeepGivenSNPByvcftoolsGzip = File("%s.gz"%vcf2KeepGivenSNPByvcftoolsJob.output.name)
						vcf2KeepGivenSNPByvcftoolsBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf2KeepGivenSNPByvcftoolsJob, inputF=vcf2KeepGivenSNPByvcftoolsJob.output, \
							outputF=vcf2KeepGivenSNPByvcftoolsGzip, \
							transferOutput=True)
					
						vcf1filterByDepthInput=vcf1KeepGivenSNPByvcftoolsJob.output
						lastRoundJobLs=[vcf1DepthFilterDirJob, vcf1KeepGivenSNPByvcftoolsJob]
						lastRoundExtraDependentInputLs=[]
						vcf2filterByDepthInput=vcf2KeepGivenSNPByvcftoolsJob.output
						vcf2filterByDepthParentJobLs=[vcf2DepthFilterDirJob, vcf2KeepGivenSNPByvcftoolsJob]
						vcf2filterByDepthExtraDependentInputLs=[]
						counter += 4
						continue	#skip the rest
					else:
						vcf1filterByDepthInput=vcf1
						lastRoundJobLs=[vcf1DepthFilterDirJob]
						lastRoundExtraDependentInputLs=[vcf1.tbi_F]
						vcf2filterByDepthInput=vcf2
						vcf2filterByDepthParentJobLs=[vcf2DepthFilterDirJob]
						vcf2filterByDepthExtraDependentInputLs=[vcf2.tbi_F]
					vcf1AfterDepthFilter = File(os.path.join(vcf1DepthFilterDir, '%s.depthFiltered.vcf'%(commonPrefix)))
					vcf1FilterByDepthJob = self.addFilterVCFByDepthJob(workflow, FilterVCFByDepthJava=workflow.FilterVCFByDepthJava, \
							GenomeAnalysisTKJar=workflow.GenomeAnalysisTKJar, \
							refFastaFList=refFastaFList, inputVCFF=vcf1filterByDepthInput, outputVCFF=vcf1AfterDepthFilter, \
							parentJobLs=lastRoundJobLs, \
							alnStatForFilterF=alnStatForFilterF, \
							extraDependentInputLs=lastRoundExtraDependentInputLs, onlyKeepBiAllelicSNP=onlyKeepBiAllelicSNP)
					
					
					vcf1AfterDepthFilterGzip = File("%s.gz"%vcf1AfterDepthFilter.name)
					vcf1AfterDepthFilterGzip_tbi_F = File("%s.gz.tbi"%vcf1AfterDepthFilter.name)
					vcf1FilterByDepthBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf1FilterByDepthJob, inputF=vcf1AfterDepthFilter, outputF=vcf1AfterDepthFilterGzip, \
							transferOutput=False)
					
					vcf2AfterDepthFilter = File(os.path.join(vcf2DepthFilterDir, '%s.depthFiltered.vcf'%(commonPrefix)))
					vcf2FilterByDepthJob = self.addFilterVCFByDepthJob(workflow, FilterVCFByDepthJava=workflow.FilterVCFByDepth2Java, \
							GenomeAnalysisTKJar=workflow.GenomeAnalysisTKJar, \
							refFastaFList=refFastaFList, inputVCFF=vcf2filterByDepthInput, outputVCFF=vcf2AfterDepthFilter, \
							parentJobLs=vcf2filterByDepthParentJobLs, \
							alnStatForFilterF=alnStatForFilterF, \
							extraDependentInputLs=vcf2filterByDepthExtraDependentInputLs, onlyKeepBiAllelicSNP=onlyKeepBiAllelicSNP)
					
					vcf2AfterDepthFilterGzip = File("%s.gz"%vcf2AfterDepthFilter.name)
					vcf2AfterDepthFilterGzip_tbi_F = File("%s.gz.tbi"%vcf2AfterDepthFilter.name)
					vcf2FilterByDepthBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf2FilterByDepthJob, inputF=vcf2AfterDepthFilter, outputF=vcf2AfterDepthFilterGzip, \
							transferOutput=False)
					
					snpMisMatchStatFile = File(os.path.join(SNPMismatchStatDir, '%s_snpMismatchStat.tsv'%(os.path.splitext(commonPrefix)[0])))
					calculateSNPMismatchRateOfTwoVCFJob = self.addCalculateTwoVCFSNPMismatchRateJob(workflow, \
							executable=workflow.CalculateSNPMismatchRateOfTwoVCF, \
							vcf1=vcf1AfterDepthFilterGzip, vcf2=vcf2AfterDepthFilterGzip, snpMisMatchStatFile=snpMisMatchStatFile, \
							maxSNPMismatchRate=maxSNPMismatchRate, \
							parentJobLs=[vcf1FilterByDepthBGZipTabixJob, vcf2FilterByDepthBGZipTabixJob, SNPMismatchStatDirJob], \
							job_max_memory=1000, extraDependentInputLs=[], \
							transferOutput=False)
					
					
					outputFnamePrefix = os.path.join(vcf1_vcftoolsFilterDir, '%s.filter_by_vcftools'%(commonPrefix))
					vcf1FilterByvcftoolsJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
							inputVCFF=vcf1AfterDepthFilterGzip, \
							outputFnamePrefix=outputFnamePrefix, \
							parentJobLs=[vcf1FilterByDepthBGZipTabixJob, vcf1_vcftoolsFilterDirJob, calculateSNPMismatchRateOfTwoVCFJob], \
							snpMisMatchStatFile=snpMisMatchStatFile, \
							minMAC=minMAC, minMAF=minMAF, \
							maxSNPMissingRate=maxSNPMissingRate,\
							extraDependentInputLs=[vcf1FilterByDepthBGZipTabixJob.tbi_F], extraArguments="--recode-INFO-all")
					vcf1FilterByvcftoolsGzip = File("%s.gz"%vcf1FilterByvcftoolsJob.output.name)
					vcf1FilterByvcftoolsBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf1FilterByvcftoolsJob, inputF=vcf1FilterByvcftoolsJob.output, outputF=vcf1FilterByvcftoolsGzip, \
							transferOutput=True)
					
					outputFnamePrefix = os.path.join(vcf2_vcftoolsFilterDir, '%s.filter_by_vcftools'%(commonPrefix))
					vcf2FilterByvcftoolsJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
							inputVCFF=vcf2AfterDepthFilterGzip, \
							outputFnamePrefix=outputFnamePrefix, \
							parentJobLs=[vcf2FilterByDepthBGZipTabixJob, vcf2_vcftoolsFilterDirJob, calculateSNPMismatchRateOfTwoVCFJob],
							snpMisMatchStatFile=snpMisMatchStatFile, \
							minMAC=minMAC, minMAF=minMAF, \
							maxSNPMissingRate=maxSNPMissingRate,\
							extraDependentInputLs=[vcf2FilterByDepthBGZipTabixJob.tbi_F], extraArguments="--recode-INFO-all")
					
					vcf2FilterByvcftoolsGzip = File("%s.gz"%vcf2FilterByvcftoolsJob.output.name)
					vcf2FilterByvcftoolsBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
							parentJob=vcf2FilterByvcftoolsJob, inputF=vcf2FilterByvcftoolsJob.output, outputF=vcf2FilterByvcftoolsGzip, \
							transferOutput=True)
					
					counter += 9
		sys.stderr.write("%s jobs.\n"%(counter+1))
	
	def addJobsToFilterOneVCFDir(self, workflow=None, inputData=None, registerReferenceData=None, \
								cumulativeMedianDepth=None, depthFoldChange=None, keepSNPPosF=None, \
						onlyKeepBiAllelicSNP=True,\
						minDepthPerGenotype=False, minMAC=None, minMAF=None, maxSNPMissingRate=None, outputDirPrefix="",\
						minNeighborDistance=None, transferOutput=True, keepSNPPosParentJobLs=None, excludeFilteredSites=0):
		"""
		2013.05.20 add argument excludeFilteredSites, cumulativeMedianDepth, depthFoldChange
		2012.9.11 add argument keepSNPPosParentJobLs
		2012.9.6 add argument minNeighborDistance
		2012.7.30 add stat collecting jobs
		2012.5.10
			add extraArguments="--recode-INFO-all" to addFilterJobByvcftools()
		2012.1.14
		"""
		if workflow is None:
			workflow = self
		sys.stderr.write("Adding filter-VCF jobs for %s vcf files ... \n"%(len(inputData.jobDataLs)))
		refFastaFList = registerReferenceData.refFastaFList
		refFastaF = refFastaFList[0]
		no_of_jobs = 0
		
		filterPASSDir = "%sFILTER_PASS"%(outputDirPrefix)
		filterPASSDirJob = self.addMkDirJob(outputDir=filterPASSDir)
		
		vcf1DepthFilterDir = "%sDepthFilter"%(outputDirPrefix)
		vcf1DepthFilterDirJob = self.addMkDirJob(outputDir=vcf1DepthFilterDir)
		
		SNPMismatchStatDir = "%sSNPMismatchStat"%(outputDirPrefix)
		SNPMismatchStatDirJob = self.addMkDirJob(outputDir=SNPMismatchStatDir)
		
		filterDir = "%sVCFtoolsFilter"%(outputDirPrefix)
		filterDirJob = self.addMkDirJob(outputDir=filterDir)
		
		topOutputDir = "%sFilterStat"%(outputDirPrefix)
		topOutputDirJob = self.addMkDirJob(outputDir=topOutputDir)
		
		if keepSNPPosF:
			filterByGivenSitesStatMergeFile = File(os.path.join(topOutputDir, 'filterByGivenSitesStat_s1.tsv'))
			filterByGivenSitesStatMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterByGivenSitesStatMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")	#column 1 is the chromosome length, which are set to be all same.
								#column 2-4 are #sitesInInput1, #sitesInInput2, #overlapping
		if excludeFilteredSites:
			filterPassStatMergeFile = File(os.path.join(topOutputDir, 'filterByFILTER_PASS_s1.5.tsv'))
			filterPassStatMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterPassStatMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")	#column 1 is the chromosome length, which are set to be all same.
								#column 2-4 are #sitesInInput1, #sitesInInput2, #overlapping
		if minDepthPerGenotype:
			filterByMinDP1MergeFile = File(os.path.join(topOutputDir, 'filterByMinDP1_s2.tsv'))
			filterByMinDP1MergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterByMinDP1MergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")	#column 1 is the chromosome length, which are set to be all same.
								#column 2-4 are #sitesInInput1, #sitesInInput2, #overlapping
		if cumulativeMedianDepth and depthFoldChange:
			filterByDepthStatMergeFile = File(os.path.join(topOutputDir, 'filterByDepthStat_s3.tsv'))
			filterByDepthStatMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterByDepthStatMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")	#column 1 is the chromosome length, which are set to be all same.
								#column 2-4 are #sitesInInput1, #sitesInInput2, #overlapping
		
		
		if minMAC is not None:
			filterByMinMACMergeFile = File(os.path.join(topOutputDir, 'filterByMinMACStat_s4.tsv'))
			filterByMinMACMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterByMinMACMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")
		
		if minMAF is not None:
			filterByMinMAFMergeFile = File(os.path.join(topOutputDir, 'filterByMinMAFStat_s5.tsv'))
			filterByMinMAFMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
								outputF=filterByMinMAFMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
								extraArguments="-k 1 -v 2-4")
		if maxSNPMissingRate is not None and maxSNPMissingRate>=0 and maxSNPMissingRate<1:
			filterByMaxSNPMissingRateMergeFile = File(os.path.join(topOutputDir, 'filterByMaxSNPMissingRateStat_s6.tsv'))
			filterByMaxSNPMissingRateMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
							outputF=filterByMaxSNPMissingRateMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
							extraArguments="-k 1 -v 2-4")
		
		if minNeighborDistance is not None and minNeighborDistance>=0:
			filterByMinNeighborDistanceMergeFile = File(os.path.join(topOutputDir, 'filterByMinNeighborDistance_s7.tsv'))
			filterByMinNeighborDistanceMergeJob = self.addStatMergeJob(workflow, statMergeProgram=workflow.ReduceMatrixByChosenColumn, \
							outputF=filterByMinNeighborDistanceMergeFile, transferOutput=transferOutput, parentJobLs=[topOutputDirJob],\
							extraArguments="-k 1 -v 2-4")
		input_site_handler = self.input_site_handler
		
		returnData = PassingData()
		returnData.jobDataLs = []
		
		counter = 0
		no_of_vcf_files = 0
		for jobData in inputData.jobDataLs:
			inputF = jobData.vcfFile
			tbi_F = jobData.tbi_F
			inputJobLs = jobData.jobLs
			chromosome = self.getChrFromFname(os.path.basename(inputF.name))
			
			no_of_vcf_files += 1
			if no_of_vcf_files%100==0:
				sys.stderr.write("%s%s VCFs. "%('\x08'*40, no_of_vcf_files))
			commonPrefix = os.path.basename(inputF.name).split('.')[0]
			
			lastRoundJobLs= inputJobLs
			lastVCFJob = PassingData(output=inputF, tbi_F=tbi_F)	#2012.8.3 fake, not a job. only useful when all filtering jobs are skipped.
			lastRoundExtraDependentInputLs =[]
			
			noTransferFlagJobSet = set()
			
			if keepSNPPosF:
				#toss SNPs that are not in this keepSNPPosFname file
				outputFnamePrefix = os.path.join(filterDir, '%s.keepGivenSNP'%(commonPrefix))
				parentJobLs = [filterDirJob] + inputJobLs
				if keepSNPPosParentJobLs:
					parentJobLs += keepSNPPosParentJobLs
				vcf1KeepGivenSNPByvcftoolsJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
						inputVCFF=inputF, \
						outputFnamePrefix=outputFnamePrefix, \
						parentJobLs = parentJobLs, \
						snpMisMatchStatFile=keepSNPPosF, \
						minMAC=None, minMAF=None, \
						maxSNPMissingRate=None,\
						extraDependentInputLs=[tbi_F], extraArguments="--recode-INFO-all")
				
				vcf1KeepGivenSNPByvcftoolsGzip = File("%s.gz"%vcf1KeepGivenSNPByvcftoolsJob.output.name)
				vcf1KeepGivenSNPByvcftoolsBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
					parentJob=vcf1KeepGivenSNPByvcftoolsJob, inputF=vcf1KeepGivenSNPByvcftoolsJob.output, \
					outputF=vcf1KeepGivenSNPByvcftoolsGzip, \
					transferOutput=None)
				
				currentVCFJob = vcf1KeepGivenSNPByvcftoolsBGZipTabixJob
				#check how much sites got filtered
				outputF = File(os.path.join(topOutputDir, '%s.filterByGivenSitesStat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									vcf1=inputF, \
									currentVCFJob=currentVCFJob,\
									statMergeJob=filterByGivenSitesStatMergeJob, parentJobLs=[topOutputDirJob]+inputJobLs)
			
				lastVCFJob = currentVCFJob
				noTransferFlagJobSet.add(currentVCFJob)
				lastRoundJobLs=[vcf1DepthFilterDirJob, vcf1KeepGivenSNPByvcftoolsBGZipTabixJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
			else:
				lastRoundJobLs=[ vcf1DepthFilterDirJob] + inputJobLs
				lastRoundExtraDependentInputLs =[tbi_F]
				lastVCFJob = vcf1DepthFilterDirJob
				lastVCFJob.output = inputF	#faking it
			
			if excludeFilteredSites:
				#2013.05.20
				if excludeFilteredSites==1:
					selectExpression="vc.isNotFiltered()"
				else:
					selectExpression = "vc.isNotFiltered() && vc.isSNP()"
				vcfAfterFILTERPASS = File(os.path.join(filterPASSDirJob.output, '%s_filterByFILTERPASS.vcf'%(commonPrefix)))
				FILTER_PASS_Job = self.addSelectVariantsJob(SelectVariantsJava=self.SelectVariantsJava, \
										GenomeAnalysisTKJar=None, inputF=lastVCFJob.output, outputF=vcfAfterFILTERPASS, \
					refFastaFList=refFastaFList, sampleIDKeepFile=None, snpIDKeepFile=None, sampleIDExcludeFile=None, \
					interval=None,\
					parentJobLs=lastRoundJobLs, extraDependentInputLs=lastRoundExtraDependentInputLs, transferOutput=False, \
					extraArguments="""--select_expressions "%s" """%(selectExpression), job_max_memory=2000, walltime=None)
				#note how to escape  (let " be part of the commandline) 
				vcfGzipFile = File("%s.gz"%FILTER_PASS_Job.output.name)
				vcfGzipJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
					parentJob=FILTER_PASS_Job, inputF=FILTER_PASS_Job.output, \
					outputF=vcfGzipFile, \
					transferOutput=None)
				
				currentVCFJob = vcfGzipJob
				#check how much sites got filtered
				outputF = File(os.path.join(filterPASSDirJob.output, '%s_FILTER_PASS_Stat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									vcf1=lastVCFJob.output, \
									currentVCFJob=currentVCFJob,\
									statMergeJob=filterPassStatMergeJob, parentJobLs=lastRoundJobLs)
				
				lastVCFJob = currentVCFJob
				noTransferFlagJobSet.add(currentVCFJob)
				lastRoundJobLs=[filterPASSDirJob, vcfGzipJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
			
			#2012.8.1 mask zero-depth sites
			if minDepthPerGenotype:
				outputFnamePrefix = os.path.join(vcf1DepthFilterDir, '%s.minDP%s'%(commonPrefix, minDepthPerGenotype))
				maskZeroDepthGenotypeAsMissingJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
						inputVCFF=lastVCFJob.output, \
						outputFnamePrefix=outputFnamePrefix, \
						parentJobLs=lastRoundJobLs, \
						minMAC=None, minMAF=None, \
						maxSNPMissingRate=None,\
						extraDependentInputLs=lastRoundExtraDependentInputLs, outputFormat='--recode', \
						extraArguments="--recode-INFO-all --minDP %s"%(minDepthPerGenotype))
				
				maskVCFGzipFile = File("%s.gz"%maskZeroDepthGenotypeAsMissingJob.output.name)
				maskVCFGzipJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
					parentJob=maskZeroDepthGenotypeAsMissingJob, inputF=maskZeroDepthGenotypeAsMissingJob.output, \
					outputF=maskVCFGzipFile, \
					transferOutput=None)
				
				currentVCFJob = maskVCFGzipJob
				#check how much sites got filtered
				outputF = File(os.path.join(vcf1DepthFilterDir, '%s.filterByminDP1.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									vcf1=lastVCFJob.output, \
									currentVCFJob=currentVCFJob,\
									statMergeJob=filterByMinDP1MergeJob, parentJobLs=lastRoundJobLs)
			
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs=[currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				
			if cumulativeMedianDepth and depthFoldChange:
				vcf1AfterDepthFilter = File(os.path.join(vcf1DepthFilterDir, '%s.filterByDepth.vcf'%(commonPrefix)))
				#2013.05.20 TC stands for total coverage in platypus output
				selectExpression = "%s>=%s && %s<=%s"%(self.siteTotalCoverateINFOFieldName, \
											cumulativeMedianDepth/depthFoldChange, \
											self.siteTotalCoverateINFOFieldName, cumulativeMedianDepth*depthFoldChange)
				vcf1FilterByDepthJob = self.addSelectVariantsJob(SelectVariantsJava=self.SelectVariantsJava, \
										GenomeAnalysisTKJar=None, inputF=lastVCFJob.output, outputF=vcfAfterFILTERPASS, \
					refFastaFList=refFastaFList, sampleIDKeepFile=None, snpIDKeepFile=None, sampleIDExcludeFile=None, \
					interval=None,\
					parentJobLs=lastRoundJobLs, extraDependentInputLs=lastRoundExtraDependentInputLs, transferOutput=False, \
					extraArguments="""--select_expressions "%s" """%(selectExpression), job_max_memory=2000, walltime=None)
				"""
				vcf1FilterByDepthJob = self.addFilterVCFByDepthJob(workflow, FilterVCFByDepthJava=workflow.FilterVCFByDepthJava, \
						GenomeAnalysisTKJar=workflow.GenomeAnalysisTKJar, \
						refFastaFList=refFastaFList, inputVCFF=lastVCFJob.output, outputVCFF=vcf1AfterDepthFilter, \
						parentJobLs=lastRoundJobLs, \
						alnStatForFilterF=alnStatForFilterF, \
						extraDependentInputLs=lastRoundExtraDependentInputLs, onlyKeepBiAllelicSNP=onlyKeepBiAllelicSNP)
				"""
			
				vcf1AfterDepthFilterGzip = File("%s.gz"%vcf1AfterDepthFilter.name)
				vcf1AfterDepthFilterGzip_tbi_F = File("%s.gz.tbi"%vcf1AfterDepthFilter.name)
				vcf1FilterByDepthBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
						parentJob=vcf1FilterByDepthJob, inputF=vcf1FilterByDepthJob.output, outputF=vcf1AfterDepthFilterGzip, \
						transferOutput=None)
				currentVCFJob = vcf1FilterByDepthBGZipTabixJob
				#check how much sites got filtered by depth filter
				outputF = File(os.path.join(vcf1DepthFilterDir, '%s.filterByDepthStat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
										vcf1=lastVCFJob.output, parentJobLs=lastRoundJobLs, \
										currentVCFJob=currentVCFJob,\
										statMergeJob=filterByDepthStatMergeJob)
				
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs = [currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				
			
				
			if minMAC is not None:
				outputFnamePrefix = os.path.join(filterDir, '%s.filterByMinMAC'%(commonPrefix))
				vcf1FilterByMinMACJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
						inputVCFF=lastVCFJob.output, \
						outputFnamePrefix=outputFnamePrefix, \
						parentJobLs=[filterDirJob] + lastRoundJobLs, \
						snpMisMatchStatFile=None, \
						minMAC=minMAC, minMAF=None, \
						maxSNPMissingRate=None,\
						extraDependentInputLs=lastRoundExtraDependentInputLs, extraArguments="--recode-INFO-all")
				
				#check how much sites got filtered by maxSNPMissingRate filter
				
				vcf1FilterByMinMACGzip = File("%s.gz"%vcf1FilterByMinMACJob.output.name)
				vcf1FilterByMinMACBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
						parentJob=vcf1FilterByMinMACJob, inputF=vcf1FilterByMinMACJob.output, outputF=vcf1FilterByMinMACGzip, \
						transferOutput=None)
				currentVCFJob = vcf1FilterByMinMACBGZipTabixJob
				outputF = File(os.path.join(filterDir, '%s.filterByMinMACStat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									vcf1=lastVCFJob.output, currentVCFJob=currentVCFJob,\
									parentJobLs=lastRoundJobLs, statMergeJob=filterByMinMACMergeJob)
				
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs = [currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				no_of_jobs += 3
			
			if minMAF is not None:
				outputFnamePrefix = os.path.join(filterDir, '%s.filterByMinMAF'%(commonPrefix))
				vcf1FilterByMinMAFJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
						inputVCFF=lastVCFJob.output, \
						outputFnamePrefix=outputFnamePrefix, \
						parentJobLs=[filterDirJob] + lastRoundJobLs, \
						snpMisMatchStatFile=None, \
						minMAC=None, minMAF=minMAF, \
						maxSNPMissingRate=None,\
						extraDependentInputLs=lastRoundExtraDependentInputLs, extraArguments="--recode-INFO-all")
				
				#check how much sites got filtered by maxSNPMissingRate filter
				
				vcf1FilterByMinMAFGzip = File("%s.gz"%vcf1FilterByMinMAFJob.output.name)
				vcf1FilterByMinMAFBGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
						parentJob=vcf1FilterByMinMAFJob, inputF=vcf1FilterByMinMAFJob.output, outputF=vcf1FilterByMinMAFGzip, \
						transferOutput=None)
				
				currentVCFJob = vcf1FilterByMinMAFBGZipTabixJob
				outputF = File(os.path.join(filterDir, '%s.filterByMinMAFStat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									vcf1=lastVCFJob.output, currentVCFJob=currentVCFJob,\
									statMergeJob=filterByMinMAFMergeJob, parentJobLs=lastRoundJobLs)
				
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs = [currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				no_of_jobs += 3
			
			if maxSNPMissingRate is not None and maxSNPMissingRate>=0 and maxSNPMissingRate<1:
				outputFnamePrefix = os.path.join(filterDir, '%s.filterByMaxSNPMissingRate'%(commonPrefix))
				vcf1FilterByMaxSNPMissingRateJob = self.addFilterJobByvcftools(workflow, vcftoolsWrapper=workflow.vcftoolsWrapper, \
						inputVCFF=lastVCFJob.output, \
						outputFnamePrefix=outputFnamePrefix, \
						parentJobLs=[filterDirJob] + lastRoundJobLs, \
						snpMisMatchStatFile=None, \
						minMAC=None, minMAF=None, \
						maxSNPMissingRate=maxSNPMissingRate,\
						extraDependentInputLs=lastRoundExtraDependentInputLs, extraArguments="--recode-INFO-all")
				
				#check how much sites got filtered by maxSNPMissingRate filter
				
				vcf1FilterByMaxSNPMissingRateGzip = File("%s.gz"%vcf1FilterByMaxSNPMissingRateJob.output.name)
				vcf1FilterByMaxSNPMissingRateGZipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
						parentJob=vcf1FilterByMaxSNPMissingRateJob, inputF=vcf1FilterByMaxSNPMissingRateJob.output, outputF=vcf1FilterByMaxSNPMissingRateGzip, \
						transferOutput=None)
				currentVCFJob = vcf1FilterByMaxSNPMissingRateGZipTabixJob
				outputF = File(os.path.join(filterDir, '%s.filterByMaxSNPMissingRateStat.tsv'%(commonPrefix)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
										vcf1=lastVCFJob.output, currentVCFJob=currentVCFJob, \
										statMergeJob=filterByMaxSNPMissingRateMergeJob, parentJobLs=lastRoundJobLs)
				
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs = [currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				no_of_jobs += 3
			
			if minNeighborDistance is not None and minNeighborDistance>=0:
				outputFile = File(os.path.join(filterDir, '%s.filterByMinNeighborDistance%s.vcf'%(commonPrefix, minNeighborDistance)))
				filterByMinNeighborDistanceJob = self.addGenericJob(executable=self.FilterVCFSNPCluster, inputFile=lastVCFJob.output, \
					outputFile=outputFile, \
					parentJobLs=[filterDirJob] + lastRoundJobLs, extraDependentInputLs=lastRoundExtraDependentInputLs, \
					extraOutputLs=None,\
					transferOutput=False, \
					extraArgumentList=None, extraArguments="--minNeighborDistance %s"%(minNeighborDistance), \
					key2ObjectForJob=None, job_max_memory=2000)
				
				
				bgzipFile = File("%s.gz"%filterByMinNeighborDistanceJob.output.name)
				bgzipTabixJob = self.addBGZIP_tabix_Job(workflow, bgzip_tabix=workflow.bgzip_tabix, \
						parentJob=filterByMinNeighborDistanceJob, inputF=filterByMinNeighborDistanceJob.output, outputF=bgzipFile, \
						transferOutput=None)
				currentVCFJob = bgzipTabixJob
				#check how much sites got filtered by this filter
				outputF = File(os.path.join(filterDir, '%s.filterByMinNeighborDistanceJob%s.tsv'%(commonPrefix, minNeighborDistance)))
				self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
										vcf1=lastVCFJob.output, currentVCFJob=currentVCFJob, \
										statMergeJob=filterByMinNeighborDistanceMergeJob, parentJobLs=lastRoundJobLs)
				
				noTransferFlagJobSet.add(currentVCFJob)
				lastVCFJob = currentVCFJob
				lastRoundJobLs = [currentVCFJob]
				lastRoundExtraDependentInputLs=[currentVCFJob.tbi_F]
				no_of_jobs += 3
				
			
			lastBGZipTabixJobOutputFile = getattr(lastVCFJob, 'output', None)	#could be None if all filter jobs are skipped
			lastBGZipTabixJobTbiF = getattr(lastVCFJob, 'tbi_F', None)
			
			#2012.8.17 remove the lastVCFJob from noTransferFlagJobSet and set everyone's transfer flag to false
			noTransferFlagJobSet.remove(lastVCFJob)
			for job in noTransferFlagJobSet:
					self.setJobOutputFileTransferFlag(job=job, transferOutput=False, outputLs=None)
			#last job's transfer flag set to True
			self.setJobOutputFileTransferFlag(job=lastVCFJob, transferOutput=True, outputLs=None)
			
			returnData.jobDataLs.append(PassingData(jobLs=lastRoundJobLs, vcfFile=lastBGZipTabixJobOutputFile, \
									tbi_F=lastBGZipTabixJobTbiF, \
									fileLs=[lastBGZipTabixJobOutputFile, lastBGZipTabixJobTbiF]))
		
		sys.stderr.write("%s%s VCFs. "%('\x08'*40, no_of_vcf_files))
		sys.stderr.write("%s jobs.\n"%(self.no_of_jobs))
		return returnData
	
	def addVCFBeforeAfterFilterStatJob(self, executable=None, chromosome=None, outputF=None, vcf1=None, vcf2=None,\
									lastVCFJob=None, currentVCFJob=None,\
									statMergeJob=None, parentJobLs=None):
		"""
		2013.06.11 renamed old arguments to lastVCFJob, currentVCFJob
		2012.7.30
			examples:
			
			self.addVCFBeforeAfterFilterStatJob(chromosome=chromosome, outputF=outputF, \
									currentVCFJob=currentVCFJob, lastVCFJob=lastVCFJob,\
									statMergeJob=filterByMaxSNPMissingRateMergeJob)
		"""
		if vcf1 is None and lastVCFJob:
			vcf1 = lastVCFJob.output
		if vcf2 is None and currentVCFJob:
			vcf2 = currentVCFJob.output
		if parentJobLs is None:
			parentJobLs = []
		if lastVCFJob:
			parentJobLs.append(lastVCFJob)
		if currentVCFJob:
			parentJobLs.append(currentVCFJob)
		if executable is None:
			executable = self.CheckTwoVCFOverlap
		vcfFilterStatJob = self.addCheckTwoVCFOverlapJob(executable=executable, \
					vcf1=vcf1, vcf2=vcf2, \
					chromosome=chromosome, chrLength=None, \
					outputF=outputF, parentJobLs=parentJobLs, \
					extraDependentInputLs=None, transferOutput=False, extraArguments=None, job_max_memory=1000, \
					perSampleMismatchFraction=False)
		self.addInputToStatMergeJob(statMergeJob=statMergeJob, \
							inputF=vcfFilterStatJob.output , \
							parentJobLs=[vcfFilterStatJob])
		return vcfFilterStatJob
			
	
	def setup_run(self):
		"""
		wrap all standard pre-run() related functions into this function.
		setting up for run(), called by run()
		
		2013.06.11 assign all returned data to self, rather than pdata (pdata has become self)
		2013.05.20 parse cumulativeMedianDepth from a sample VCF file.
		
		"""
		pdata = AbstractVervetWorkflow.setup_run(self)
		
		"""
		#without commenting out db_vervet connection code. schema "genome" wont' be default path.
		db_genome = GenomeDB.GenomeDatabase(drivername=self.drivername, username=self.db_user,
						password=self.db_passwd, hostname=self.hostname, database=self.dbname, schema="genome")
		db_genome.setup(create_tables=False)
		chr2size = db_genome.getTopNumberOfChomosomes(contigMaxRankBySize=80000, contigMinRankBySize=1, tax_id=60711, sequence_type_id=9)
		"""
		firstVCFFile = None
		inputData = None
		cumulativeMedianDepth = None
		if self.vcf1Dir and  not self.vcf2Dir:
			#a relative-path name for vcf1Dir
			vcf1Name = self.findProperVCFDirIdentifier(self.vcf1Dir, defaultName='vcf1')
			inputData = self.registerAllInputFiles(workflow=pdata.workflow, inputDir=self.vcf1Dir, \
										input_site_handler=self.input_site_handler, \
										checkEmptyVCFByReading=self.checkEmptyVCFByReading,\
										pegasusFolderName="%s_%s"%(self.pegasusFolderName, vcf1Name), \
										maxContigID=self.maxContigID, \
										minContigID=self.minContigID)
			if inputData.jobDataLs:
				firstVCFFile = inputData.jobDataLs[0].file
		sys.stderr.write("One sample VCF file is %s (used to get alignments).\n"%(firstVCFFile))
		if self.depthFoldChange and self.depthFoldChange>0 and firstVCFFile:
			alignmentLs = self.db.getAlignmentsFromVCFFile(inputFname=yh_pegasus.getAbsPathOutOfFile(firstVCFFile))
			cumulativeMedianDepth = self.db.getCumulativeAlignmentMedianDepth(alignmentLs=alignmentLs, \
										defaultSampleAlignmentDepth=8)
			"""
			self.outputAlignmentDepthAndOthersForFilter(db_vervet=db_vervet, outputFname=self.alnStatForFilterFname, \
												ref_ind_seq_id=self.ref_ind_seq_id, \
												foldChange=self.depthFoldChange, minGQ=self.minGQ)
			#alnStatForFilterF = self.registerOneInputFile(inputFname=os.path.abspath(self.alnStatForFilterFname))
		#else:
			#alnStatForFilterF = None
			"""
		
		if self.keepSNPPosFname:
			keepSNPPosF = self.registerOneInputFile(inputFname=os.path.abspath(self.keepSNPPosFname),\
														folderName=self.pegasusFolderName)
		else:
			keepSNPPosF = None
		self.inputData = inputData
		self.keepSNPPosF = keepSNPPosF
		self.cumulativeMedianDepth = cumulativeMedianDepth
		sys.stderr.write("cumulativeMedianDepth for all samples is %s.\n"%(cumulativeMedianDepth))
		return self
	
	def run(self):
		"""
		"""
		
		pdata = self.setup_run()
		
		
		if self.vcf1Dir and self.vcf2Dir:
			self.addJobsToFilterTwoVCFDir(vcf1Dir=self.vcf1Dir, vcf2Dir=self.vcf2Dir, \
							registerReferenceData=pdata.registerReferenceData, \
							keepSNPPosF=pdata.keepSNPPosF, \
							onlyKeepBiAllelicSNP=self.onlyKeepBiAllelicSNP, minMAC=self.minMAC, minMAF=self.minMAF, \
							maxSNPMissingRate=self.maxSNPMissingRate, maxSNPMismatchRate=self.maxSNPMismatchRate)
		elif self.vcf1Dir:
			# 2012.5.1 filter only on the 1st vcf folder
			
			self.addJobsToFilterOneVCFDir(inputData=pdata.inputData, registerReferenceData=pdata.registerReferenceData, \
									cumulativeMedianDepth=pdata.cumulativeMedianDepth, depthFoldChange=self.depthFoldChange, \
									keepSNPPosF=pdata.keepSNPPosF, \
									onlyKeepBiAllelicSNP=self.onlyKeepBiAllelicSNP,\
									minMAC=self.minMAC, minMAF=self.minMAF, maxSNPMissingRate=self.maxSNPMissingRate,\
									minDepthPerGenotype=self.minDepthPerGenotype, outputDirPrefix="",\
									minNeighborDistance=self.minNeighborDistance, keepSNPPosParentJobLs=None,\
									excludeFilteredSites=self.excludeFilteredSites)
		self.end_run()
		


	
if __name__ == '__main__':
	main_class = FilterVCFPipeline
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	instance = main_class(**po.long_option2value)
	instance.run()
