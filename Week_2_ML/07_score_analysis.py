import numpy as np
#Creating 1D array
array_1d=np.array([78,85,62,90,55,88])
print("The Given 1D Array is:",array_1d)
#Score analysis operations
#find Average Score
avg_score=np.mean(array_1d)
print("Averga score:",avg_score)
#find Highest Score
highest_score=np.max(array_1d)
print("Highest Score:",highest_score)
#Students above average
above_avg_students=array_1d[array_1d>avg_score]
print("Students scoring above average:",above_avg_students)
#over
