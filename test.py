from ledConvert import get_new_pixel_number

width = 14
height = 50

def convert_test1():
    assert get_new_pixel_number(42, width, height) == 46

def convert_test2():
    assert get_new_pixel_number(14, width, height) == 48

def convert_test3():
    assert get_new_pixel_number(412, width, height) == 320

def convert_test4():
    assert get_new_pixel_number(686, width, height) == 0

def convert_test5():
    assert get_new_pixel_number(687, width, height) == 99

def convert_test6():
    assert get_new_pixel_number(697, width, height) == 599

if __name__ == "__main__":
    convert_test1()
    convert_test2()
    convert_test3()
    print("Everything passed")