import sqlite3

conn = sqlite3.connect('DunGram.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS Items (
    ItemId INTEGER PRIMARY KEY,
    ItemName TEXT,
    ItemData TEXT
);
'''
)

def create_new_item(item_name, item_description):
    conn = sqlite3.connect('DunGram.db')
    c = conn.cursor()
    c.execute('INSERT INTO Items (ItemName, ItemData) VALUES (?, ?)', (item_name, item_description))
    conn.commit()
    conn.close()

def add_item_to_inventory(user_id, item_id, count):
    c.execute('SELECT ItemCount FROM InventorySlots WHERE UserId=? AND ItemId=?', (user_id, item_id))
    row = c.fetchone()
    if row:
        new_count = int(row[0]) + int(count)  # Добавляем к текущему количеству
        c.execute('UPDATE InventorySlots SET ItemCount=? WHERE UserId=? AND ItemId=?', (new_count, user_id, item_id))
    else:
        c.execute('INSERT INTO InventorySlots (UserId, ItemId, ItemCount) VALUES (?, ?, ?)', (user_id, item_id, count))
    conn.commit()

move = input('Move?')
if move:
    while True:
        choice = input('Creating?\n')
        if choice:
            item_name = input('Enter item name: ')
            item_description = input('Enter item data: ')
            create_new_item(item_name, item_description)
            print('Item created')
        else:
            break
else:
    while True:
        choice = input('Adding?\n')
        if choice:
            user_id = input('Enter user id: ')
            item_id = input('Enter item id: ')
            count = input('Enter count: ')
            add_item_to_inventory(user_id, item_id, count)
            print('Item added')
        else:
            break
        


conn.close()