from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import keyboard
from aiogram.fsm.context import FSMContext
from states import LoginState
from config import API_URL

import aiohttp

router=Router()

@router.message(CommandStart())
async def handler_start(message:Message):
    await message.answer("salo men eslatma botman",reply_markup=keyboard.login_kb)


@router.message(F.text == "login qilish")
async def login_sorash(message:Message,state:FSMContext):
    await state.set_state(LoginState.waiting_username)
    await message.answer("login kiriting")


@router.message(LoginState.waiting_username)
async def get_username(message:Message,state:FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(LoginState.waiting_password)
    await message.answer("parol kiritng")

@router.message(LoginState.waiting_password)
async def get_password(message:Message,state:FSMContext):
    data = await state.get_data()
    username = data['username']
    password = message.text


    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}",json={"username":username,"password":password})as resp:
            if resp.status !=200:
                await message.answer("login yoki parol hato")
                await state.clear()
                return
            result = await resp.json()
            token = result.get("token")


    await state.update_data(token=token)
    await message.answer("login qilindi malumot olinmoqda")


    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/user/me", headers={"Authorization": f"Bearer {token}"}) as resp:


            if resp.status != 200:
                await message.answer("malumotlar yuklanmadi")
                await state.clear()
                return
            
            profile = await resp.json()

            data = profile.get("data",{})


            user_id = data.get("id")
            first_name = data.get("firstName")
            last_name = data.get("lastName")

            text =f"malumotlaringiz:\n\n {user_id}\nIsm: {first_name}\nFailya: {last_name}"

            await message.answer(text)