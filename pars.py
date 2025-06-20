import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import telebot

# ==== НАСТРОЙКА TELEGRAM ====
TOKEN = ''
CHAT_ID = ''
bot = telebot.TeleBot(TOKEN)

# ==== ФУНКЦИЯ ЦВЕТА ====
def get_color(price):
    try:
        p = int(price)
        if 1 <= p <= 4:
            return "🔴"
        elif 5 <= p <= 6:
            return "🟡"
        elif 7 <= p <= 10:
            return "🟢"
    except:
        return "⚪️"

# ==== ФУНКЦИЯ ПАРСИНГА И ОТПРАВКИ ====
def parse_and_notify():
    options = uc.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://fragment.com/?sort=price_asc&filter=sale")
        time.sleep(2)

        # Парсинг
        results = []
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tm-row-selectable"))
            )
            rows = driver.find_elements(By.CLASS_NAME, "tm-row-selectable")
            print("✅ Таблица найдена")

            for i, row in enumerate(rows[:10]):
                try:
                    username = row.find_element(By.CLASS_NAME, "tm-value").text.strip()
                    ton_price = row.find_element(By.CLASS_NAME, "icon-ton").text.strip()
                    results.append((username, ton_price))
                except Exception as e:
                    print(f"{i+1}. ❌ Парсинг строки: {e}")
        except:
            print("❌ Таблица не найдена")

        # Telegram сообщение
        if results:
            message = "👤 <b>Юзернеймы на продаже:</b>\n\n"
            for i, (username, ton_price) in enumerate(results, start=1):
                username_clean = username.replace("@", "")
                link = f"https://fragment.com/username/{username_clean}"
                color = get_color(ton_price)
                message += f'{i}. {username} | <a href="{link}">{ton_price} TON</a> {color}\n'

            bot.send_message(CHAT_ID, message, parse_mode="HTML", disable_web_page_preview=True)
            print("📬 Сообщение отправлено")
        else:
            print("⚠️ Нет данных для отправки")

    except Exception as e:
        print(f"❌ Ошибка парсера: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

# ==== АВТОЗАПУСК ====
print("🔁 Парсер запущен. Проверка каждые 10 секунд.\n")
while True:
    parse_and_notify()
    print("⏱ Ждём 10 секунд...\n")
    time.sleep(10)
