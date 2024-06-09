import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

language_options = ["Indonesia", "English"]
mode_options = ["Malam", "Siang"]
web_version = "1.0.0"

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
    </style>
""", unsafe_allow_html=True)

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    username TEXT UNIQUE,
    password TEXT
)
''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password):
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    if c.fetchone():
        return True
    return False

def register_user(name, email, phone, username, password):
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (name, email, phone, username, password) VALUES (?, ?, ?, ?, ?)",
                (name, email, phone, username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def admin_login(username, password):
    admin_users = {
        "adminallos": "allos123",
        "adminathif": "athif123",
        "adminnadia": "nadia123",
        "adminzidni": "zidni123",
        "adminfajar": "fajar123"
    }
    return username in admin_users and admin_users[username] == password

def delete_account(username, password):
    hashed_password = hash_password(password)
    c.execute("DELETE FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    conn.commit()

def change_password(username, old_password, new_password):
    hashed_old_password = hash_password(old_password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_old_password))
    if c.fetchone():
        hashed_new_password = hash_password(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_new_password, username))
        conn.commit()
        return True
    return False

def reset_password(username, new_password):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        hashed_new_password = hash_password(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_new_password, username))
        conn.commit()
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
    <div class="intro-text">
        Silahkan login terlebih dahulu untuk fitur lebih lanjut
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup, tab_loginadmin = st.tabs(["Login", "Sign Up", "Login Admin"])

    with tab_login:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns([4.20, 1])

        if col1.button("Login"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login berhasil!")
                st.experimental_rerun()
            else:
                c.execute("SELECT * FROM users WHERE username = ?", (username,))
                if c.fetchone():
                    st.error("Password salah")
                else:
                    st.error("Username tidak ditemukan")

        if col2.button("Lupa Password"):
            st.session_state.forgot_password = True
            st.experimental_rerun()

    with tab_signup:
        name = st.text_input("Nama")
        email = st.text_input("Email")
        phone = st.text_input("Nomor Handphone")
        new_username = st.text_input("Username ")
        new_password = st.text_input("Password ", type="password")

        if st.button("Sign Up"):
            if register_user(name, email, phone, new_username, new_password):
                st.session_state.message = "Registrasi berhasil! Silakan login."
                st.experimental_rerun()
            else:
                st.error("Username sudah terdaftar")

    with tab_loginadmin:
        st.subheader("Admin Login")
        admin_username = st.text_input("Username  ")
        admin_password = st.text_input("Password  ", type="password")
        if st.button("Login "):
            if admin_login(admin_username, admin_password):
                st.session_state.admin_logged_in = True
                st.success("Admin login berhasil!")
                st.experimental_rerun()
            else:
                st.error("username atau password admin salah")

def forgot_password_page():
    if st.button("< back"):
        st.session_state.forgot_password = False
        st.experimental_rerun()

    st.title("Lupa Password")
    st.write("Masukkan password baru Anda!")

    username = st.text_input("Username")
    new_password = st.text_input("Password Baru", type="password")

    if st.button("Reset Password"):
        if reset_password(username, new_password):
            st.session_state.forgot_password = False
            st.session_state.message = "Password berhasil direset. Silakan login dengan password baru Anda."
            st.experimental_rerun()
        else:
            st.error("Username tidak ditemukan. Silakan coba lagi.")

def get_user_data(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, email, phone, username, password FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()
    return user_data

def user_data_page(username):
    if st.button("< back"):
        st.session_state.show_user_data = False
        st.experimental_rerun()
    st.title("Informasi Akun Anda")
    user_data = get_user_data(username)
    if user_data:
        name, email, phone, username, _ = user_data
        new_name = st.text_input("Nama", value=name)
        new_email = st.text_input("Email", value=email)
        new_phone = st.text_input("Nomor Handphone", value=phone)
        new_username = st.text_input("Username", value=username)
        
        if st.button("Simpan Perubahan"):
            if (new_name != name or new_email != email or new_phone != phone or
                new_username != username):
                conn = connect_db()
                c = conn.cursor()
                c.execute("""
                UPDATE users SET name=?, email=?, phone=?, username=? WHERE username=?
                """, (new_name, new_email, new_phone, new_username, username))
                conn.commit()
                conn.close()
                st.success("Informasi akun berhasil diperbarui.")
                st.session_state.show_user_data = False
            else:
                st.warning("Tidak ada perubahan yang dibuat.")
    else:
        st.error("Data pengguna tidak ditemukan.")

def get_user_name(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "User"




#
#
#
#
#
#



def load_model():
    return joblib.load('model_saved3.joblib')

def load_columns():
    return joblib.load('X_columns2.joblib')

# Fungsi untuk melatih dan menyimpan model
def train_and_save_model():
    df = pd.read_csv('autos.csv')

    df.drop(columns=['index', 'dateCrawled', 'dateCreated', 'nrOfPictures', 'lastSeen'], inplace=True)

    df = df[(df['price'] > 100) & (df['price'] < 25000)]
    df = df[(df['powerPS'] > 50) & (df['powerPS'] < 1500)]
    df = df[(df['yearOfRegistration'] > 1970) & (df['yearOfRegistration'] < 2024)]

    df['vehicleType'].replace({'andere': 'other', 'kleinwagen': 'smallCar', 'kombi': 'stationWagon'}, inplace=True)
    df['fuelType'].replace({'benzin': 'gasoline', 'andere': 'other'}, inplace=True)
    df['gearbox'].replace({'manuell': 'Manual', 'automatik': 'Automatic'}, inplace=True)
    df['notRepairedDamage'].replace({'ja': 'Yes', 'nein': 'No'}, inplace=True)

    df.drop(['seller', 'offerType', 'monthOfRegistration', 'abtest', 'name'], axis=1, inplace=True)
    df.dropna(inplace=True)

    df['car_age'] = 2024 - df['yearOfRegistration']
    df.drop(columns=['yearOfRegistration'], inplace=True)

    df1 = df.copy()
    dummies = pd.get_dummies(df1[['vehicleType', 'gearbox', 'model', 'fuelType', 'brand', 'notRepairedDamage']])
    df2 = pd.concat([df1, dummies], axis=1)
    df2.drop(columns=['vehicleType', 'gearbox', 'model', 'fuelType', 'brand', 'notRepairedDamage'], axis=1, inplace=True)

    X = df2.drop(columns=['price'])
    y = df2['price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    gb_model = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1)
    dt_model = DecisionTreeRegressor()

    rf_model.fit(X_train, y_train)
    gb_model.fit(X_train, y_train)
    dt_model.fit(X_train, y_train)

    models = {'Random Forest': rf_model, 'Gradient Boosting': gb_model, 'Decision Tree': dt_model}
    scores = {}

    for name, model in models.items():
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        scores[name] = {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R2': r2}

    print(scores)

    best_model = gb_model  # Assuming Gradient Boosting is the best model
    joblib.dump(best_model, 'model_saved3.joblib')
    joblib.dump(X.columns, 'X_columns2.joblib')

# Fungsi untuk prediksi harga
def pcp(vehicleType, gearbox, fuelType, brand, vehicle_model, notRepairedDamage, powerPS, kilometer, car_age, postalCode, X, lr_model):
    def get_index(column_name):
        indices = np.where(X == column_name)[0]
        return indices[0] if len(indices) > 0 else -1

    vehicleType_index = get_index('vehicleType_' + vehicleType)
    gearbox_index = get_index('gearbox_' + gearbox)
    fuelType_index = get_index('fuelType_' + fuelType)
    brand_index = get_index('brand_' + brand)
    model_index = get_index('model_' + vehicle_model)
    notRepairedDamage_index = get_index('notRepairedDamage_' + notRepairedDamage)

    p = np.zeros(len(X))
    p[np.where(X == 'powerPS')[0][0]] = powerPS
    p[np.where(X == 'kilometer')[0][0]] = kilometer
    p[np.where(X == 'car_age')[0][0]] = car_age
    p[np.where(X == 'postalCode')[0][0]] = postalCode

    if vehicleType_index >= 0:
        p[vehicleType_index] = 1
    if gearbox_index >= 0:
        p[gearbox_index] = 1
    if fuelType_index >= 0:
        p[fuelType_index] = 1
    if brand_index >= 0:
        p[brand_index] = 1
    if model_index >= 0:
        p[model_index] = 1
    if notRepairedDamage_index >= 0:
        p[notRepairedDamage_index] = 1

    return lr_model.predict([p])[0]




#
#
#
#
#
#




def main_page():
    if st.session_state.logged_in:
        user_name = get_user_name(st.session_state.username)
        st.title(f"Hallo, {user_name} Selamat Datang di Mobi38!")

    menu = st.selectbox(
        "Pilih tindakan menu:",
        ("Pilih menu", "Profil", "Pengaturan", "Hapus Akun", "Ganti Password", "Logout")
    )
    if menu == "Profil":
        st.session_state.show_user_data = True
        st.experimental_rerun()

    elif menu == "Pengaturan":
        st.session_state.settings = True
        st.experimental_rerun()

    elif menu == "Ganti Password":
        st.session_state.change_password = True
        st.experimental_rerun()

    elif menu == "Hapus Akun":
        st.session_state.delete_account = True
        st.experimental_rerun()

    elif menu == "Logout":
        logout()

    if "message" in st.session_state:
        st.success(st.session_state.message)
        del st.session_state.message

    st.markdown("<hr>", unsafe_allow_html=True)
    st.title('Prediksi Harga Mobil')

    vehicleType = st.selectbox("Tipe Kendaraan", ["Pilih tipe kendaraan", "coupe", "SUV", "smallCar", "limousine", "cabrio", "bus", "stationWagon", "other"])
    vehicle_model = st.text_input("Model Kendaraan")
    fuelType = st.selectbox("Tipe Bahan Bakar", ["Pilih tipe bahan bakar", "diesel", "gasoline", "lpg", "other", "hybrid", "cng", "elektro"])
    kilometer = st.number_input("Kilometer yang sudah ditempuh", min_value=0)
    car_age = st.number_input("Usia Mobil (tahun)", min_value=0)
    gearbox = st.selectbox("Transmisi", ["Pilih tipe transmisi", "Manual", "Automatic"])
    brand = st.text_input("Merek Kendaraan")
    notRepairedDamage = st.selectbox("Kerusakan Tidak Diperbaiki", ["Pilih kerusakan", "Yes", "No"])
    powerPS = st.number_input("Daya Mesin (PS)", min_value=0)
    postalCode = st.number_input("Kode Pos", min_value=0)

    if st.button("Prediksi Harga"):
        model = load_model()
        X = load_columns()
        
        predicted_price = pcp(vehicleType, gearbox, fuelType, brand, vehicle_model, notRepairedDamage, powerPS, kilometer, car_age, postalCode, X, model)

        st.success(f"Mobil '{brand} {vehicle_model}' diprediksi memiliki harga jual: ${predicted_price:,.2f}")

def settings_page():
    if st.button('< back'):
        st.session_state.settings = False
        st.experimental_rerun()

    st.title("Pengaturan")
    st.write("Halaman ini berisi pengaturan akun pengguna.")
    
    selected_language = st.selectbox("Pilih Bahasa", language_options, key="language_select")
    selected_mode = st.selectbox("Pilih Mode", mode_options, key="mode_select")

    st.write("Versi Website:")
    st.write(f"Versi: {web_version}")

    if st.button('Butuh bantuan?'):
        st.session_state.help = not st.session_state.help  # Toggle help state
        st.experimental_rerun()

def help_page():
    if st.button('< back'):
        st.session_state.help = False
        st.experimental_rerun()
        
    st.title("Bantuan")
    st.write("Saran, Kritik, dan Bantuan hubungi admin: ")
    st.markdown("1. [Allos Mamaroh](#)")
    st.markdown("2. [Muhammad Athif Fadhlurrohman](#)")
    st.markdown("3. [Nadia Ifti Khani](#)")
    st.markdown("4. [Zidni Robby](#)")
    st.markdown("5. [Abdul Malik Fajar](#)")

def connect_db():
    conn = sqlite3.connect('users.db')
    return conn

def display_data():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def admin_page():
    st.title("Admin")
    st.write("Selamat datang di halaman admin")

    if "show_data" not in st.session_state:
        st.session_state.show_data = False

    if st.button("Tampilkan Data User dan Dataset"):
        st.session_state.show_data = not st.session_state.show_data

    if st.session_state.show_data:
        user_data = display_data()
        st.write("Berikut data akun user:")
        st.write(user_data)
        data_page()
        
    if st.button("Logout"):
        logout()

def data_page():
    st.title("Dataset")
    nama_file_csv = 'autos.csv'
    data = pd.read_csv(nama_file_csv)
    st.dataframe(data)

def delete_account_page():
    if st.button("< back"):
        st.session_state.delete_account = False
        st.experimental_rerun()

    st.title("Hapus Akun")
    st.warning("Anda yakin ingin menghapus akun? Tindakan ini tidak dapat dikembalikan.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Hapus Akun"):
        if check_login(username, password):
            delete_account(username, password)
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.message = "Akun berhasil dihapus. Anda telah logout."
            st.session_state.delete_account = False  
            st.experimental_rerun() 
            return 
        else:
            st.error("Username atau password salah. Akun tidak dihapus.")

def change_password_page():
    if st.button("< back"):
        st.session_state.change_password = False
        st.experimental_rerun()

    st.title("Ganti Password")
    st.warning("Ganti password hanya tersedia untuk pengguna yang sudah login.")
    username = st.text_input("Username")
    old_password = st.text_input("Password Lama", type="password")
    new_password = st.text_input("Password Baru", type="password")

    if st.button("Ganti Password"):
        if change_password(username, old_password, new_password):
            st.session_state.logged_in = False
            st.session_state.message = "Password berhasil diubah. Silakan login kembali."
            st.session_state.change_password = False  
            st.experimental_rerun()  
            return 
        else:
            st.error("Gagal mengganti password. Pastikan username dan password lama benar.")

def logout():
    st.session_state.logged_in = False
    st.session_state.admin_logged_in = False
    st.session_state.username = ""
    st.session_state.settings = False
    st.session_state.change_password = False
    st.session_state.delete_account = False
    st.session_state.show_user_data = False
    st.session_state.show_data = False
    st.session_state.forgot_password = False
    st.session_state.message = "Logout berhasil!"
    st.experimental_rerun()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if "show_data" not in st.session_state:
        st.session_state.show_data = False
    
    if "delete_account" not in st.session_state:
        st.session_state.delete_account = False

    if "change_password" not in st.session_state:
        st.session_state.change_password = False
    
    if "forgot_password" not in st.session_state:
        st.session_state.forgot_password = False

    if "settings" not in st.session_state:
        st.session_state.settings = False

    if "help" not in st.session_state:
        st.session_state.help = False

    if "message" in st.session_state:
        st.success(st.session_state.message)
        del st.session_state.message

    if "show_user_data" not in st.session_state:
        st.session_state.show_user_data = False

    if st.session_state.help:
        help_page()
    elif st.session_state.show_user_data:
        user_data_page(st.session_state.username)
    elif st.session_state.logged_in:
        if st.session_state.settings:
            settings_page()
        elif st.session_state.change_password:
            change_password_page()
        elif st.session_state.delete_account:
            delete_account_page()
        else:
            main_page()
    elif st.session_state.admin_logged_in:
        admin_page()
    elif st.session_state.forgot_password:
        forgot_password_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
    pass
