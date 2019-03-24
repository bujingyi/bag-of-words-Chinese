#!/user/bin/env python
#encoding: utf-8

import os
import re
import jieba
import numpy as np
import pickle as pk
from scipy import sparse


class BagOfWords:
	def __init__(
		self,
		dir,
		process_line_fn=default_process_line_fn,
		reduce_dict_fn=default_reduce_dict_fn,
		format='csv',
		encoding='utf-8'
		mode='normal'
		):
		"""
		Bag of words model for Chinese
		:param process_line_fn: function, passed in to process each line
		"""
		self.dir = dir  # specify the location of the training files
		self.process_line_fn = process_line_fn  # function processing each line
		self.format = format  # file format, txt, csv, etc.
		self.encoding = encoding  # indicates file encoding
		self.mode = mode  # 'debug' or 'normal'

		self.dict = None  # word dictionary

	def build_dictionary(self):
		"""
		Build the dictionary for bag of words model
		"""
		dict_set = set()  # word set
		record_count = 0  # total number of records for training
		for (dirname, _, files) in os.walk(self.dir):
			# walk through all txt files
			for file in files:
				if file.endswith('.' + self.format):
					filename = os.path.join(dirname, file)
					# open files with specified encoding
					with open(filename, 'r', encoding=self.encoding, errors='ignore') as f:
						# process each line in the file
						for line in f:
							record_count += 1
							line = self.process_line_fn(line)
							# skip the line if no Chinese character is contained
							if (line is None) or (len(line) == 0):
								continue
							# split Chinese sentences into words with jieba
							words = jieba.cut(line.strip(), cut_all=False)
							dict_set |= set(words)
							if record_count % 2000 == 0:  # verbose
								print('\r{} records processed'.format(record_count), end='')
		Print('\r{} records processed'.format(record_count), end='\n')
		self.num_samples = record_count
		# remove the one-character words
		self.dict = self.reduce_dict_fn(dict_set)

	def save_dictionary(self, dir):
		"""
		Save the dictionary in pickle file
		"""
		# check if word dictionary exists
		if self.dict is None:
			raise IOError('no dictionary when saving it into pickle')
		pk.dump(self.dict, open(dir, 'wb'))
		print('saved dictionary to {}'.format(dir))

	def load_dictionary(self, dir):
		"""
		Load word dictionary from pickle file
		"""
		# TODO: check the esistence of dictionary pickle file
		try:
			print('loading dictionary from {}'.format(dir))
			self.dict = pk.load(open(dir, 'rb'))
			print('loading dictionary done')
		except IOError:
			print('error while loading from {}'.format(dir))

	def transform_data(self, dir):
		"""
		Transform free texts into bag of wards vectors
		:return: features (word vectors in sparse matrix), labels (labels in np.array)
		"""
		print('transforming free texts into bag of words vectors')
		features = []
		labels = []
		count = 0
		for (dirname, _, files) in os.walk(dir):
			for file in files:
				if file.endswith('.' + self.format):
					count += 1
					filename = os.path.join(dirname, file)
					tags = re.split('[/\\\\]', dirname)
					tag = tags[-1]  # the last dirname is the label
					word_vector = np.zeros(len(self.dict))
					with open(filename, 'r', encoding=self.encoding, errors='ignore') as f:
						for line in f:
							line = self.process_line_fn(line)
							if (line is None) or (len(line) == 0):
								continue  # skip the line if no Chinese character is contained
							words = jieba.cut(line.strip(), cut_all=False)
							for word in words:
								try:
									word_vector[self.dict[word]] += 1
								except KeyError:
									pass
							features.append(word_vector)
							labels.append(tag)
							# print information for debug
							if self.mode == 'debug':
								print(lin(line), line)
								print(word_vector, tag)
		self.num_samples = count
		print('trasforming done')
		return sparse.csr_matrix(np.asarray(features)), np.asarray(labels)


# default passed in functions
def default_process_line_fn(line):
	"""
	Default process line function
	:param line: str
	:return: str
	"""
	# check the input
	if line =='':
		return None
	# rule1 to remove all strange symbols, \u4e00-\u9fa5 are the unicodes for all Chinese characters
	rule1 = re.compile(u'[^\u4e00-\u9fa5^.^a-z^A-Z^0-9^,^:^，^。]')
	line = rule1.sub('', line)
	# rule2 to locate and match everything before the first Chinese character
	rule2 = re.compile(u'[^\u4e00-\u9fa5]*')
	# if no Chinese is contained in this line then return None
	prefix = rule2.search(line)
	if prefix is None:
		return None
	# rule3 to remove everything before the first Chinese character
	rule3 = re.compile(str(prefix.group()))
	line = rule3.sub('', line)
	return line

def default_reduce_dict_fn(dict_set):
	"""
	Default reduce dictionary function:
	Remove the one-character words
	:param dict_set: set, word set for bag of words model
	:return: dict, {'word': index}
	"""
	dict_set_copy = dict_set.copy()
	for word in dict_set:
		# remove one-character words
		if len(word) < 2:
			dict_set_copy.remove(word)
		# remove numerical words
		else:
			try:
				float(word)
				dict_set_copy.remove(word)
			except ValueError:
				continue
	dictioinary = {}
	# build word dictionary
	for idx, word in enumerate(dic_copy):
		dictionary[word] = idx
	return dictionary
