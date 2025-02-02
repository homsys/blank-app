import streamlit as st
import requests
import json
from streamlit_autorefresh import st_autorefresh

# CSS для стилизации сообщений
discord_style = """
<style>
.discord-message {
    background-color: #36393f;
    color: #ffffff;
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
    max-width: 70%;
    word-wrap: break-word;
    font-family: Arial, sans-serif;
}
.username {
    color: #7289da;
    font-weight: bold;
}
</style>
"""


@st.cache_data(ttl=60)  # Кэшируем данные на 60 секунд!
def get_crow_data():  # Функция получения данных о курсе crow
    params = {
        'symbol': 'CROW',
        'range': '1d',
    }
    try:
        response = requests.get('https://api.wemixplay.com/info/v2/price-chart', params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


@st.cache_data(ttl=60)  # Кэшируем данные на 60 секунд!
def get_discord_message():  # Функция получения сообщений от дискорда
    TOKEN = st.secrets["discord"]["token"]
    CHANNEL_ID = '1215815002422906881'
    headers = {
        "Authorization": f"Bot {TOKEN}"
    }
    params2 = {
        'chat_id': CHANNEL_ID,
        'limit': 30  # Получить только 30 сообщений
    }
    try:
        response_discord = requests.get(
            url=f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
            headers=headers,
            params=params2
        )
        response_discord.raise_for_status()  # Проверяем статус ответа
        return response_discord.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при запросе к Discord API: {e}")


def send_message_to_channel(content):  # Функция для отправки сообщения
    TOKEN = st.secrets["discord"]["token"]

    # URL для отправки сообщения
    url = f"https://discord.com/api/v10/channels/1215815002422906881/messages"

    # Заголовки запроса
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    # Данные для отправки
    data = {
        "content": content
    }

    # Отправка POST-запроса
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Проверка результата
    if response.status_code == 200:
        st.success("Сообщение успешно отправлено!")  # Уведомление в Streamlit
    else:
        st.error(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")  # Уведомление об ошибке


def message_chat(messages):  # Поиск сообщений и подготовка чата
    if messages:
        # Создаем пустую строку для хранения HTML-кода всех сообщений
        all_messages_html = ""
        try:
            for i in range(0, 30):  # Ограничение на 30 сообщений
                username = messages[i]["author"]["username"]
                content = messages[i]["content"]
                if content == "":
                    continue

                # Формируем HTML для сообщения
                s1 = """<span class="username">"""
                s2 = "</span>"
                all_messages_html += F" {s1} {username} {s2} : {content} <br>"

        except (IndexError, KeyError):
            pass

        # Обертываем все сообщения в один блок div
        final_html = f"""
                <div class="discord-message">
                    {all_messages_html}
                </div>
                """
        return final_html
    else:
        st.warning("Нет сообщений в канале.")


def find_values(data, key, result_list):  # Ищем значение
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                result_list.append(v)
            elif isinstance(v, (dict, list)):
                find_values(v, key, result_list)
    elif isinstance(data, list):
        for item in data:
            find_values(item, key, result_list)


def main():
    placeholder_crow = st.empty()
    placeholder_crow.write("Загрузка данных...")

    data = get_crow_data()

    if data is None:
        placeholder_crow.write("Ошибка обновления курса CROW")
        return

    list_crow = []
    find_values(data, 'p', list_crow)

    if not list_crow:
        placeholder_crow.write("Данные не найдены")
        return

    average = sum(list_crow) / len(list_crow)
    average = round(average, 4)
    placeholder_crow.write(f"CROW: $<span style='color:red'>{average}</span>", unsafe_allow_html=True)

    st.write("Discord чат:")

    # Поле для ввода сообщения
    message_content = st.text_input("Введите ваше сообщение:")

    # Кнопка отправки
    if st.button("Отправить"):
        if message_content:
            send_message_to_channel(message_content)
        else:
            st.warning("Введите текст сообщения.")  # Предупреждение, если поле пустое



    # Вставляем CSS в Streamlit
    st.markdown(discord_style, unsafe_allow_html=True)

    messages = get_discord_message()
    final_html = message_chat(messages)

    # Отображаем сообщение с использованием HTML
    st.markdown(final_html, unsafe_allow_html=True)
    # Автоматический перезапуск приложения каждую минуту
    st_autorefresh(interval=60 * 1000, key="crow_refresh")


if __name__ == '__main__':
    main()
