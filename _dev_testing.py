import pickle

with open('script.bin', 'rb') as file:
    data = pickle.load(file)
    for dat in data:
        print(dat)