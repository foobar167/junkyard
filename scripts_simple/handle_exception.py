# Be DRY (don't repeat yourself), use exception handler function for try-except
def handle_exception(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            print('[ERROR] {}'.format(error))
            exit(1)
    return inner

@handle_exception
def divide(x, y):
    return x/y

def show_result(x, y):
    print(f'{x} divided by {y} is {divide(x, y)}')

# It should work.
show_result(16, 2)

# Check the exception handler. Division by zero.
show_result(8, 0)
