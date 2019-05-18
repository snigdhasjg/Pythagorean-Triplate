import os


def retrieve_name(var):
    import inspect

    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]


def search_dir(path):
    files = os.listdir(path)
    for name in files:
        answer = input('\n{}\nIs this the file? (y/n)'.format(name))
        if answer.lower() == 'y':
            return name
    return None


def save_list(obj):
    import pickle
    from datetime import datetime

    now = datetime.now()
    date_time = now.strftime("%d:%m:%Y %H:%M:%S")
    file_name = retrieve_name(obj)
    with open("list/{} {}.txt".format(file_name, date_time), "wb") as fp:  # Pickling
        pickle.dump(obj, fp)


def load_list(dirname: str = '../logs'):
    import pickle

    filename = search_dir(dirname)
    if filename is None:
        raise FileNotFoundError
    fname = "{}/{}".format(dirname, filename)
    with open(fname, "rb") as fp:  # Unpickling
        obj = pickle.load(fp)
    if __name__ != '__main__':
        old = "{}/{}".format(dirname, filename)
        new = "{}/{}".format(dirname, filename).replace('logs', 'logs/graph_done')
        os.rename(old, new)
    return obj, filename


def save_halloffame(hof):
    with open('output_div_1-10.txt', 'a+') as file:
        file.write('{} {}\n'.format(hof[0], hof[0].fitness.values[0]))
