
TASK_STATUSES = [
    {
        "text": "Инициализировано",
        "value": "INITIALIZED",
        "toStates": ["PLAN_CREATED", "APPROVED", "DONE"],
    },
    {
        "text": "Создан план",
        "value": "PLAN_CREATED",
        "toStates": ["INITIALIZED", "APPROVED", "DONE"],
    },
    {
        "text": "Согласовано ТЗ",
        "value": "APPROVED",
        "toStates": ["INITIALIZED", "PLAN_CREATED", "DONE"],
    },
    {
        "text": "Работы выполнены",
        "value": "DONE",
        "toStates": ["INITIALIZED", "PLAN_CREATED", "APPROVED"],
    },
]

# вместо старого кортежа STATUSES
def GetStatusValues(): #возвращает ["INITIALIZED","PLAN_CREATED", "APPROVED", "DONE"]
    values = []
    for status in TASK_STATUSES: # берём один словарь, вытаскиваем из него value и добавляем в пустой список
        values.append(status["value"])
    return values

def GetStatusByValue(value): # возвращает полное описание(словарь) статуса по его value 
    for status in TASK_STATUSES:
        if status["value"] == value:
            return status #возвращает весь словарь если INITIALIZED == INITIALIZED и тд
    return None

def CanChangeStatus(current_status, new_status): #булевое
    if current_status == new_status: #при отправл одного и того же статуса ничего не меняю, отправляю 200 ОК
        return True
    status = GetStatusByValue(current_status)
    if not status: return False # на случай если в БД битый статус (но хз как такое возможно, я всё проверяю, что в БД кладу)
    return new_status in status["toStates"]
