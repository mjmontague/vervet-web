#!/usr/bin/env python
"""
Examples:
	%s 
	
	%s -n /tmp/replicateIndividualOccurrence.tsv
		-i AlignmentToTrioCallPipeline_VRC_Aln559_600_Trio620_632_648_top2Contigs.2011.12.14T1432/preTrioCaller/Contig0.vcf.gz -o /tmp/Contig0.vcf
	

Description:
	2012.3.29

	
"""

import sys, os, math
__doc__ = __doc__%(sys.argv[0], sys.argv[0])

sys.path.insert(0, os.path.expanduser('~/lib/python'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import csv
from pymodule import ProcessOptions, getListOutOfStr, PassingData, utils, figureOutDelimiter, getColName2IndexFromHeader
from pymodule import VCFFile
from pymodule import AbstractVCFMapper

class ReplicateVCFGenotypeColumns(AbstractVCFMapper):
	__doc__ = __doc__
	option_default_dict = AbstractVCFMapper.option_default_dict.copy()
	option_default_dict.update({
					('replicateIndividualTag', 1, ): ['copy', 'T', 1, 'the tag that separates the true ID and its replicate count'],\
					('sampleID2FamilyCountFname', 1, ): ['', 'n', 1, 'a tab-delimited file that records how many families in which each individual occurs'],\
					
					})
	def __init__(self,  **keywords):
		"""
		"""
		AbstractVCFMapper.__init__(self, **keywords)
	
	def getSampleID2FamilyCount(self, inputFname):
		"""
		2012.3.29
		"""
		sys.stderr.write("Getting sampleID2FamilyCount from %s ..."%(inputFname))
		reader = csv.reader(open(inputFname, 'r'), delimiter=figureOutDelimiter(inputFname))
		header = reader.next()
		colName2Index = getColName2IndexFromHeader(header)
		sampleID2FamilyCount = {}
		for row in reader:
			individualID = row[colName2Index.get("individualID")]
			familyCount = int(row[colName2Index.get("familyCount")])
			sampleID2FamilyCount[individualID] = familyCount
		sys.stderr.write("%s individuals.\n"%(len(sampleID2FamilyCount)))
		return sampleID2FamilyCount
	
	
	def replicateVCFGenotypeColumns(self, inputFname, outputFname=None, replicateIndividualTag=None, sampleID2FamilyCount=None,\
								minDepth=0):
		"""
		2012.10.5 remove argument sampleStartingColumn
		2012.5.10
			VCFFile has been changed considerably and can act as a writer now.
		2012.3.29
			
		"""
		sys.stderr.write("Replicating some genotype columns in %s ...\n"%(inputFname))
		vcfFile = VCFFile(inputFname=inputFname, minDepth=minDepth)
		
		outVCFFile = VCFFile(outputFname=outputFname)
		outVCFFile.metaInfoLs = vcfFile.metaInfoLs
		
		"""
		outf = open(outputFname, 'w')
		writer = csv.writer(outf, delimiter='\t')
		#write all the headers up till the last line (which describes the samples and etc.)
		for metaInfo in vcfFile.metaInfoLs:
			outf.write(metaInfo)
		"""
		
		#modify the sample-id header line 
		sampleID2DataIndexLs = {}
		oldHeader = vcfFile.header
		oldHeaderLength = len(oldHeader)
		newHeader = oldHeader[:vcfFile.sampleStartingColumn]	#anything before the samples are same
		no_of_samples = 0
		for i in xrange(vcfFile.sampleStartingColumn, oldHeaderLength):
			#for sample_id in vcfFile.metaInfoLs[-1][vcfFile.sampleStartingColumn:]:
			sample_id = oldHeader[i].strip()
			newHeader.append('%s%s%s'%(sample_id, replicateIndividualTag, 1))	#1 because it's the 1st copy
			no_of_samples += 1
			sampleID2DataIndexLs[sample_id] = [i]	#1st copy for this sample
		
		#add additional column headers based on each one's occurrence
		extraColIndex2sampleID = {}
		for sample_id, familyCount in sampleID2FamilyCount.iteritems():
			for i in xrange(1, familyCount):
			#if familyCount>1:
				if sample_id in sampleID2DataIndexLs:
					no_of_samples += 1
					extraColIndex = len(newHeader)
					extraColIndex2sampleID[extraColIndex] = sample_id
					sampleID2DataIndexLs[sample_id].append(extraColIndex)
					replicate_order = len(sampleID2DataIndexLs[sample_id])
					newHeader.append("%s%s%s"%(sample_id, replicateIndividualTag, replicate_order))
		outVCFFile.header = newHeader
		outVCFFile.writeMetaAndHeader()
		
		newHeaderLength = len(newHeader)
		no_of_snps = 0
		for vcfRecord in vcfFile.parseIter():
			data_row =vcfRecord.row
			#2013.09.13 replace all "./." with full NA formating i.e. "./.:.:.:.", pending fields in the "format" column
			for i in xrange(vcfRecord.sampleStartingColumn, len(data_row)):
				if data_row[i]=='./.':	#2013.09.15 expand this NA genotype for TrioCaller
					field_value_ls = []
					for format_field in vcfRecord.format_column_ls:
						if format_field=='GT':
							field_value_ls.append('./.')
						elif format_field=='PL':	#for TrioCaller
							field_value_ls.append('.,.,.')
						else:
							field_value_ls.append('.')
					#field_value_ls = ['./.'] + ['.']*(len(vcfRecord.format_column_name2index)-1)
					data_row[i] = ':'.join(field_value_ls)
			for i in xrange(oldHeaderLength, newHeaderLength):	#add more genotype copies for those extra columns
				sample_id = extraColIndex2sampleID.get(i)
				sourceIndex = sampleID2DataIndexLs.get(sample_id)[0]
				data_row.append(data_row[sourceIndex])
			outVCFFile.writer.writerow(data_row)
			no_of_snps += 1
		outVCFFile.close()
		vcfFile.close()
		sys.stderr.write("%s samples X %s SNPs.\n"%(no_of_samples, no_of_snps))
	
	def run(self):
		"""
		2012.3.29
		"""
		if self.debug:
			import pdb
			pdb.set_trace()
		
		sampleID2FamilyCount = self.getSampleID2FamilyCount(self.sampleID2FamilyCountFname)
		
		self.replicateVCFGenotypeColumns(self.inputFname, self.outputFname, replicateIndividualTag=self.replicateIndividualTag, \
								sampleID2FamilyCount=sampleID2FamilyCount,\
								minDepth=self.minDepth)

if __name__ == '__main__':
	main_class = ReplicateVCFGenotypeColumns
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	instance = main_class(**po.long_option2value)
	instance.run()
