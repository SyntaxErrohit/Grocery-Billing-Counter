import pickle

price = {"soda": 40, "milk": 10, "chips": 10, "eggs": 50, "bread": 35, "oatmeal": 100, "candy": 5, "cookies": 20, "apple": 10, "banana": 10}

t = open("item_price.bin", "wb")
pickle.dump(price, t)
t.close()