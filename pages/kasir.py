import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid
import pandas as pd
import streamlit.components.v1 as components

# === TAMBAHAN PDF ===
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO

# ================= PROTEKSI LOGIN =================
if "login" not in st.session_state or not st.session_state.login:
    st.switch_page("pages/login.py")

# ================= PROTEKSI ROLE =================
if st.session_state.get("role") != "kasir":
    st.error("Akses ditolak")
    st.stop()

# ================= SUPABASE =================
url = "https://ukgzplcpupucrlalkafs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrZ3pwbGNwdXB1Y3JsYWxrYWZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3MDA0MzUsImV4cCI6MjA5MDI3NjQzNX0.8ugnFoGqW71PbP4PRtp1UUTznhh3iJjRuwQrFgbP_Qw"
supabase = create_client(url, key)
st.markdown("""
<style>
div[role="radiogroup"] input:checked + div {
    background: rgba(124,58,237,0.2);
    border-left: 4px solid #a78bfa;
    border-radius: 8px;
    color: white !important;
    padding: 10px 14px;
}
</style>
""", unsafe_allow_html=True)
# ================= HELPER =================
def rp(x):
    return f"Rp {x:,.0f}".replace(",", ".")

# 🔥 TAMBAHAN: AMBIL NAMA KASIR DARI AKUN
def get_nama_kasir():
    user_id = st.session_state.get("user_id")

    if not user_id:
        return "KASIR"

    data = supabase.table("akun") \
        .select("username") \
        .eq("id_akun", user_id) \
        .execute().data

    if data:
        return data[0]["username"]

    return "KASIR"


def generate_struk_html(order_id, nama, items, total, bayar, kembali):
    item_text = ""

    for i in items:
        item_text += f"""
        {i['nama']}<br>
        {i['qty']} x {rp(i['harga'])}<br>
        = {rp(i['subtotal'])}<br><br>
        """

    html = f"""
    <div style="
        width: 280px;
        font-family: monospace;
        font-size: 12px;
        padding: 10px;
        border: 1px dashed #000;
    ">
        <center>
            <b>TOKO UBI ARDYELA</b><br>
            ----------------------<br>
            STRUK PEMBELIAN<br>
        </center>

        ID: {order_id[:8]}<br>
        Nama Kasir: {nama}<br>
        ----------------------<br>

        {item_text}

        ----------------------<br>
        TOTAL   : {rp(total)}<br>
        BAYAR   : {rp(bayar)}<br>
        KEMBALI : {rp(kembali)}<br>

        ----------------------<br>
        <center>TERIMA KASIH</center>
    </div>
    """
    return html

# === PDF (TIDAK DIUBAH) ===
def generate_pdf(order_id, nama, items, total, bayar, kembali):
    buffer = BytesIO()

    width = 58 * mm
    height = 300 * mm

    c = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 10

    c.setFont("Courier", 8)

    def draw(text):
        nonlocal y
        c.drawString(5, y, str(text))
        y -= 10

    draw("TOKO UBI ARDYELA")
    draw("STRUK PEMBELIAN")
    draw("----------------------")
    draw(f"ID: {order_id[:8]}")
    draw(f"Kasir: {nama}")
    draw("----------------------")

    for i in items:
        draw(i['nama'])
        draw(f"{i['qty']} x {rp(i['harga'])}")
        draw(f"= {rp(i['subtotal'])}")

    draw("----------------------")
    draw(f"TOTAL: {rp(total)}")
    draw(f"BAYAR: {rp(bayar)}")
    draw(f"KEMBALI: {rp(kembali)}")
    draw("TERIMA KASIH")

    c.save()
    buffer.seek(0)
    return buffer

# ================= DATABASE =================
def get_produk():
    return supabase.table("produk").select("*").execute().data

def get_laporan():
    return supabase.table("pemesanan").select("*").execute().data

def insert_order(order_id, nama, total):
    supabase.table("pemesanan").insert({
        "id": order_id,
        "nama_kasir": nama,
        "total": total,
        "tanggal": datetime.now().isoformat()
    }).execute()

def insert_detail(data):
    supabase.table("detail_pemesanan").insert(data).execute()

def update_stok(id, stok):
    supabase.table("produk").update({"stok": stok}).eq("id", id).execute()

# ================= SESSION =================
if "cart" not in st.session_state:
    st.session_state.cart = []

# ================= CSS PREMIUM (TIDAK DIUBAH) =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1e1b4b, #6d28d9, #c4b5fd);
}
section[data-testid="stSidebar"] {
    background: rgba(30, 27, 75, 0.95);
    backdrop-filter: blur(10px);
}
[data-testid="stSidebarNav"] {
    display: none;
}
.card {
    display: flex;
    gap: 12px;
    align-items: center;
    background: rgba(6, 182, 212, 0.22);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.15);
}
.total {
    font-size: 20px;
    font-weight: bold;
    color: #34d399;
}
/* Khusus elemen Streamlit */
h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}
.stButton button[kind="primary"] {
    background: linear-gradient(45deg, #10b981, #34d399);
    color: white !important;
    border-radius: 10px;
}
.stButton button[kind="secondary"] {
    background: linear-gradient(45deg, #ef4444, #dc2626);
    color: white !important;
    border-radius: 10px;
}
div.stButton > button {
    display: block;
    margin: 0 auto;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<h1 style='color:white;text-align:center;'>🍠 KASIR TOKO UBI ARDYELA</h1>", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.markdown("<h2 style='color:white;text-align:center;'>🍠 MENU</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio("", ["🛒 Kasir", "📊 Laporan"])

st.sidebar.markdown("---")

col1, col2, col3 = st.sidebar.columns([1,2,1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

if st.sidebar.button("🧹 Reset Keranjang"):
    st.session_state.cart = []

# ================= KASIR =================
if menu == "🛒 Kasir":

    st.subheader("Transaksi")

    produk_list = get_produk()

    nama = get_nama_kasir()
    st.info(f"Kasir: {nama}")

    def format_produk(x):
        stok = x['stok']
        if stok <= 0:
            status = "🔴 OUT"
        elif stok <= 10:
            status = "🟡"
        else:
            status = "🟢"
        return f"{status} {x['nama']} (Stok: {stok})"

    produk = st.selectbox("Pilih Produk", produk_list, format_func=format_produk)

    qty = st.number_input("Jumlah", min_value=1)

    if st.button("➕ Tambah ke Keranjang", type="primary"):

        produk_db = supabase.table("produk").select("*").eq("id", produk['id']).execute().data
        produk_db = produk_db[0]

        stok_terbaru = produk_db["stok"]

        if stok_terbaru <= 0:
            st.error("❌ Stok habis!")
            st.stop()

        if qty > stok_terbaru:
            st.error("❌ Stok tidak cukup!")
            st.stop()

        st.session_state.cart.append({
            "id": produk_db['id'],
            "nama": produk_db['nama'],
            "harga": int(produk_db['harga']),
            "qty": int(qty),
            "subtotal": int(produk_db['harga']) * int(qty),
            "stok": stok_terbaru,
            "kode_promo": produk_db.get("kode_promo"),
            "diskon": produk_db.get("diskon", 0),
            "promo_aktif": produk_db.get("promo_aktif", False)
        })

        st.success("Berhasil ditambahkan!")

    st.subheader("🛍️ Keranjang")

    kode_input = st.text_input("🎟️ Kode Promo")

    total = 0
    diskon = 0

    for i, item in enumerate(st.session_state.cart):
        total += int(item['subtotal'])

        st.markdown(f"""
        <div class="card">
            <div>
                <b style="color:white;">{item['nama']}</b><br>
                <span style="color:#c4b5fd;">{item['qty']}x</span><br>
                <span style="color:#34d399;">{rp(item['subtotal'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"❌ Hapus {item['nama']}", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    # ================= CEK PROMO =================
    if kode_input:
        for item in st.session_state.cart:
            if (
                item.get("kode_promo")
                and item.get("promo_aktif")
                and item.get("kode_promo").upper() == kode_input.upper()
            ):
                diskon = int(item.get("diskon", 0))
                break

    st.markdown(f"<div class='total'>Total: {rp(total)}</div>", unsafe_allow_html=True)

    if diskon > 0:
        st.success(f"🎉 Promo {diskon}% aktif!")
    elif kode_input:
        st.error("❌ Kode promo tidak valid")

    total_akhir = int(total - (total * diskon / 100))

    st.markdown(f"<div class='total'>Total Setelah Diskon: {rp(total_akhir)}</div>", unsafe_allow_html=True)

    bayar = st.number_input("Bayar", min_value=0)

    kembali = bayar - total_akhir if bayar >= total_akhir else 0

    if bayar >= total_akhir and total > 0:
        st.success(f"Kembalian: {rp(kembali)}")

# ================= SIMPAN =================
if st.button("💾 Simpan Transaksi", type="primary"):

    try:
        order_id = str(uuid.uuid4())

        # 🔥 simpan ke pemesanan (pakai total_akhir)
        insert_order(order_id, nama, total_akhir)

        # 🔥 simpan detail
        for item in st.session_state.cart:
            insert_detail({
                "order_id": order_id,
                "produk": item['nama'],
                "harga": int(item['harga']),
                "jumlah": int(item['qty']),
                "subtotal": int(item['subtotal'])
            })

            update_stok(item['id'], item['stok'] - item['qty'])

        st.success("Transaksi berhasil!")

        # ================= STRUK =================
        struk_html = generate_struk_html(
            order_id,
            nama,
            st.session_state.cart,
            total,
            bayar,
            kembali
        )

        print_block = f"""
        <div id="printArea">{struk_html}</div>

        <button onclick="window.print()">PRINT</button>

        <style>
        @media print {{
            body * {{ visibility: hidden; }}
            #printArea, #printArea * {{ visibility: visible; }}
        }}
        </style>
        """

        st.components.v1.html(print_block, height=500)

        pdf = generate_pdf(order_id, nama, st.session_state.cart, total, bayar, kembali)

        st.download_button(
            "Download PDF",
            data=pdf,
            file_name=f"struk_{order_id[:8]}.pdf",
            mime="application/pdf"
        )

        # 🔥 reset cart
        st.session_state.cart = []
    except Exception as e:
        st.error(f"❌ Gagal simpan: {e}")
        st.stop()
# ================= LAPORAN =================
else:

    st.subheader("📊 Riwayat Transaksi Saya")

    data = get_laporan()

    if data:
        df = pd.DataFrame(data)

        # 🔥 FILTER SESUAI KASIR LOGIN
        nama_login = get_nama_kasir()
        df = df[df['nama_kasir'] == nama_login]

        # ================= FORMAT TANGGAL =================
        df['tanggal'] = pd.to_datetime(df['tanggal'])

        # ================= HITUNG WAKTU (AUTO RESET) =================
        today = pd.Timestamp.now()

        # 🔥 HARI INI
        hari_ini = df[df['tanggal'].dt.date == today.date()]

        # 🔥 MINGGU INI (Senin - Minggu)
        start_minggu = today - pd.Timedelta(days=today.weekday())
        end_minggu = start_minggu + pd.Timedelta(days=6)

        minggu_ini = df[
            (df['tanggal'] >= start_minggu) &
            (df['tanggal'] <= end_minggu)
        ]

        # 🔥 BULAN INI
        bulan_ini = df[
            (df['tanggal'].dt.month == today.month) &
            (df['tanggal'].dt.year == today.year)
        ]

        # 🔥 TAHUN INI
        tahun_ini = df[df['tanggal'].dt.year == today.year]

        # ================= TOTAL =================
        total_hari = hari_ini['total'].sum()
        total_minggu = minggu_ini['total'].sum()
        total_bulan = bulan_ini['total'].sum()
        total_tahun = tahun_ini['total'].sum()

        # ================= TAMPILKAN STAT =================
        st.markdown("### 💰 Statistik Pendapatan")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Hari Ini", rp(total_hari))
        col2.metric("Minggu Ini", rp(total_minggu))
        col3.metric("Bulan Ini", rp(total_bulan))
        col4.metric("Tahun Ini", rp(total_tahun))

        # ================= AMBIL DETAIL =================
        detail = supabase.table("detail_pemesanan").select("*").execute().data
        df_detail = pd.DataFrame(detail)

        st.info(f"Menampilkan transaksi kasir: {nama_login}")

        # ================= SEARCH =================
        search_id = st.text_input("Cari ID Transaksi")

        st.markdown("### 🧾 Data Transaksi")

        # ================= LOOP =================
        for _, row in df.iterrows():

            # 🔎 SEARCH ID
            if search_id and search_id not in str(row['id']):
                continue

            detail_transaksi = df_detail[df_detail['order_id'] == row['id']]

            with st.expander(
                f"🧾 ID: {row['id'][:8]} | 💰 {rp(row['total'])}"
            ):

                st.write({
                    "Tanggal": row.get("tanggal"),
                    "Total": rp(row.get("total", 0)),
                    "Kasir": row.get("nama_kasir")
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
        st.download_button("⬇️ Download CSV", csv, "riwayat_saya.csv")

    else:
        st.info("Belum ada transaksi")
