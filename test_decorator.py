#!/usr/bin/env python3

def decorator(f):
    def new_func(x):
        print("Called, x=", x)
        return f(x)
    return new_func

@decorator
def first_func(x):
    print("In First Func, x=",x)
    return x+1


y = first_func(6)
print(y)
