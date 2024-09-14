from datetime import datetime

from ..database.mysql.MysqlArray import MYSQL


async def insert_statis(source, origin, sender, sender_group):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = """
        INSERT INTO statis (source, origin, sender, sender_group, time) 
        VALUES (%s, %s, %s, %s, %s)
        """
    await MYSQL.execute(sql, (source, origin, sender, sender_group, time))
    return
