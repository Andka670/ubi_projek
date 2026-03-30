import streamlit as st
from supabase import create_client
import pandas as pd
import uuid
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Admin Panel",
    layout="wide",
    initial_sidebar_state="collapsed"
)

url = "https://ukgzplcpupucrlalkafs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrZ3pwbGNwdXB1Y3JsYWxrYWZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDA0MzUsImV4cCI6MjA5MDI3NjQzNX0.8ugnFoGqW71PbP4PRtp1UUTznhh3iJjRuwQrFgbP_Qw"
supabase = create_client(url, key)
if "login" not in st.session_state or not st.session_state.login:
    st.switch_page("pages/login.py")
# ================= DARK UI PREMIUM =================
st.markdown("""
<style>

/* ===== BACKGROUND SOFT GRADIENT ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1e1b4b, #6d28d9, #c4b5fd);
}
/* SEMBUNYIKAN SIDEBAR NAV BAWAAN (pages) */
[data-testid="stSidebarNav"] {
    display: none;
}
/* TRANSPARAN CONTAINER */
.main, .block-container {
    background: transparent;
    padding-top: 2rem;
}

/* ===== SIDEBAR CLEAN ===== */
section[data-testid="stSidebar"] {
    background: rgba(30, 27, 75, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.1);
}
/* ===== EXPANDER STYLE ===== */
details {
    background: rgba(16, 185, 129, 0.25); /* berubah jadi hijau */
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.2);
}

/* HEADER (judul expander) */
details summary {
    color: white !important;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
}

/* HOVER */
details:hover {
    background: rgba(124, 58, 237, 0.35);
}

/* SAAT TERBUKA */
details[open] {
    background: rgba(16, 185, 129, 0.25); /* berubah jadi hijau */
    border: 1px solid rgba(16,185,129,0.5);
}
/* LOGO */
section[data-testid="stSidebar"]::before {
    content: "🍠 ARDYELA";
    display: block;
    font-size: 20px;
    font-weight: 600;
    padding: 18px;
    text-align: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    color: white;
}

/* MENU TITLE */
section[data-testid="stSidebar"] h2 {
    color: #c4b5fd !important;
    font-size: 26px !important;
    text-align: center;
}

div[role="radiogroup"] input:checked + div {
    background: rgba(124,58,237,0.2);
    border-left: 4px solid #a78bfa;
    border-radius: 8px;
    color: white !important;
    padding: 10px 14px;
}

/* ===== CARD PRODUK ===== */
.card {
    display: flex;
    gap: 12px;
    align-items: center;
    background: rgba(6, 182, 212, 0.22);
    backdrop-filter: blur(12px);
    width: 100%;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.15);
    transition: 0.25s;
    margin-bottom: 15px;
    padding: 10px;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.card img {
    width: 90px;
    height: 90px;
    border-radius: 12px;
    object-fit: cover;
}

.card-body {
    flex: 1;
}

.title {
    font-size: 16px;
    font-weight: 600;
    color: white;
}

.price {
    color: #c4b5fd;
    font-weight: 600;
    font-size: 14px;
}

p {
    color: #e5e7eb;
    font-size: 13px;
}

/* ================= BUTTON STYLE FIX ================= */

/* TAMBAH / PRIMARY BUTTON */
.stButton button[kind="primary"] {
    border-radius: 10px;
    background: linear-gradient(45deg, #10b981, #34d399);
    color: white !important;
    border: none !important;
}

/* hover primary */
.stButton button[kind="primary"]:hover {
    box-shadow: 0 5px 15px rgba(124,58,237,0.5) !important;
}

/* DELETE BUTTON (merah) */
.stButton button[kind="secondary"] {
    border-radius: 10px;
    background: linear-gradient(45deg, #ef4444, #dc2626) !important;
    color: white !important;
    border: none !important;
}

.stButton button[kind="secondary"]:hover {
    box-shadow: 0 5px 15px rgba(239,68,68,0.5) !important;
}

</style>
""", unsafe_allow_html=True)

# ================= HELPER =================
def rp(x): return f"Rp {x:,.0f}".replace(",", ".")

# ================= STORAGE =================
def upload_gambar(file):
    if file is None:
        return None

    file_name = f"{uuid.uuid4()}.{file.name.split('.')[-1]}"

    supabase.storage.from_("produk").upload(
        file_name,
        file.getvalue(),
        {"content-type": file.type}
    )

    return supabase.storage.from_("produk").get_public_url(file_name)

# ================= DB =================
def get_produk():
    return supabase.table("produk").select("*").execute().data

def insert_produk(data):
    supabase.table("produk").insert(data).execute()

def update_produk(id, data):
    supabase.table("produk").update(data).eq("id", id).execute()

def delete_produk(id):
    supabase.table("produk").delete().eq("id", id).execute()

def get_laporan():
    return supabase.table("pemesanan").select("*").execute().data
# USER =================
def get_users():
    return supabase.table("akun").select("*").execute().data

def insert_user(data):
    supabase.table("akun").insert(data).execute()

def update_user(id, data):
    supabase.table("akun").update(data).eq("id", id).execute()

def delete_user(id):
    supabase.table("akun").delete().eq("id", id).execute()

# ================= UI =================
st.markdown("<h1 style='color:white;'>Admin Panel</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='color:white;'>MENU</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("", [
    "📊 Dashboard",
    "📦 Produk",
    "🧾 Transaksi",
    "👤 Pengguna"
])

# ================= LOGOUT BUTTON (PALING BAWAH) =================
st.sidebar.markdown("""
<style>
div.stButton > button {
    display: block;
    margin: 0 auto;
    width: 80%;
}
</style>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# ================= DASHBOARD =================
if menu == "📊 Dashboard":

    data = supabase.table("pemesanan").select("*").execute().data

    if data:
        df = pd.DataFrame(data)

        # ================= STAT =================
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='stat-card'><div>Total</div><div class='stat-value'>{rp(df['total'].sum())}</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='stat-card'><div>Transaksi</div><div class='stat-value'>{len(df)}</div></div>", unsafe_allow_html=True)

        # ================= FORMAT =================
        df['tanggal'] = pd.to_datetime(df['tanggal'])

        # ================= GROUP =================
        df_group = df.groupby(['tanggal', 'nama_kasir'])['total'].sum().reset_index()

        # ================= GRAFIK =================
        fig = px.line(
            df_group,
            x="tanggal",
            y="total",
            color="nama_kasir",  # 🔥 langsung per kasir
            title="Grafik Penjualan (Pemesanan)",
            markers=True
        )

        fig.update_layout(template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Belum ada data")
# ================= GRAFIK DETAIL PEMESANAN =================
    st.markdown("### 📦 Grafik Detail Pemesanan")

    detail = supabase.table("detail_pemesanan").select("*").execute().data

    if detail:
        df_detail = pd.DataFrame(detail)

        # kalau ada tanggal
        if 'tanggal' in df_detail.columns:
            df_detail['tanggal'] = pd.to_datetime(df_detail['tanggal'])

        # ================= GROUP =================
        # contoh: total penjualan per produk
        df_produk = df_detail.groupby('produk')['subtotal'].sum().reset_index()

        # ================= GRAFIK =================
        fig2 = px.bar(
            df_produk,
            x="produk",
            y="subtotal",
            title="Penjualan per Produk",
            text_auto=True
        )

        fig2.update_layout(template="plotly_dark")

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Belum ada data detail")
# ================= PRODUK =================
elif menu == "📦 Produk":

    with st.expander("➕ Tambah Produk"):
        nama = st.text_input("Nama")
        harga = st.number_input("Harga")
        stok = st.number_input("Stok")
        desk = st.text_area("Deskripsi")
        img = st.file_uploader("Upload gambar")

        if st.button("Simpan", type="primary"):
            url_img = upload_gambar(img)
            insert_produk({
                "nama": nama,
                "harga": harga,
                "stok": stok,
                "deskripsi": desk,
                "gambar": url_img
            })
            st.success("Berhasil!")
            st.rerun()

    data = get_produk()

    if data:
        nama_list = ["Semua"] + [item['nama'] for item in data]
        selected = st.selectbox("🔍 Cari Produk", nama_list)

        for item in data:
            if selected != "Semua" and item['nama'] != selected:
                continue

            id_str = str(item['id'])
            img = item.get("gambar") or "https://via.placeholder.com/300"

            st.markdown(f"""
            <div class="card">
                <img src="{img}">
                <div class="card-body">
                    <div class="title">{item['nama']}</div>
                    <div class="price">{rp(item['harga'])}</div>
                    <p>Stok: {item['stok']}</p>
                    <p>{item.get('deskripsi','-')[:60]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            if col1.button("🗑️ Hapus", key="d"+id_str, type="secondary"):
                delete_produk(item['id'])
                st.rerun()

            with col2.expander("Edit"):
                nama_b = st.text_input("Nama", item['nama'], key="n"+id_str)
                harga_b = st.number_input("Harga", value=item['harga'], key="h"+id_str)
                stok_b = st.number_input("Stok", value=item['stok'], key="s"+id_str)
                desk_b = st.text_area("Desk", item.get('deskripsi',''), key="x"+id_str)
                img_b = st.file_uploader("Ganti gambar", key="i"+id_str)

                if st.button("Update", key="u"+id_str, type="primary"):
                    url_img = item.get("gambar")
                    if img_b:
                        url_img = upload_gambar(img_b)

                    update_produk(item['id'], {
                        "nama": nama_b,
                        "harga": harga_b,
                        "stok": stok_b,
                        "deskripsi": desk_b,
                        "gambar": url_img
                    })
                    st.rerun()

# ================= TRANSAKSI =================
elif menu == "🧾 Transaksi":
    data = get_laporan()

    if data:
        df = pd.DataFrame(data)

        # ================= AMBIL DETAIL =================
        detail = supabase.table("detail_pemesanan").select("*").execute().data
        df_detail = pd.DataFrame(detail)

        # ================= AMBIL PEMESANAN (KASIR) =================
        pemesanan = supabase.table("pemesanan").select("id,nama_kasir").execute().data
        df_kasir = pd.DataFrame(pemesanan)

        # ================= MERGE =================
        df_detail = df_detail.merge(
            df_kasir,
            left_on="order_id",   # SESUAIKAN kalau beda
            right_on="id",
            how="left"
        )

        # ================= FILTER =================
        st.markdown("## 🔍 Filter Data")

        col1, col2 = st.columns(2)

        # list kasir
        list_kasir = df_detail['nama_kasir'].dropna().unique().tolist()
        list_kasir.insert(0, "Semua")

        with col1:
            filter_kasir = st.selectbox("Filter Kasir", list_kasir)

        with col2:
            search_id = st.text_input("Cari ID Transaksi")

        st.markdown("## 🧾 Data Transaksi")

        # ================= LOOP TRANSAKSI =================
        for _, row in df.iterrows():

            # filter detail berdasarkan order_id
            detail_transaksi = df_detail[df_detail['order_id'] == row['id']]

            # ambil nama kasir
            nama_kasir = "-"
            if not detail_transaksi.empty:
                nama_kasir = detail_transaksi.iloc[0].get("nama_kasir", "-")

            # ================= APPLY FILTER =================
            if filter_kasir != "Semua" and nama_kasir != filter_kasir:
                continue

            if search_id and search_id not in str(row['id']):
                continue

            # ================= UI =================
            with st.expander(
                f"🧾 ID: {row['id']} | 👤 {nama_kasir} | 💰 {rp(row['total'])}"
            ):

                st.write({
                    "Tanggal": row.get("tanggal"),
                    "Total": rp(row.get("total", 0)),
                    "Kasir": nama_kasir
                })

                # ================= DETAIL =================
                if not detail_transaksi.empty:
                    st.markdown("### 📦 Detail Pemesanan")

                    st.dataframe(
                        detail_transaksi[['produk', 'jumlah', 'subtotal']],
                        use_container_width=True
                    )
                else:
                    st.info("Tidak ada detail")

        # ================= DOWNLOAD =================
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download CSV", csv, "laporan.csv")

    else:
        st.info("Belum ada transaksi")
# ================= PENGGUNA =================
elif menu == "👤 Pengguna":

    st.subheader("🔑 Ubah Password Admin")

    username = st.session_state.get("username")

    pw1 = st.text_input("Password Baru", type="password")
    pw2 = st.text_input("Konfirmasi Password", type="password")

    if st.button("Update Password", type="primary"):
        if not pw1 or not pw2:
            st.error("Password tidak boleh kosong!")
        elif pw1 != pw2:
            st.error("Password tidak sama!")
        elif len(pw1) < 4:
            st.error("Password minimal 4 karakter")
        else:
            supabase.table("akun").update({
                "password": pw1
            }).eq("username", username).execute()

            st.success("Password berhasil diubah!")

    st.markdown("---")

    st.subheader("👥 Manajemen Kasir")

    # ===== TAMBAH KASIR =====
    with st.expander("➕ Tambah Kasir"):
        u = st.text_input("Username Kasir", key="t_user")
        p = st.text_input("Password Kasir", type="password", key="t_pass")

        if st.button("Tambah Kasir", type="primary"):
            if not u or not p:
                st.error("Username & Password wajib diisi!")
            else:
                supabase.table("akun").insert({
                    "username": u,
                    "password": p,
                    "keterangan": "kasir"
                }).execute()

                st.success("Kasir ditambahkan!")
                st.rerun()

    # ===== LIST KASIR =====
    users = get_users()

    if users:
        for usr in users:

            # FILTER HANYA KASIR
            if usr.get("keterangan") != "kasir":
                continue

            id_str = str(usr["id_akun"])

            st.markdown(f"""
            <div class="card">
                <div class="card-body">
                    <div class="title">👤 {usr['username']}</div>
                    <p>Keterangan: Kasir</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            # ===== DELETE =====
            if col1.button("🗑️ Hapus", key="del_user_" + id_str, type="secondary"):
                supabase.table("akun").delete().eq("id_akun", usr["id_akun"]).execute()
                st.rerun()

            # ===== EDIT =====
            with col2.expander("Edit"):
                new_u = st.text_input("Username", usr["username"], key="u_" + id_str)
                new_p = st.text_input("Password Baru", type="password", key="p_" + id_str)

                if st.button("Update", key="up_" + id_str, type="primary"):
                    if not new_u:
                        st.error("Username tidak boleh kosong!")
                    else:
                        data_update = {"username": new_u}

                        if new_p:
                            data_update["password"] = new_p

                        supabase.table("akun").update(data_update)\
                            .eq("id_akun", usr["id_akun"])\
                            .execute()

                        st.success("Berhasil update!")
                        st.rerun()

    else:
        st.info("Belum ada user kasir")