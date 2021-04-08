'''transform data'''

def create_items_with_price(data):

    check_list = []
    items_list = []
    item_id = 0

    for item_list in data:
        for item in item_list:
            if isinstance(item, int):
                continue
            for string in item:
                string = string.strip()
                price = string[-4:]
                item = string[:-4]
                item = item.replace('-','')
                if item not in check_list:
                    check_list.append(item)
                    items_list.append({
                        'id':item_id,
                        'item': item.strip(),
                        'price':float(price)
                        })
                    item_id += 1
    return items_list