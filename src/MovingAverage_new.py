import numpy

class Filter(object):
		def __init__(window_size):
				self.data_x = []
				self.data_y = []
				self.window_size = window_size
				self.filtered_x
				self.filtered_y

		def calculate_average(self, window_size):
				raise NotImplementedError

		def return_position(self):
				self.calculate_average(self, self.window_size)
				return (filtered_x,filtered_y)


class MovingAverage(Filter):
		def calculate_average(self, window_size):
   			window = numpy.ones(int(window_size))/float(window_size)
   			return numpy.convolve(values, window, 'valid')



			window = numpy.ones(int(window_size))/float(window_size)
	    return numpy.convolve(values, window, 'valid')

	  def moving_exp(values,window) :
	    weights = numpy.exp(numpy.linspace(-1,0,window))
	    weights /= weights.sum()
	    return numpy.convolve(values,weights)[window-1:len(values)]
		self.filtered_x = moving_exp(data_x,self.number_values)
		self.filtered_y = moving_exp(data_y,self.number_values)


		def movingaverage(values, window_size):
	 