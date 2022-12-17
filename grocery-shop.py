import mysql.connector
import pickle
import os

db = mysql.connector.connect(
    host="localhost", user="root", passwd="mysql", database="project")
con = db.cursor()

print("############ Grocery shop counter ############")
print("Enter the choice by entering the number corresponding to it (eg 1-9)")


def inputAdv(message, opt=int):
    while True:
        inp = input(message)
        if opt == int:
            if inp.isdigit():
                return int(inp)
            else:
                print("Invalid input... Try again")
        elif opt == str:
            if inp.isalpha():
                return inp
            else:
                print("Invalid input... Try again")
        elif opt[0] == "check":
            if inp != opt[1] and inp != opt[2]:
                print("Invalid input... Try again")
            else:
                return inp


def addEntry(no):
    phone_no = inputAdv("Enter phone number: ")
    while len(str(phone_no)) != 10:
        print("Invalid phone number... Enter again")
        phone_no = inputAdv("Enter phone number: ")

    total_amount = 0
    while True:
        item = inputAdv("Enter item: ", opt=str)
        f = open("item_price.bin", "rb")
        prices = pickle.load(f)
        f.close()
        if item not in prices:
            print("Price of item is not available... Only the following is available:")
            for i in prices:
                print(i)
            print("Choose option 7 in main menu to add more items")
        else:
            qty = inputAdv("Enter quantity: ")
            amount = float(prices[item] * qty)
            total_amount += amount
            con.execute("insert into grocery(no, phone_no, item, quantity, amount) values({}, {}, '{}', {}, {})".format(
                no, phone_no, item, qty, amount))
            db.commit()

        choice = inputAdv("Do you want to add more (y/n): ",
                          opt=["check", "y", "n"])
        if choice == "n":
            break
    con.execute(
        "update grocery set total_amount = {} where no = {}".format(total_amount, no))
    db.commit()
    return phone_no


def displayEntry(no):
    print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+")
    print("| {:10} | {:8} | {:>10} |".format("Item", "Quantity", "Amount"))
    print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+")
    con.execute(
        "select item, quantity, amount from grocery where no={}".format(no))
    for i in con:
        print("| {:10} | {:>8} | {:>10} |".format(*i))
    print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+\n")


while True:
    print("\nMain menu:")
    print("1. Append entry")
    print("2. Modify entry")
    print("3. Delete entry")
    print("4. Search entry")
    print("5. Show report")
    print("6. Show items")
    print("7. Add more items")
    print("8. Delete items")
    print("9. Exit")
    ch = inputAdv("Enter your choice: ")

    # append entry
    if ch == 1:
        con.execute("select distinct no from grocery")
        temp = [i[0] for i in con.fetchall()]
        for i in range(1, len(temp)+1):
            if i not in temp:
                no = i
                break
        else:
            no = i+1 if temp != [] else 1

        phone_no = addEntry(no)
        print("Added successfully...")

        print("Bill:")
        print("Phone no:", phone_no)
        displayEntry(no)

    # modify entry
    elif ch == 2:
        no = inputAdv("Enter no to modify: ")
        con.execute(
            "select item, sum(quantity), sum(amount) from grocery where no = {} group by item;".format(no))
        result = con.fetchall()
        if len(result) == 0:
            print("No results found...")
        else:
            con.execute(
                "select distinct phone_no from grocery where no = {}".format(no))
            print("Phone no:", con.fetchall()[0][0])
            displayEntry(no)

            confirmation = inputAdv(
                "Do you want to continue modifying this record(y/n): ", opt=["check", "y", "n"])

            if confirmation == "y":
                con.execute("delete from grocery where no = {}".format(no))
                db.commit()
                addEntry(no)
                print("Entry modified successfully...")

            if confirmation == "n":
                print("Process cancelled...")

    # delete entry
    elif ch == 3:
        no = inputAdv("Enter no to delete: ")
        con.execute(
            "select item, sum(quantity), sum(amount) from grocery where no = {} group by item;".format(no))
        result = con.fetchall()
        if len(result) == 0:
            print("No results found...")
        else:
            con.execute(
                "select distinct phone_no from grocery where no = {}".format(no))
            print("Phone no:", con.fetchall()[0][0])
            displayEntry(no)

            confirmation = inputAdv(
                "Do you want to continue deleting this record(y/n): ", opt=["check", "y", "n"])

            if confirmation == "y":
                con.execute("delete from grocery where no = {}".format(no))
                db.commit()
                print("Entry deleted successfully...")

            if confirmation == "n":
                print("Process cancelled...")

    # search entry
    elif ch == 4:
        choice = inputAdv("Search by phone or no: ",
                          opt=["check", "phone", "no"])

        if choice == "phone":
            phone_no = inputAdv("Enter phone number to search: ")
            con.execute(
                "select item, sum(quantity), sum(amount) from grocery where phone_no = {} group by item;".format(phone_no))

        if choice == "no":
            no = inputAdv("Enter no to search: ".format(choice))
            con.execute(
                "select item, sum(quantity), sum(amount) from grocery where no = {} group by item;".format(no))

        total_amount = 0
        result = con.fetchall()
        if len(result) == 0:
            print("No results found...")
        else:
            print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+")
            print("| {:10} | {:8} | {:>10} |".format(
                "Item", "Quantity", "Amount"))
            print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+")
            for i in result:
                print("| {:10} | {:>8} | {:>10} |".format(*i))
                total_amount += i[2]
            print("+"+"-"*12+"+"+"-"*10+"+"+"-"*12+"+\n")
            print("Total amount:", total_amount)

    # show report
    elif ch == 5:
        con.execute(
            "select item, sum(quantity), sum(amount) from grocery group by item;")
        result = con.fetchall()
        total_amount = 0
        if len(result) == 0:
            print("No report found...")
        else:
            print("+"+"-"*12+"+"+"-"*15+"+"+"-"*13+"+")
            print("| {:10} | {:13} | {:11} |".format(
                "Items sold", "Quantity sold", "Amount sold"))
            print("+"+"-"*12+"+"+"-"*15+"+"+"-"*13+"+")
            for i in result:
                print("| {:10} | {:>13} | {:>11} |".format(*i))
                total_amount += i[2]
            print("+"+"-"*12+"+"+"-"*15+"+"+"-"*13+"+\n")
            print("Total amount sold:", total_amount)

    # show items
    elif ch == 6:
        f = open("item_price.bin", "rb")
        price = pickle.load(f)
        f.close()
        print("+"+"-"*20+"+"+"-"*10+"+")
        print("| {:18} | {:>8} |".format("Items", "Price"))
        print("+"+"-"*20+"+"+"-"*10+"+")
        for i in price:
            print("| {:18} | {:>8} |".format(i, price[i]))
        print("+"+"-"*20+"+"+"-"*10+"+")

    # add more items
    elif ch == 7:
        new_item = inputAdv("Enter item: ", opt=str)
        new_price = inputAdv("Enter price: ")
        f = open("item_price.bin", "rb")
        price = pickle.load(f)
        f.close()
        price[new_item] = new_price
        f = open("temp.bin", "wb")
        pickle.dump(price, f)
        f.close()
        os.remove("item_price.bin")
        os.rename("temp.bin", "item_price.bin")
        print("New item recorded...")

    # delete items
    elif ch == 8:
        item = inputAdv("Enter item to delete: ", opt=str)
        f = open("item_price.bin", "rb")
        price = pickle.load(f)
        f.close()
        v = price.pop(item, "NA")
        if v == "NA":
            print("Item doesn't exist")
        else:
            print("Item successfully deleted")
        f = open("temp.bin", "wb")
        pickle.dump(price, f)
        f.close()
        os.remove("item_price.bin")
        os.rename("temp.bin", "item_price.bin")

    # exit
    elif ch == 9:
        break

    # out of the choices
    else:
        print("Invalid choice. Enter again.")
