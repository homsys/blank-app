import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# Автоматический перезапуск приложения каждую минуту
st_autorefresh(interval=60 * 1000, key="crow_refresh")

params = {
    'symbol': 'CROW',
    'range': '1d',
}


@st.cache_data(ttl=60)  # Кэшируем данные на 60 секунд!
def get_crow_data():
    try:
        response = requests.get('https://api.wemixplay.com/info/v2/price-chart', params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def find_values(data, key, result_list):
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
    st.title("NightCrow")
    placeholder_crow = st.empty()

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


if __name__ == '__main__':
    main()
