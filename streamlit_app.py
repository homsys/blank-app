# pip install streamlit
# pip install requests

import streamlit as st
import requests
import time

list_crow = []
params = {
    'symbol': 'CROW',
    'range': '1d',
}


def find_values(data, key):  # Функция для поиска значения
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                list_crow.append(v)
            elif isinstance(v, (dict, list)):
                find_values(v, key)
    elif isinstance(data, list):
        for item in data:
            find_values(item, key)


def main():
    st.title("NightCrow")
    placeholder_crow = st.empty()  # Создаем контейнер для отображения курса

    while True:
        try:
            response = requests.get('https://api.wemixplay.com/info/v2/price-chart', params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            placeholder_crow.write(
                f"Ошибка обновления курса CROW, всё пропало, бежим кто-куда!!!")
            time.sleep(60)
            continue

        if response.ok:
            list_crow.clear()
            find_values(response.json(), 'p')

            average = sum(list_crow) / len(list_crow)  # Вычисляем среднее значение
            average = round(average, 4)  # Округляем

            a = 60
            for i in range(60):
                time.sleep(1)
                a -= 1
                if i == 59:
                    placeholder_crow.write(
                        f"До обновления курса CROW, {a} секунд:  $<span style='color:red'>{average}</span>",
                        unsafe_allow_html=True)  # Обновляем контейнер с новым значением

                else:
                    placeholder_crow.write(f"До обновления курса CROW, {a} секунд:  ${average}")  # Обновляем контейнер с новым значением


if __name__ == '__main__':
    main()
