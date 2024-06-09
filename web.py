import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.markdown("""
    <style>
        .intro-text {
            max-width: 800px;
            margin: auto;
            padding: 10px;
            font-size: 18px;
            line-height: 1.6;
            text-align: justify;
        }
        .intro-text1 {
            max-width: 800px;
            margin: auto;
            padding: 10px;
            font-size: 18px;
            line-height: 1.6;
            text-align: justify;
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

users = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"},
}

def check_login(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

def login_page():
    st.title("Welcome in Mobi38!")
    st.markdown("""
    <div class="intro-text">
        Selamat datang di Mobi38, platform terdepan untuk prediksi harga mobil yang akurat dan terpercaya. 
        Di Mobi38, kami memahami bahwa membeli atau menjual mobil merupakan keputusan besar yang memerlukan informasi yang tepat dan terkini. 
        Oleh karena itu, kami hadir untuk membantu Anda dengan menyediakan prediksi harga mobil yang didukung oleh data dan analisis mendalam.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="intro-text1">
        Login terlebih dahulu, registrasi akun baru hubungi developer.
    </div>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Username atau password salah")
            
def main_page():
    st.title(f"Hallo, {st.session_state.username}")


    load_model = joblib.load('gradient_boosting_model.joblib')


    nama_file_csv = 'autos.csv'
    data = pd.read_csv(nama_file_csv)
    st.title('Prediksi Harga Mobil')

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input('Masukkan Nama Mobil')
    with col2:
        price = st.text_input('Masukkan Harga Mobil')
    with col1:
        vehicleType = st.text_input('Masukkan Jenis Kendaraan')
    with col2:
        model = st.text_input('Masukkan Model Mobil')
    with col1:
        fuelType = st.text_input('Masukkan Jenis Bensin')
    with col2:
        kilometer = st.text_input('Masukkan Kilometer')
    with col1:
        yearOfRegistration = st.text_input('Masukkan Tahun Kendaraan')
    with col2:
        gearbox = st.text_input('Masukkan Tipe Persneling')
    with col1:
        brand = st.text_input('Masukkan Merk Kendaraan')
    with col2:
        monthOfRegistration = st.text_input('Masukkan Bulan Pendaftaran')


    # Prediksi Harga
    data = pd.DataFrame({
        'name': [name],
        'prrice': [price],
        'vehicleType': [vehicleType],
        'model': [model],
        'fuelType': [fuelType],
        'kilometer': [kilometer],
        'yearOfRegistration': [yearOfRegistration],
        'gearbox': [gearbox],
        'brand': [brand],
        'monthOfRegistration': [monthOfRegistration]
    })
    
    prediksi = load_model.predict(data)
    
    if st.button('Lihat Hasil Tes'):
        st.write('Prediksi harga mobil belum diimplementasikan.', prediksi[0])
    
    if st.button('Lihat Dataset'):
        st.session_state.show_data = True
        st.experimental_rerun()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

def data_page():
    st.title("Dataset")
    nama_file_csv = 'autos.csv'
    data = pd.read_csv(nama_file_csv)
    st.dataframe(data)

    if st.button('Kembali'):
        st.session_state.show_data = False
        st.experimental_rerun()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "show_data" not in st.session_state:
        st.session_state.show_data = False
    
    if st.session_state.logged_in:
        if st.session_state.show_data:
            data_page()
        else:
            main_page()
    else:
        login_page()

if __name__ == "__main__":
    main()

st.markdown('<a href="mailto:zidni@gmail.com">Contact us !</a>', unsafe_allow_html=True)    