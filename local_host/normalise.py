import csv
import os

def seprating_lines(list_dict, column_key):
    not_normal_list = []
    first_item = []
    for i in list_dict:
        s = i[column_key]
        dictionary = {}
        item = s.split(',')    
        for k in item:
            first_item.append(k)
            dictionary["date"] = i["date"]
            dictionary["location"] = i["location"]
            dictionary["items"] = k
            dictionary["payment_type"] = i["payment_type"]
            dictionary["cost"] = i["cost"]
            not_normal_list.append(dictionary)
            dictionary = {}
    return not_normal_list, first_item


def finding_unique_value(list_list):
    items = []
    for w in list_list:
        if w not in items:
            items.append(w)
    return items

def adding_id(entry_list):
    id_items = []            
    for i in range(len(entry_list)):
        id_items.append(i+1)    
    for x, y in zip(entry_list, id_items):
        # x.append(y)
        print(x)
    return entry_list

def creating_list_with_item_id(not_normal_list, items_list):
    for key in not_normal_list:
        for i in items_list:
            list_difference = []
            for j in key["items"]:
                if j not in i:
                    list_difference.append(j)
            if len(list_difference) <= 1:
                key["items"] = i[3]
                break
    return not_normal_list

def adding_regular(item_list):
    s = []
    for i in item_list:
        m = i.split('-')
        s.append(m)
    for j in s:
        string1 = j[0]
        string = string1[0:4]
        if string == " Lar" or string == "Larg" or string == " Reg"or string == "Regu":
            continue
        else:
            string2 = "Regular" + string1
            j[0] = string2   
    return s

def adding_null(item_list):
    for i in item_list:
        if len(i) < 3:
            s = i[1]
            i[1] = "Null"
            i.append(s)
    return item_list

def deleting_extra_space(item_list):
    for i in item_list:
        x = i[0].lstrip()   #delete spaces which is before regular or large
        y = re.sub(' +', ' ', x)   #replace two spaces with one space
        i[0] = y
    return item_list

def finding_unique_location(list_dict):
    new_list = []
    for i in list_dict:
        for k, v in i.items():
            if k == "location":
                if v not in new_list:
                    new_list.append(v)
    return new_list