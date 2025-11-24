@router.message(F.text == "task_chek")
async def task_check(message: Message):
    token = get_token(message.from_user.id)

    if not token:
        await message.answer("❌ Avval login qiling!")
        return

    await message.answer("📚 Vazifalar yuklanmoqda...")

    # ✅ To'liq headers - 417 xatosini oldini olish uchun
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://erp.student.najottalim.uz",
        "Referer": "https://erp.student.najottalim.uz/"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(TASK_URL, headers=headers) as response:
                
                print(f"📊 Status: {response.status}")  # Debug
                print(f"📄 Headers sent: {headers}")  # Debug
                
                if response.status == 401:
                    await message.answer("❌ Token eskirgan. Qaytadan login qiling!")
                    delete_token(message.from_user.id)
                    return
                
                if response.status == 417:
                    await message.answer("❌ Server 417 xatosi. Iltimos, qaytadan login qiling.")
                    delete_token(message.from_user.id)
                    return
                
                if response.status != 200:
                    response_text = await response.text()
                    print(f"❌ Error response: {response_text}")  # Debug
                    await message.answer(f"❌ Xato: {response.status}\n{response_text[:200]}")
                    return

                data = await response.json()
                print(f"✅ Response: {data}")  # Debug

                # ✅ To'g'ri strukturadan olish
                tasks = (
                    data.get("data", {})
                    .get("groupLessonsData", {})
                    .get("groupLessons", [])
                )
                
                if not tasks:
                    await message.answer("📭 Hozircha vazifalar yo'q")
                    return

                # Homework statuslari
                status_map = {
                    1: "✅ Bajarilgan",
                    2: "⏳ Kutilmoqda",
                    3: "✅ Tekshirilgan",
                    4: "📝 Jarayonda",
                    5: "❌ Bajarilmagan",
                    6: "🚫 Vazifa yo'q"
                }

                text = f"📚 <b>Vazifalar ro'yxati ({len(tasks)} ta):</b>\n\n"
                
                for i, task in enumerate(tasks, 1):
                    name = task.get('name', 'Nomsiz vazifa')
                    hw_status = task.get('homeworkStatus', 6)
                    score = task.get('score', 0)
                    xp = task.get('xp', 0)
                    coin = task.get('coin', 0)
                    deadline = task.get('homeworkDeadline', '')
                    
                    # Status emoji
                    status_text = status_map.get(hw_status, "❓ Noma'lum")
                    
                    text += f"<b>{i}. {name}</b>\n"
                    text += f"   {status_text}\n"
                    
                    if score > 0:
                        text += f"   📊 Ball: {score}\n"
                    if xp > 0:
                        text += f"   ⭐ XP: {xp}\n"
                    if coin > 0:
                        text += f"   🪙 Coin: {coin}\n"
                    if deadline and hw_status in [2, 4, 5]:
                        # Deadline'ni formatlash
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(deadline.replace('GMT+0000', '+00:00'))
                            text += f"   ⏰ Deadline: {dt.strftime('%d.%m.%Y %H:%M')}\n"
                        except:
                            text += f"   ⏰ Deadline: {deadline[:10]}\n"
                    
                    text += "\n"

                # Guruh nomini qo'shish
                group_name = data.get("data", {}).get("groupLessonsData", {}).get("groupName", "")
                if group_name:
                    text += f"\n👥 <b>Guruh:</b> {group_name}\n"
                
                # Statistika
                completed = sum(1 for t in tasks if t.get('homeworkStatus') in [1, 3])
                pending = sum(1 for t in tasks if t.get('homeworkStatus') in [2, 4])
                text += f"\n📈 <b>Statistika:</b> {completed} bajarilgan, {pending} kutilmoqda"

                await message.answer(text, parse_mode="HTML")

        except aiohttp.ClientError as e:
            await message.answer(f"❌ Tarmoq xatosi: {str(e)}")
        except Exception as e:
            print(f"❌ Exception: {e}")  # Debug
            await message.answer(f"❌ Xatolik: {str(e)}")