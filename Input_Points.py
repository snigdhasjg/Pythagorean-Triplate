def open_and_get_file_content(file_name):
    file = open(file_name, 'r')
    file_content = file.readlines()
    file.close()
    return file_content


def get_file_array(file_content):
    file_array = []
    for each_line in file_content:
        each_array = list(map(int, each_line.replace('\n', '').split()))
        file_array.append(each_array)
    return file_array


def divide_x_and_y(input_array):
    input_x = []
    input_y = []
    for each_array in input_array:
        tuple_x = (each_array[0], each_array[1])
        input_x.append(tuple_x)
        input_y.append(each_array[2])
    return input_x, input_y


def main():
    file_name = 'few_triple.txt'
    file_content = open_and_get_file_content(file_name)
    all_triple = get_file_array(file_content)
    return all_triple


if __name__ == '__main__':
    print(main())

