import streamlit as st
from supabase import create_client

# ================= SUPABASE CONFIG =================
SUPABASE_URL = "https://ukgzplcpupucrlalkafs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrZ3pwbGNwdXB1Y3JsYWxrYWZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDA0MzUsImV4cCI6MjA5MDI3NjQzNX0.8ugnFoGqW71PbP4PRtp1UUTznhh3iJjRuwQrFgbP_Qw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Login System",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= DESIGN PRO =================
st.markdown("""
<style>

/* HIDE DEFAULT */
[data-testid="stSidebar"] {display:none;}
[data-testid="stSidebarNav"] {display:none;}
header {visibility:hidden;}
footer {visibility:hidden;}

/* BACKGROUND ANIMASI */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #ffffff, #ede9fe, #c4b5fd, #8b5cf6);
    background-size: 400% 400%;
    animation: gradientMove 10s ease infinite;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* CENTER */
.block-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* STREAMLIT CONTAINER JADI LOGIN BOX */
.block-container > div {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(18px);
    padding: 40px;
    border-radius: 18px;
    width: 380px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.6);
    animation: fadeUp 0.8s ease;
}

/* ANIMASI MASUK */
@keyframes fadeUp {
    from {opacity:0; transform:translateY(30px);}
    to {opacity:1; transform:translateY(0);}
}

/* TITLE */
.title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: #4c1d95;
}
/* WARNA JUDUL DI ATAS INPUT (USERNAME & PASSWORD) */
.stTextInput > label {
    color: #4c1d95 !important;
    font-weight: 600;
    font-size: 14px;
}
/* SUBTITLE */
.subtitle {
    text-align: center;
    font-size: 14px;
    color: #4c1d95;
    margin-bottom: 25px;
}

/* INPUT */
.stTextInput input {
    border-radius: 10px !important;
    padding: 12px !important;
}

/* BUTTON */
.stButton button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(45deg, #7c3aed, #a78bfa);
    color: white;
    border: none;
    font-weight: 600;
    padding: 12px;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(124,58,237,0.4);
}

</style>
""", unsafe_allow_html=True)

# ================= SESSION INIT =================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# ================= AUTO REDIRECT =================
if st.session_state.login:
    if st.session_state.role == "admin":
        st.switch_page("app.py")
    elif st.session_state.role == "kasir":
        st.switch_page("app.py")

# ================= UI =================
st.markdown("<div class='title'>LOGIN SYSTEM</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Masuk ke sistem Ardyela</div>", unsafe_allow_html=True)

username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_btn = st.button("Login")

st.markdown("</div>", unsafe_allow_html=True)

# ================= LOGIN PROCESS =================
if login_btn:
    username = username.strip()
    password = password.strip()

    if username == "" or password == "":
        st.warning("Username dan password tidak boleh kosong!")
    else:
        try:
            response = supabase.table("akun") \
                .select("*") \
                .eq("username", username) \
                .eq("password", password) \
                .execute()

            data = response.data

            if data and len(data) > 0:
                user = data[0]
                role = user.get("keterangan", "").strip().lower()
                st.session_state.login = True
                st.session_state.username = user["username"]
                st.session_state.role = role
                st.session_state.user_id = user["id_akun"]   # 🔥 INI PENTING
                st.session_state.login = True
                st.session_state.username = username
                st.session_state.role = role

                st.success(f"Login berhasil sebagai {role}!")

                if role == "admin":
                    st.switch_page("app.py")
                elif role == "kasir":
                    st.switch_page("app.py")
                else:
                    st.error("Role tidak dikenali di database!")

            else:
                st.error("Username atau password salah!")

        except Exception as e:
            st.error("Terjadi kesalahan koneksi ke Supabase.")
            st.error(e)