# pip install streamlit
# pip install requests

import streamlit as st
import requests
import pandas as pd

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
    st.title("Курс CROW")
    if st.button("Узнать"):
        try:
            response = requests.get('https://api.wemixplay.com/info/v2/price-chart', params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            print("Ошибка get запроса получения цены, повторим через 5 минут")

        if response.ok:
            list_crow.clear()
            find_values(response.json(), 'p')

            average = sum(list_crow) / len(list_crow)  # Вычисляем среднее значение
            average = round(average, 4)  # Округляем

        st.write(f"Актуальный курс: {average}")
        df = pd.DataFrame(list_crow, columns=["Average"])
        st.line_chart(df)


if __name__ == '__main__':
    main()
