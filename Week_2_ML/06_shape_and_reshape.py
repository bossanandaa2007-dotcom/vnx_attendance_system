import numpy as np
#creating 1D array  
array_1d=np.array([1,2,3,4,5,6])
print("The Given 1D Array is:",array_1d)
#Reshaping 1D array to 2D array
print("Original Shape:",array_1d.shape) # To know original shape
array_1d_reshaped=array_1d.reshape(2,3) #reshaping to 2 rows and 3 columns
print("Reshaped 2D Array:\n",array_1d_reshaped)
print("New Shape:",array_1d_reshaped.shape) # To know new shape
