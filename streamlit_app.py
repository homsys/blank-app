#  pip install streamlit

import streamlit as st


def main():
    st.title("Курс CROW")

    # Здесь можно добавить элементы управления для взаимодействия с ботом
    user_input = st.text_input("Введите сообщение для бота")

    if st.button("Отправить"):
        # Здесь можно добавить логику для отправки сообщения боту
        st.write(f"Вы отправили: {user_input}")


if __name__ == '__main__':
    main()
