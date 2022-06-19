import pickle
import os
# print('here')
# dogs_dict = { 'Ozzy': 3, 'Filou': 8, 'Luna': 5, 'Skippy': 10, 'Barco': 12, 'Balou': 9, 'Laika': 16 }
filename = 'app/pickledgames/'
# outfile = open(filename,'wb')
# pickle.dump(dogs_dict,outfile)
# outfile.close()
# infile = open(filename,'rb')
# new_dict = pickle.load(infile)
# infile.close()
# print(new_dict)
# print(new_dict==dogs_dict)
# print(type(new_dict))
# path = 'C://Users//faisa//Desktop//Fefal//Projects//WA//app//pickledgames'

dir_list = os.listdir(filename)
print(dir_list)