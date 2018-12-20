def InteractiveIf(msg=None, no_func=None, divider=True):
    if msg is None:
        msg = "Do you want to execute the function?"
    if no_func is None:
        def temp_func():
            print("Ignored!")
        no_func = temp_func
    def mainDecorator(yes_func):
        def wrapper(*args, **kwargs):
            if divider:
                print('-'*20)
            flag = 'a'
            while flag not in ['y','n']:
                flag = input("{} (y/n)".format(msg))
                if flag == 'y':
                    yes_func(*args, **kwargs)
                elif flag=='n':
                    no_func(*args, **kwargs)
                else:
                    print("invalid input: {}".format(flag))
        return wrapper
    return mainDecorator

@InteractiveIf("Do you want to try out testFunc?")
def testFunc():
    print("executed testFunc!")

if __name__ == '__main__':
    testFunc()