from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, F
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.filters import Command, CommandStart
from database.database import Users as DB_Users, GlobalTasks as DB_GlobalTasks
from keyboards.reply import get_start_keyboard
from FSM.FSM import GlobalTasks as FSM_global_tasks

router: Router = Router()


@router.message(StateFilter(None), CommandStart())
async def process_start_command(message: Message) -> None:
    db = DB_Users(user_id=message.from_user.id, user_name=message.from_user.username,
                  full_name=message.from_user.full_name)
    check = db.check_user()
    if not check:
        db.insert_new_user()
    await message.answer(text=LEXICON_RU['/start'], reply_markup=get_start_keyboard('global_tasks_button',
                                                                                    'daily_tasks_button', width=2))


@router.message(StateFilter(None), Command(commands='help'))
async def process_help_command(message: Message) -> None:
    await message.answer(text=LEXICON_RU['/help'])


@router.message(StateFilter(None), F.text == LEXICON_RU['global_tasks_button'])
async def process_global_tasks(message: Message, state: FSMContext) -> None:
    db = DB_GlobalTasks(message.from_user.id)
    if db.get_all_active_tasks():
        await message.answer(text=(f'{LEXICON_RU['global_tasks']}' + f'{db.get_all_active_tasks()}'))
    else:
        await message.answer(text='Активных задач нет.')
    await state.set_state(FSM_global_tasks.view_tasks)


@router.message(StateFilter(FSM_global_tasks.view_tasks), F.text == LEXICON_RU['redact_button'])
async def redact_global_tasks(message: Message, state: FSMContext) -> None:
    pass
