import streamlit as st
from supabase import create_client
import pandas as pd
import uuid
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
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
/* ===== TEXT GLOBAL (KECUALI INPUT) ===== */
body, .stApp {
    color: white;
}

/* Judul & teks */
h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

/* Markdown */
[data-testid="stMarkdownContainer"] {
    color: white !important;
}

/* ===== EXCLUDE INPUT & SELECT ===== */


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
def get_pengeluaran():
    return supabase.table("pengeluaran").select("*").execute().data
# ================= UI =================
st.markdown("<h1 style='color:white;'>Admin Panel</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='color:white;'>MENU</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("", [
    "📊 Dashboard",
    "📦 Produk",
    "🧾 Transaksi",
    "📈 Analisa Keuangan",
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
        harga = st.number_input("Harga Jual", min_value=0)
        harga_beli = st.number_input("Harga Beli (Modal)", min_value=0)  # ✅ TAMBAHAN
        stok = st.number_input("Stok", min_value=0)
        desk = st.text_area("Deskripsi")
        img = st.file_uploader("Upload gambar")
        kode_promo = st.text_input("Kode Promo (opsional)")
        diskon = st.number_input("Diskon (%)", min_value=0, max_value=100)
        promo_aktif = st.checkbox("Aktifkan Promo")

        if st.button("Simpan", type="primary"):
            if not nama:
                st.error("Nama wajib diisi!")
            elif harga <= 0:
                st.error("Harga jual harus lebih dari 0!")
            elif harga_beli <= 0:
                st.error("Harga beli harus lebih dari 0!")
            else:
                url_img = upload_gambar(img)

                insert_produk({
                    "nama": nama,
                    "harga": harga,
                    "harga_beli": harga_beli,  # ✅ MASUKKAN KE DB
                    "stok": stok,
                    "deskripsi": desk,
                    "gambar": url_img,
                    "kode_promo": kode_promo.upper(),
                    "diskon": diskon,
                    "promo_aktif": promo_aktif
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
                    <div class="price">Jual: {rp(item['harga'])}</div>
                    <div class="price">Modal: {rp(item.get('harga_beli',0))}</div>
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
                harga_b = st.number_input("Harga Jual", value=item['harga'], key="h"+id_str)
                harga_beli_b = st.number_input(
                    "Harga Beli",
                    value=item.get("harga_beli", 0),
                    key="hb"+id_str
                )  # ✅ TAMBAHAN
                stok_b = st.number_input("Stok", value=item['stok'], key="s"+id_str)
                desk_b = st.text_area("Desk", item.get('deskripsi',''), key="x"+id_str)
                img_b = st.file_uploader("Ganti gambar", key="i"+id_str)
                kode_b = st.text_input("Kode Promo", item.get("kode_promo",""), key="kp"+id_str)
                diskon_b = st.number_input("Diskon (%)", value=item.get("diskon",0), key="dk"+id_str)
                promo_b = st.checkbox("Promo Aktif", value=item.get("promo_aktif",False), key="pb"+id_str)

                if st.button("Update", key="u"+id_str, type="primary"):
                    if not nama_b:
                        st.error("Nama tidak boleh kosong!")
                    else:
                        url_img = item.get("gambar")
                        if img_b:
                            url_img = upload_gambar(img_b)

                        update_produk(item['id'], {
                            "nama": nama_b,
                            "harga": harga_b,
                            "harga_beli": harga_beli_b,  # ✅ UPDATE
                            "stok": stok_b,
                            "deskripsi": desk_b,
                            "gambar": url_img,
                            "kode_promo": kode_b.upper(),
                            "diskon": diskon_b,
                            "promo_aktif": promo_b
                        })

                        st.success("Berhasil update!")
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
# ================= ANALISA KEUANGAN =================
elif menu == "📈 Analisa Keuangan":

    st.subheader("📊 Analisa Keuangan")

    # ================= FILTER =================
    colf1, colf2 = st.columns(2)
    start = colf1.date_input("Dari Tanggal")
    end = colf2.date_input("Sampai Tanggal")

    # ================= DATA =================
    transaksi = supabase.table("pemesanan").select("*").execute().data
    detail = supabase.table("detail_pemesanan").select("*").execute().data
    produk = supabase.table("produk").select("*").execute().data
    pengeluaran = get_pengeluaran()

    df_trx = pd.DataFrame(transaksi) if transaksi else pd.DataFrame()
    df_detail = pd.DataFrame(detail) if detail else pd.DataFrame()
    df_produk = pd.DataFrame(produk) if produk else pd.DataFrame()
    df_pengeluaran = pd.DataFrame(pengeluaran) if pengeluaran else pd.DataFrame()

    # ================= FILTER TRANSAKSI =================
    if not df_trx.empty and 'tanggal' in df_trx.columns:
        df_trx['tanggal'] = pd.to_datetime(df_trx['tanggal'])
        df_trx = df_trx[
            (df_trx['tanggal'].dt.date >= start) &
            (df_trx['tanggal'].dt.date <= end)
        ]

    # ================= PENDAPATAN =================
    total_pendapatan = df_trx['total'].sum() if not df_trx.empty else 0

    # ================= MODAL (REAL) =================
    total_modal = 0

    if not df_detail.empty and not df_produk.empty and not df_trx.empty:

        # ambil transaksi sesuai filter
        valid_order = df_trx['id'].tolist()
        df_detail = df_detail[df_detail['order_id'].isin(valid_order)]

        # rapihin nama
        df_detail['produk'] = df_detail['produk'].astype(str).str.strip().str.lower()
        df_produk['nama'] = df_produk['nama'].astype(str).str.strip().str.lower()

        # merge
        df_merge = df_detail.merge(
            df_produk,
            left_on="produk",
            right_on="nama",
            how="left"
        )

        # hitung modal dari harga_beli
        if 'harga_beli' in df_merge.columns:
            df_merge['modal'] = df_merge['harga_beli'].fillna(0) * df_merge['jumlah']
            total_modal = df_merge['modal'].sum()
        else:
            st.error("❌ Kolom harga_beli belum ada di tabel produk!")

    # ================= PENGELUARAN =================
    total_pengeluaran = 0

    if not df_pengeluaran.empty and 'created_at' in df_pengeluaran.columns:
        df_pengeluaran['created_at'] = pd.to_datetime(df_pengeluaran['created_at'])

        df_pengeluaran = df_pengeluaran[
            (df_pengeluaran['created_at'].dt.date >= start) &
            (df_pengeluaran['created_at'].dt.date <= end)
        ]

        total_pengeluaran = df_pengeluaran['jumlah'].sum()

    # ================= LABA =================
    laba_bersih = total_pendapatan - total_modal - total_pengeluaran

    # ================= UI =================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Pendapatan", rp(total_pendapatan))
    col2.metric("📦 Modal", rp(total_modal))
    col3.metric("💸 Pengeluaran", rp(total_pengeluaran))
    col4.metric("📈 Laba Bersih", rp(laba_bersih))

    st.markdown("---")

    # ================= GRAFIK =================
    if not df_trx.empty:
        df_trx['hari'] = df_trx['tanggal'].dt.date
        df_harian = df_trx.groupby('hari')['total'].sum().reset_index()

        fig = px.line(df_harian, x="hari", y="total", title="Pendapatan Harian", markers=True)
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ================= GRAFIK RINGKASAN =================
    df_chart = pd.DataFrame({
        "Kategori": ["Pendapatan", "Modal", "Pengeluaran", "Laba"],
        "Jumlah": [total_pendapatan, total_modal, total_pengeluaran, laba_bersih]
    })

    fig2 = px.bar(df_chart, x="Kategori", y="Jumlah", text_auto=True)
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# ================= INFO =================
if total_pendapatan == 0:
    st.info("ℹ️ Belum ada pendapatan di periode ini. Pengeluaran akan membuat laba minus.")

# ================= INPUT PENGELUARAN =================
with st.expander("➕ Tambah Pengeluaran"):
    nama = st.text_input("Nama Pengeluaran")
    jumlah = st.number_input("Jumlah", min_value=0)

    if st.button("Simpan Pengeluaran", type="primary"):
        if not nama:
            st.error("Nama wajib diisi!")
        elif jumlah <= 0:
            st.error("Jumlah harus > 0!")
        else:
            # ⚠️ hanya warning, bukan blok
            if total_pendapatan == 0:
                st.warning("⚠️ Pendapatan masih 0. Laba akan minus!")

            supabase.table("pengeluaran").insert({
                "nama": nama,
                "jumlah": jumlah
            }).execute()

            st.success("Berhasil ditambahkan!")
            st.rerun()

# ================= DATA =================
if not df_pengeluaran.empty:
    st.markdown("### 📋 Data Pengeluaran")
    st.dataframe(df_pengeluaran, use_container_width=True)

# ================= EXPORT PDF =================
if st.button("📄 Export PDF"):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("LAPORAN KEUANGAN", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"Pendapatan: {rp(total_pendapatan)}", styles["Normal"]),
        Paragraph(f"Modal: {rp(total_modal)}", styles["Normal"]),
        Paragraph(f"Pengeluaran: {rp(total_pengeluaran)}", styles["Normal"]),
        Paragraph(f"Laba Bersih: {rp(laba_bersih)}", styles["Normal"]),
    ]

    doc.build(content)

    st.download_button(
        "⬇️ Download PDF",
        buffer.getvalue(),
        file_name="laporan_keuangan.pdf"
    )
if st.button("🗑️ Reset Pengeluaran", type="secondary"):
    try:
        supabase.table("pengeluaran").delete().not_.is_("id", None).execute()
        st.success("✅ Semua pengeluaran berhasil dihapus!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Gagal reset: {e}")
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
