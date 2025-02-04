import streamlit as st
import requests
import json
from streamlit_autorefresh import st_autorefresh
from streamlit_javascript import st_javascript
from urllib.parse import urlparse, parse_qs, unquote
import re





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


def add_username(content):  # Функция распознания пользователя - добавляем ник в сообещние
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")

    # Извлечение фрагмента после '#'
    fragment = urlparse(url).fragment

    # Разделение фрагмента на параметры
    params = parse_qs(fragment)

    # Декодирование параметров
    decoded_params = {key: unquote(value[0]) for key, value in params.items()}


    user_data_str = decoded_params["tgWebAppData"].split('user=')[1].split('&')[0]

    # Преобразуем строку в словарь
    user_data = json.loads(user_data_str)

    # Извлекаем username
    username = user_data["username"]
    return username


def send_message_to_channel(content):  # Функция для отправки сообщения
    TOKEN = st.secrets["discord"]["token"]

    id_canal = "941976229412761653"

    # URL для отправки сообщения
    url = f"https://discord.com/api/v10/channels/{id_canal}/messages"

    # Заголовки запроса
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    send_message_to_channel(content)

    username = F"Сообщение от{name}"

    colored_message = F"""{username}```ansi
[2;31m[2;31m[2;31m[2;31m{content}[0m[2;31m[0m[2;31m[0m[2;31m[0m[2;31m[2;31m[2;31m[2;31m[2;41m[2;31m[2;31m[2;31m[0m[2;31m[2;41m[0m[2;31m[2;41m[0m[2;31m[2;41m[0m[2;31m[0m[2;31m[0m[2;31m[0m[2;31m[0m
```"""


    # Данные для отправки
    data = {
        "content": colored_message
    }


    # Отправка POST-запроса
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Проверка результата
    if response.status_code == 200:
        st.success("Сообщение успешно отправлено!")  # Уведомление в Streamlit
    else:
        st.error(f"Ошибка при отправке сообщения: {response.status_code}, {response.text}")  # Уведомление об ошибке


def remove_text(text):  # Очищяю текст от символов окрашивающих текст
    # Регулярное выражение для удаления всех ANSI-последовательностей
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    new_string = text.replace("```ansi", "")
    new_string = new_string.replace("```", "")
    return new_string


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

                cleaned_content = remove_text(content)

                # Формируем HTML для сообщения
                s1 = """<span class="username">"""
                s2 = "</span>"
                all_messages_html += F" {s1} {username} {s2} : {cleaned_content} <br>"

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

    # Поле для ввода сообщения
    message_content = st.text_input("Введите ваше сообщение в дискорд чат:")

    if st.button("Отправить"):     # Кнопка отправки
        if message_content:
            send_message_to_channel(message_content)
        else:
            st.warning("Введите текст сообщения.")  # Предупреждение, если поле пустое

    messages = get_discord_message()  # Пролучаем сообщения
    final_html = message_chat(messages)  # Формируем сообщения в чат

    # Отображаем сообщение с использованием HTML
    st.markdown(final_html, unsafe_allow_html=True)

    # Автоматический перезапуск приложения каждую минуту
    st_autorefresh(interval=60 * 1000, key="crow_refresh")

    # Вставляем CSS в Streamlit
    st.markdown(discord_style, unsafe_allow_html=True)

    url = st_javascript("await fetch('').then(r => window.parent.location.href)")

    # Извлечение фрагмента после '#'
    fragment = urlparse(url).fragment

    # Разделение фрагмента на параметры
    params = parse_qs(fragment)

    # Декодирование параметров
    decoded_params = {key: unquote(value[0]) for key, value in params.items()}


    user_data_str = decoded_params["tgWebAppData"].split('user=')[1].split('&')[0]

    # Преобразуем строку в словарь
    user_data = json.loads(user_data_str)

    # Извлекаем username
    username = user_data["username"]
    st.write(username)


if __name__ == '__main__':
    main()
