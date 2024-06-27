def add_income(cursor,userid,val,desc):
    cursor.execute(f'''
                    INSERT INTO HISTORY (id,val,description,cdate) VALUES ('{userid}',{val},'{desc}',date('now'))
    ''')
    l = ""
    if val > 0:
        l = "+"
    if val < 0:
        budget = get_budget(cursor,userid)
        if budget < (-val):
            return "ERR_BUDGET_TOO_LOW"
    cursor.execute(f'''
                    UPDATE USERS SET BALANCE=BALANCE{l}{val}
                   ''')
    return "SUCCESS"


def add_budget(cursor,userid):
    bd = get_budget(cursor,userid)
    if bd != 'ERR_USR_NOT_FOUND':
        return "EXISTS" 
    cursor.execute(f'''
                    INSERT INTO USERS(id,balance) VALUES ('{userid}',0)
                   ''')
    return "SUCCESS"
def get_budget(cursor,userid):
    cursor.execute(f'''
                    SELECT * FROM USERS  WHERE ID='{userid}'
    ''')
    users = cursor.fetchall()
    val = ''
    for i in users:
        val = i[1]
    if val == '':
        return "ERR_USR_NOT_FOUND"
    else:
        return val

def set_budget(cursor,userid,new_budget):
    cursor.execute(f'''
                    UPDATE USERS SET BALANCE={new_budget} WHERE ID={userid}
                   ''')

def get_report(cursor,userid):
    cursor.execute(f'''
        SELECT * FROM HISTORY WHERE ID='{userid}'
    ''')
    hist = cursor.fetchall()
    hist_form = 'Ваша история доходов и расходов:\n\n'
    est = False
    for i in hist:
        est = True
        val = i[1]
        description = i[2]
        date = i[3]
        emj = ''
        if val > 0:
            val = f'+{val}'
            emj = "• Доход"
        else:
            emj = "• Расход"
        hist_form += f'{emj}: {val} - {description} {date}\n\n'
    if est == False:
        return "У вас пока нет расходов и доходов"
    return hist_form
