import numpy

class Filter(object):
    def calculate_average(self,new_x,new_y):
        raise NotImplementedError

class ExponentialAverage(Filter):
    
    def __init__(self,window_size):
        self.data_x=[]
        self.data_y=[]
        self.window_size = window_size   ## window size
        self.filtered_x_list=[]
        self.filtered_y_list=[]
        self.filterd_x = 0.0
        self.filterd_y = 0.0
        self.data_list = [] 

    def moving_exp(self,values,window) :
        weights = numpy.exp(numpy.linspace(-1,0,window))
        weights /= weights.sum()
        return numpy.convolve(values,weights)[window-1:len(values)]
            
    def append_list(self,coor,data_list):
        self.data_list.append(coor);
        return data_list ;
    def calculate_average(self,new_x,new_y):
##        average_x = 0.0
##        average_y = 0.0
##        self.data_x = self.append_list(new_x,self.data_x)
##        self.data_y = self.append_list(new_y,self.data_y)
        self.data_x.append(new_x)
        self.data_y.append(new_y)
        
        self.filtered_x_list = self.moving_exp(self.data_x,self.window_size)
        self.filtered_y_list = self.moving_exp(self.data_y,self.window_size)
        if(len(self.filtered_x_list)==0 or len(self.filtered_y_list) == 0):
           self.filterd_x = 0
           self.filterd_y = 0
        else :
            self.filterd_x = self.filtered_x_list[-1]
            self.filterd_y = self.filtered_y_list[-1]

            
    def test(self):
        test_filter = ExponentialAverage(1)
        self.data_1 = 1
        self.data_2 = 1
        self.calculate_average(self.data_1,self.data_2)
        print(self.filterd_x)
                 
if __name__ == '__main__':
	test_filter = ExponentialAverage(1).test()
    












