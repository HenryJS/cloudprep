
def decorator(f):
    def new_func(x):
        print("Called, x=", x)
        f(x)
    return new_func

@decorator
def first_func(x):
    return x+1

first_func(6)