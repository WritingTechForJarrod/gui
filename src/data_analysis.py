import matplotlib.pyplot as plt 
f_1 = open ('original_data','r')
f_2 = open ('simple_mav','r')
f_3 = open ('exp_mav','r')

contents_1 = f_1.readline()
contents_2 = f_2.readline()
contents_3 = f_3.readline()

original = contents_1.split()
simple_avg = contents_2.split()
exp_avg = contents_3.split()

plt.plot(original[0],original[1],'ro',simple_avg[0],simple_avg[1],'bo',exp_avg[0],exp_avg[1],'go')
f_1.close()
f_2.close()
f_3.close()



