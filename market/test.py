
food=[]
with open('market/static/files/53food.txt') as f:
        class_names = f.readlines()
        for items in class_names:
                food.append(items.split("\n")[0])
print(food)