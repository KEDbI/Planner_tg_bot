from aiogram.fsm.state import State, StatesGroup


class GlobalTasks(StatesGroup):
    view_tasks: State = State()
    redact_task: State = State()
    add_task: State = State()
    add_description: State = State()
    add_deadline: State = State()
    confirm_add_task: State = State()


class DailyTasks(StatesGroup):
    view_tasks: State = State()
    redact_task: State = State()
    add_task: State = State()
    view_certain_date_tasks: State = State()
