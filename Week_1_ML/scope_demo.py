x=100
def scope():
    x=50
    print("Inside Function",x)
    return scope
scope()
print("Outside Function",x)
scope()

# Global variable = Decalred outside the functiom
# Local Variable = Declared inside the function
# We can decide which variable to be print by swapping last two lines