def reverseString():
    String=input("Enter the String:")
    print("The Given String is",String)
    reversed_text=""
    for char in String:
        reversed_text=char+reversed_text
    print("Reversed String:",reversed_text)
    return reversed_text
reverseString()

# 1, Get Input and display
# 2, reversed text assign
# 3, use for loop to access the strings!