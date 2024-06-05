import sqlite3

# Создание соединения с базой данных
conn = sqlite3.connect('DunGram.db')
c = conn.cursor()

# Создание таблицы для хранения информации о врагах
c.execute(
'''CREATE TABLE IF NOT EXISTS SortieEnemies (
                EnemyId INTEGER PRIMARY KEY,
                EnemyName TEXT,
                EnemyDefData TEXT
)'''
)

# Пример данных о врагах
enemies_data = [
    (1, "Кадавр", '{"health": 10, "attack": 4, "DodgeChance": 10}'),
    (2, "Чешуйка", '{"health": 10, "attack": 3, "DodgeChance": 20}'),
    (3, "Зомби на Курице", '{"health": 15, "attack": 4, "DodgeChance": 10}'),
    (4, "Призыватель", '{"health": 20, "attack": 3, "DodgeChance": 0}')
]

# Добавление данных о врагах в таблицу
c.executemany('''INSERT INTO SortieEnemies (EnemyId, EnemyName, EnemyDefData)
                VALUES (?, ?, ?)''', enemies_data)

# Подтверждение изменений и закрытие соединения
conn.commit()
conn.close()