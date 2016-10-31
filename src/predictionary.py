class Node(dict):
	def __init__(self, parent=None, letter=None):
		self.frequency = 1
		self.letter = letter
		self.parent = parent
		self.traversed = False # !!! this needs to be reset after repr called
	def __repr__(self):
		if self.parent is None:
			return '[root]'
		else:
			return '[' + self.letter + ', ' + str(self.frequency) + ']'

class Predictionary():
	def __init__(self, filename):
		root = self.root = Node()
		head = self.head = self.root
		break_chars = [' ',':',';',',','.','\'','"','?','-','_',
			'0','1','2','3','4','5','6','7','8','9','(',')']
		omit_chars = ['\n','\t']
		with open(filename) as f:
			for line in f:
				for letter in line:
					if letter not in omit_chars:
						if letter in break_chars:
							head = root
							try:
								head[letter].frequency += 1
							except KeyError:
								head[letter] = Node(head, letter)
						else:
							letter = letter.lower()
							try:
								head[letter].frequency += 1
							except KeyError:
								head[letter] = Node(head, letter)
							head = head[letter]

	def __repr__(self):
		str_out = '<PREDICTIONARY>\n'
		for first_letter in self.root.values():
			head = first_letter
			depth = 0
			while head.parent is not None:
				if head.traversed:
					head = head.parent
					depth -= 1
				elif len(head) == 0:
					str_out += get_word(head) + '\n'
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

	def get_word(self):
		out = self.head
		str_out = ''
		rev_word = []
		while(out.letter is not None):
			rev_word.append(out)
			out = out.parent
		for letter in rev_word[::-1]:
			str_out += letter.letter
		return str_out

	def get_children(self):
		one, twoplus = [x for x in self.head.values() if len(x) == 0], [x for x in self.head.values() if len(x) > 0]
		freq_sorted_one = sorted(one, key=lambda x: -x.frequency)
		freq_sorted_twoplus = sorted(twoplus, key=lambda x: -x.frequency)
		return ''.join([x.letter for x in freq_sorted_twoplus]) + ''.join([x.letter for x in freq_sorted_one])

	def process(self, in_str):
		try:
			self.head = self.head[in_str]
		except:
			print(in_str + ' selection not available')
		if len(self.head) == 0:
			return True

	def reset(self):
		self.head = self.root

if __name__ == '__main__':
	p = Predictionary('childrens_book.txt')
	all_symbols = p.get_children()
	print(all_symbols)
	alive = True
	while alive:
		if(p.process(raw_input())):
			print(p.get_word())
			p.reset()
		arrangement = str(all_symbols)
		for symbol in p.get_children():
			arrangement = arrangement.replace(symbol,'')
		print('[' + p.get_children() + ']' + arrangement)