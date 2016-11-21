from __future__ import unicode_literals
from __future__ import print_function
import settings
import logging

class Node(dict):
	''' 
	A letter in the dict tree that has information about how often it occurs,
	links to next letters of words in the dict, and links to its parent for reverse
	traversal of the tree structure
	'''
	def __init__(self, parent=None, char=None):
		self.frequency = 1
		self.char = char
		self.parent = parent
		self.traversed = False # !!! this needs to be reset after repr called
	def __repr__(self):
		if self.parent is None:
			return '[root]'
		else:
			return '['+self.char+', '+str(self.frequency)+']'

class Predictionary(object):
	''' Predictive text object in the shape of a letter tree, built from a supplied .txt file '''
	def __init__(self, filename='../dict/sample_dict.txt'):
		logging.getLogger('predictionary').debug('Opening dict file '+filename)
		root = self.root = Node()
		head = self.head = self.root
		next_char_root = self.next_char_root = Node()
		break_chars = [' ',':',';',',','.','\'','"','?','-','_',
			'0','1','2','3','4','5','6','7','8','9','(',')']
		omit_chars = ['\n','\t','\r']
		self.completion_chars = [' ',',','.','?','!']
		with open(filename) as f:
			last_char = ' '
			for line in f:
				for char in line:
					try:
						char = unicode(char.lower())
					except:
						break
					if char not in omit_chars:
						# Calculate next most likely char
						try:
							last_letter_node = next_char_root[last_char]
						except KeyError:
							last_letter_node = next_char_root[last_char] = Node(next_char_root, last_char)
						try:
							last_letter_node[char].frequency += 1
						except KeyError:
							last_letter_node[char] = Node(last_char, char)
						last_char = char

						# Build dictionary tree
						if char in break_chars:
							head = self.root # Return to the top of the dictionary
							try:
								head[char].frequency += 1
							except KeyError:
								head[char] = Node(head, char)
						else:
							try:
								head[char].frequency += 1
							except KeyError:
								head[char] = Node(head, char)
							head = head[char] # Advance down the tree
					else:
						head = self.root
		self.all_symbols = self.get_children(self.root)

	def __repr__(self):
		''' 
		Return a string of all possible words in the dictionary
		NOTE this does not return words that are the first part of a longer word,
		e.g. if 'all' is in the dictionary 'a' is not output
		TODO mark end of all words
		'''
		str_out = '<PREDICTIONARY>\n'
		for first_letter in self.root.values():
			head = first_letter
			depth = 0
			while head.parent is not None:
				if head.traversed:
					head = head.parent
					depth -= 1
				elif len(head) == 0:
					str_out += self.get_word(head) + '\n'
					head.traversed = True
				else:
					head_advanced = False
					for head_candidate in head.values():
						if head_candidate.traversed is not True:
							head = head_candidate
							head_advanced = True
							depth += 1 
					if head_advanced is False:
						head.traversed = True
		return str_out

	def freqstrings(self):
		out = '<NEXT LETTER>'
		for letter_node in sorted(self.next_char_root.values(), key=lambda x: ord(x.char)):
			freq_list = ''
			for letter in sorted(letter_node.values(), key=lambda x: -x.frequency):
				freq_list += letter.char
			out += '\n'+'['+letter_node.char+']' + freq_list
		return out

	def get_word(self, node):
		out = node
		str_out = ''
		rev_word = []
		while(out.char is not None):
			rev_word.append(out)
			out = out.parent
		for letter in rev_word[::-1]:
			str_out += letter.char
		return str_out

	def get_children(self, at_node=None):
		if at_node is None: at_node = self.head
		one, twoplus = [x for x in at_node.values() if len(x) == 0], [x for x in at_node.values() if len(x) > 0]
		freq_sorted_one = sorted(one, key=lambda x: -x.frequency)
		freq_sorted_twoplus = sorted(twoplus, key=lambda x: -x.frequency)
		return ''.join([x.char for x in freq_sorted_twoplus]) + ''.join([x.char for x in freq_sorted_one])

	def process(self, in_char):
		''' Move down the dictionary tree if in_char is a valid choice. Else switch to frequency method '''
		if in_char is not None:
			try:
				self.head = self.head[in_char]
			except:
				print(in_char+' selection not available')
			word_found = None
			if len(self.head) == 0:
				print('self.head is of type ' + str(type(self.head)))
				word_found = self.get_word(self.head)
			if in_char in self.completion_chars:
				self.reset()
			return word_found
		else:
			print('None value passed to Predictionary.process()')
			return None

	def get_arrangement(self):
		''' Get a list of all the available chars in the dictionary '''
		arrangement = str(self.all_symbols)
		in_words = self.get_children() if self.get_children() is not None else ''
		for char in in_words:
			arrangement = arrangement.replace(char, '')
		return in_words + '.' + arrangement

	def reset(self):
		''' Resets the dictionary tree, back to choose a new first letter '''
		self.head = self.root

if __name__ == '__main__':
	''' Test build a Predictionary from a file, interact on the console std in '''
	import time
	start = time.clock()
	p = Predictionary(settings.dict_path+'test_dict.txt')
	end = time.clock()
	logging.basicConfig(level=logging.DEBUG)
	dictlog = logging.getLogger('predictionary')
	dictlog.debug(str(end-start)+' seconds to build dictionary')
	dictlog.debug(p.freqstrings())
	dictlog.debug(repr(p))
	alive = True
	while alive:
		word = p.process(raw_input())
		if word is not None: print('Word found: '+word)
		print(p.get_arrangement())