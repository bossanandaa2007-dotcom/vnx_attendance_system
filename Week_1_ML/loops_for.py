def PositiveNumbers ():
    numbers = [5,-2,10,-8,20]
    print("The Given Numbers are", numbers)
    for i in numbers:
     if (i>0):
        print("The Positive Numbers are",i)
    return Positives
PositiveNumbers()

# here when we to try to compare the list object directly to an Integer:
# it throws the exception error!
# we have to use the for loop condition 
# so that We can Take it as int from the list