from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards import keyboard
from aiogram.fsm.context import FSMContext
from states import LoginState
from config import API_URL

import aiohttp

router=Router()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

@router.message(CommandStart())
async def handler_start(message:Message):
    await message.answer("eslatma bot",reply_markup=keyboard.login_kb)


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
        async with session.post(f"{API_URL}",json={"login":username,"password":password},headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                if result.get("success") and "data" in result:
                    
                    token = result["data"].get("accessToken")
                    student_info = result["data"].get("studentInfo",{})

                    if token:
                        await state.update_data(token=token)

                        first_name = student_info.get("firstName", "")
                        last_name = student_info.get("lastName", "")
                        middle_name = student_info.get("middleName", "")
                        login = student_info.get("login", username)
                        mobile = student_info.get("mobile", "")
                        
                        full_name = f"{first_name} {last_name} {middle_name}".strip()

                        await message.answer(
                            f"LOgin qilindi\n\n"
                            f"Ism: {full_name}\n"
                            f"Login: {login}\n"
                            f"Telefon: {mobile}"
                        )

                        await state.clear()
                        return
                    
                    await message.answer("token topilmadi")
                    await state.clear()
                    return
                
                else:
                    await message.answer("login yoki parol hato")
                    await state.clear()
                    return

    await message.answer("server bilan ulanishda xato")
    await state.clear()
