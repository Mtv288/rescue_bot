
# 🔹 Регистрация пользователя
from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    name = State()
    call_sign = State()
    birth_year = State()


# 🔹 Добавление материала (кнопка + ссылка)
class AddMaterial(StatesGroup):
    title = State()
    url = State()

# 🔹 Назначение ролей (админ/шеф)
class AssignRole(StatesGroup):
    user_id = State()
    role = State()

# 🔹 Назначение задачи группе
class AssignTask(StatesGroup):
    group = State()
    task = State()

# 🔹 Назначение новой группы
class AssignGroup(StatesGroup):
    group_name = State()
    leader_id = State()

# 🔹 Завершение задачи
class CompleteTask(StatesGroup):
    task_id = State()

# 🔹 Назначение СНМ / СПГ в группу
class AssignToGroup(StatesGroup):
    group_id = State()
    user_id = State()
    role = State()  # СНМ или СПГ

# 🔹 Назначение точки сбора
class SetMeetingPoint(StatesGroup):
    group_id = State()
    location = State()  # геолокация или текст

# 🔹 Добавление участника в поисковую группу
class JoinGroupRequest(StatesGroup):
    group_id = State()

# 🔹 Передача отчёта о задаче
class TaskReport(StatesGroup):
    task_id = State()
    report_text = State()

# 🔹 Добавление ссылки без названия (только URL)
class AddMaterial(StatesGroup):
    title = State()
    url = State()
    direct_url = State()