from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, F
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.filters import Command, CommandStart
from database.database import Users as DB_Users, GlobalTasks as DB_GlobalTasks
from keyboards.reply import get_reply_keyboard_using_lexicon, get_reply_keyboard
from FSM.FSM import GlobalTasks as FSM_global_tasks
import time

router: Router = Router()


@router.message(StateFilter(None), CommandStart())
async def process_start_command(message: Message) -> None:
    db = DB_Users(user_id=message.from_user.id, user_name=message.from_user.username,
                  full_name=message.from_user.full_name)
    check = db.check_user()
    if not check:
        db.insert_new_user()
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=get_reply_keyboard_using_lexicon('global_tasks_button',
                                                                       'daily_tasks_button', width=2))


@router.message(StateFilter(None), Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'])


@router.message(StateFilter(None), F.text == LEXICON_RU['cancel_button'])
async def process_cancel_button_none_state(message: Message, state: FSMContext) -> None:
    await state.set_data({})
    await message.answer(text='Нечего отменять', reply_markup=get_reply_keyboard_using_lexicon(
        'global_tasks_button',
        'daily_tasks_button', width=2))


@router.message(F.text == LEXICON_RU['cancel_button'])
async def process_cancel_button(message: Message, state: FSMContext) -> None:
    await state.set_data({})
    await state.set_state(None)
    await message.answer(text='Действие отменено',
                         reply_markup=get_reply_keyboard_using_lexicon('global_tasks_button',
                                                                       'daily_tasks_button', width=2))


@router.message(StateFilter(None), F.text == LEXICON_RU['global_tasks_button'])
async def process_global_tasks(message: Message, state: FSMContext) -> None:
    db = DB_GlobalTasks(message.from_user.id)
    if db.get_all_active_tasks():
        await message.answer(text=(f'{LEXICON_RU['global_tasks']}' + f'{db.get_all_active_tasks()}'),
                             reply_markup=get_reply_keyboard_using_lexicon('add_task_button',
                                                                           'redact_button',
                                                                           'cancel_button', width=2))
    else:
        await message.answer(text='Активных задач нет.',
                             reply_markup=get_reply_keyboard_using_lexicon('add_task_button',
                                                                           'redact_button',
                                                                           'cancel_button', width=2))
    await state.set_state(FSM_global_tasks.view_tasks)


@router.message(StateFilter(None), F.text == LEXICON_RU['daily_tasks_button'])
async def process_global_tasks(message: Message, state: FSMContext) -> None:
    await message.answer(text=f'Данный функционал еще не реализован',
                         reply_markup=get_reply_keyboard_using_lexicon('global_tasks_button',
                                                                       'daily_tasks_button', width=2))


@router.message(StateFilter(FSM_global_tasks.view_tasks), F.text == LEXICON_RU['redact_button'])
async def redact_global_tasks(message: Message, state: FSMContext) -> None:
    db = DB_GlobalTasks(message.from_user.id)
    if db.get_ids_of_active_tasks():
        """await message.answer(text=f'Выберите id задачи, которую хотите отредактировать.',
                             reply_markup=get_reply_keyboard(db.get_ids_of_active_tasks(), width=4))"""
        await message.answer(text=f'Данный функционал еще не реализован',
                             reply_markup=get_reply_keyboard_using_lexicon('add_task_button',
                                                                           'redact_button', width=2)
                             )
        # await state.set_state(FSM_global_tasks.redact_task)
    else:
        await message.answer(text='Активных задач нет.',
                             reply_markup=get_reply_keyboard_using_lexicon('add_task_button',
                                                                           'redact_button', width=2))


@router.message(StateFilter(FSM_global_tasks.view_tasks), F.text == LEXICON_RU['add_task_button'])
async def add_global_task(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['add_task'], reply_markup=get_reply_keyboard(
        [LEXICON_RU['cancel_button']], width=2))
    await state.set_state(FSM_global_tasks.add_task)


@router.message(StateFilter(FSM_global_tasks.view_tasks))
async def no_such_command_view_tasks(message: Message) -> None:
    await message.answer(text=f'На данном этапе я понимаю только 3 команды: {LEXICON_RU['add_task_button']},'
                              f' {LEXICON_RU['redact_button']}, {LEXICON_RU['cancel_button']}')


@router.message(StateFilter(FSM_global_tasks.add_task), F.text)
async def catch_task_name(message: Message, state: FSMContext) -> None:
    # Этот хендлер ловит название задачи, просит ввести описание задачи и переводит FSM в следующее состояние
    await state.update_data(task=message.text)
    await message.answer(text=LEXICON_RU['add_description'],
                         reply_markup=get_reply_keyboard([LEXICON_RU['skip_button'],
                                                          LEXICON_RU['cancel_button']], width=2))
    await state.set_state(FSM_global_tasks.add_description)


@router.message(StateFilter(FSM_global_tasks.add_task))
async def no_such_command_in_add_task(message: Message) -> None:
    await message.answer(text='В качестве названия цели я принимаю только текстовый формат.')


@router.message(StateFilter(FSM_global_tasks.add_description), F.text == LEXICON_RU['skip_button'])
async def skip_description(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON_RU['add_deadline'], reply_markup=get_reply_keyboard(
        [LEXICON_RU['skip_button'], LEXICON_RU['cancel_button']], width=2))
    await state.update_data(description='NULL')
    await state.set_state(FSM_global_tasks.add_deadline)


@router.message(StateFilter(FSM_global_tasks.add_description), F.text)
async def add_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(text=LEXICON_RU['add_deadline'], reply_markup=get_reply_keyboard(
        [LEXICON_RU['skip_button'], LEXICON_RU['cancel_button']], width=2))
    await state.set_state(FSM_global_tasks.add_deadline)


@router.message(StateFilter(FSM_global_tasks.add_description))
async def no_such_command_add_description(message: Message) -> None:
    await message.answer(text='В качестве описания я принимаю только текстовый формат.')


@router.message(StateFilter(FSM_global_tasks.add_deadline), F.text == LEXICON_RU['skip_button'])
async def skip_deadline(message: Message, state: FSMContext) -> None:
    await state.update_data(deadline='NULL')
    data = await state.get_data()
    for key in data:
        if data[key] == 'NULL':
            data[key] = 'Не указано'
    await message.answer(text=f'Подтверди добавление задачи:\n'
                              f'<b>Название задачи:</b>\n'
                              f'{data['task']}\n'
                              f'<b>Описание:</b>\n'
                              f'{data['description']}\n'
                              f'<b>Крайний срок:</b>\n'
                              f'{data['deadline']}', reply_markup=get_reply_keyboard(
        [LEXICON_RU['confirm_button'], LEXICON_RU['cancel_button']], width=2))
    await state.set_state(FSM_global_tasks.confirm_add_task)


@router.message(StateFilter(FSM_global_tasks.add_deadline), F.text)
async def add_deadline(message: Message, state: FSMContext) -> None:
    date = str(message.text)
    try:
        valid_date = time.strptime(date, '%d.%m.%Y')
    except ValueError:
        date = False
    if date:
        await state.update_data(deadline=str(date))
        data = await state.get_data()
        await message.answer(text=f'Подтверди добавление задачи:\n'
                                  f'<b>Название задачи:</b>\n'
                                  f'{data['task']}\n'
                                  f'<b>Описание:</b>\n'
                                  f'{data['description']}\n'
                                  f'<b>Крайний срок:</b>\n'
                                  f'{data['deadline']}', reply_markup=get_reply_keyboard(
            [LEXICON_RU['confirm_button'], LEXICON_RU['cancel_button']], width=2))
        await state.set_state(FSM_global_tasks.confirm_add_task)

    else:
        await message.answer(text='Введи дату в формате ДД.ММ.ГГГГ')


@router.message(StateFilter(FSM_global_tasks.confirm_add_task), F.text == LEXICON_RU['confirm_button'])
async def process_confirm_button(message: Message, state: FSMContext) -> None:
    db = DB_GlobalTasks(message.from_user.id)
    data = await state.get_data()
    db.insert_task(task_name=data['task'], description=data['description'], deadline=data['deadline'])
    await message.answer(text=f'Задача успешно внесена в список!')
    await state.set_data({})
    await state.set_state(None)


@router.message(StateFilter(None))
async def process_other_answer(message: Message) -> None:
    await message.answer(text=LEXICON_RU['other_answer'])
