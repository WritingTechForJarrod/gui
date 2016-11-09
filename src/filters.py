class Filter(object):
	def calculate_average(self, new_x, new_y):
		raise NotImplementedError

class MovingAverage(Filter):
	def __init__(self, window_size):
		self.data_x = []
		self.data_y = []
		self.window_size = window_size
		self.filtered_x = 0
		self.filtered_y = 0

	def shift_list(self, new_item, shift_list):
		if(len(shift_list) < self.window_size):
			shifted_list = [new_item] + shift_list
		else:
			shifted_list = [new_item] + shift_list[0:len(shift_list)-1]
		return shifted_list

	# Testbench
	def test(self):
		test_filter = MovingAverage(5)
		test_filter.calculate_average(1,1)
		# test 1
		assert(test_filter.filtered_x == 1.0)
		assert(test_filter.filtered_y == 1.0)
		print ("test_1 passed")

		# test 2
		test_filter.calculate_average(2,1)
		assert(test_filter.filtered_x == 1.5)
		assert(test_filter.filtered_y == 1.0)
		print ("test_2 passed")

		# test 3
		test_filter.calculate_average(3,2)
		assert(test_filter.filtered_x == 2.0)
		assert(test_filter.filtered_y == 4.0/3.0)
		print ("test_3 passed")

		# test 4
		test_filter.calculate_average(4,5)
		assert(test_filter.filtered_x == 2.5)
		assert(test_filter.filtered_y == 2.25)
		print ("test_4 passed")

		# test 5
		test_filter.calculate_average(6,7)
		assert(test_filter.filtered_x == 3.2)
		assert(test_filter.filtered_y == 3.2)
		print ("test_5 passed")

		# test 6
		test_filter.calculate_average(1,2)
		assert(test_filter.filtered_x == 3.2)
		assert(test_filter.filtered_y == 3.4)
		print ("test_6 passed")
		
		# test 7
		test_filter.calculate_average(3,1)
		assert(test_filter.filtered_x == 3.4)
		assert(test_filter.filtered_y == 3.4)
		print ("test_2 passed")
		print ("all tests passed")


	def calculate_average(self, new_x, new_y):
		average_x = 0.0
		average_y = 0.0
		self.data_x = self.shift_list(new_x, self.data_x)
		self.data_y = self.shift_list(new_y, self.data_y)
		average_x = float(sum(self.data_x)) / float(len(self.data_x))
		average_y = float(sum(self.data_y)) / float(len(self.data_y))

		self.filtered_x = average_x
		self.filtered_y = average_y
		
if __name__ == '__main__':
	test_filter = MovingAverage(5).test()
	 