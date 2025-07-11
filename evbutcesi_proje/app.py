import streamlit as st
import pandas as pd
import pyodbc
import datetime
import plotly.express as px

# SQL Server bağlantısı
conn = pyodbc.connect(
    'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=homeproject;Trusted_Connection=yes;'
)

st.title("💰 Ev Bütçesi Takip Paneli")

# Kullanıcı verileri
kullanicilar = pd.read_sql("SELECT * FROM Kullanicilar", conn)
st.subheader("👥 Kullanıcılar")
st.dataframe(kullanicilar)

# Gelirler
gelirler = pd.read_sql("SELECT * FROM Gelirler", conn)
st.subheader("📈 Gelirler")
st.dataframe(gelirler)

# Giderler
giderler = pd.read_sql("SELECT * FROM Giderler", conn)
st.subheader("📉 Giderler")
st.dataframe(giderler)

# Net Durum
netdurum = pd.read_sql("""
    SELECT ku.Ad, ku.Soyad,
    ISNULL(gelirler.ToplamGelir, 0) - ISNULL(giderler.ToplamGider, 0) AS NetDurum
    FROM Kullanicilar ku
    LEFT JOIN (
        SELECT KullaniciID, SUM(Tutar) AS ToplamGelir
        FROM Gelirler
        GROUP BY KullaniciID
    ) AS gelirler ON ku.KullaniciID = gelirler.KullaniciID
    LEFT JOIN (
        SELECT KullaniciID, SUM(Tutar) AS ToplamGider
        FROM Giderler
        GROUP BY KullaniciID
    ) AS giderler ON ku.KullaniciID = giderler.KullaniciID;
""", conn)
st.subheader("💸 Net Durum")
st.dataframe(netdurum)


# Loglar
loglar = pd.read_sql("SELECT * FROM LogTablosu ORDER BY Tarih DESC", conn)
st.subheader("📝 Log Mesajları")
st.dataframe(loglar)

# ➕ Yeni Kayıt Ekle
st.header("➕ Yeni Kayıt Ekle")

secim = st.radio("Ne eklemek istersin?", ["Gelir", "Gider"])
kullanici_id = st.number_input("Kullanıcı ID", min_value=1)
tutar = st.number_input("Tutar", min_value=0.0, format="%.2f")
tarih = st.date_input("Tarih")
aciklama = st.text_input("Açıklama")
if secim == "Gider":
    kategori_id = st.number_input("Kategori ID", min_value=1)

if st.button("Kaydı Ekle"):
    cursor = conn.cursor()
    tarih_str = tarih.strftime('%Y-%m-%d')
    tutar_float = float(tutar)
    kullanici_id_int = int(kullanici_id)
    if secim == "Gelir":
        cursor.execute(
            "INSERT INTO Gelirler (KullaniciID, Tutar, Tarih, Aciklama) VALUES (?, ?, ?, ?)",
            (kullanici_id_int, tutar_float, tarih_str, aciklama)
        )
    else:
        kategori_id_int = int(kategori_id)
        cursor.execute(
            "INSERT INTO Giderler (KullaniciID, KategoriID, Tutar, Tarih, Aciklama) VALUES (?, ?, ?, ?, ?)",
            (kullanici_id_int, kategori_id_int, tutar_float, tarih_str, aciklama)
        )
    conn.commit()
    st.success(f"{secim} başarıyla eklendi!")
    st.experimental_rerun()

# 📅 Aylık Gider Grafiği
gider_aylik = pd.read_sql("""
    SELECT CONVERT(VARCHAR(7), Tarih, 120) AS Ay, SUM(Tutar) AS ToplamGider
    FROM Giderler
    GROUP BY CONVERT(VARCHAR(7), Tarih, 120)
    ORDER BY Ay
""", conn)
st.subheader("📅 Aylık Gider Grafiği")
fig1 = px.bar(gider_aylik, x='Ay', y='ToplamGider', title='Aylık Toplam Giderler')
st.plotly_chart(fig1)

# 🍰 Kategori Bazlı Harcama Dağılımı
kategori_gider = pd.read_sql("""
    SELECT k.KategoriAdi, SUM(g.Tutar) AS ToplamGider
    FROM Giderler g
    INNER JOIN Kategoriler k ON g.KategoriID = k.KategoriID
    GROUP BY k.KategoriAdi
""", conn)
st.subheader("🍰 Kategori Bazlı Harcama Dağılımı")
fig2 = px.pie(kategori_gider, names='KategoriAdi', values='ToplamGider', title='Harcama Dağılımı (Kategori)')
st.plotly_chart(fig2)

# ⚖️ Kullanıcı Gelir-Gider Karşılaştırma
gelir_gider = pd.read_sql("""
    SELECT ku.Ad,
        ISNULL(gelir.ToplamGelir,0) AS ToplamGelir,
        ISNULL(gider.ToplamGider,0) AS ToplamGider
    FROM Kullanicilar ku
    LEFT JOIN (
        SELECT KullaniciID, SUM(Tutar) AS ToplamGelir
        FROM Gelirler
        GROUP BY KullaniciID
    ) gelir ON ku.KullaniciID = gelir.KullaniciID
    LEFT JOIN (
        SELECT KullaniciID, SUM(Tutar) AS ToplamGider
        FROM Giderler
        GROUP BY KullaniciID
    ) gider ON ku.KullaniciID = gider.KullaniciID
""", conn)
st.subheader("⚖️ Kullanıcı Gelir-Gider Karşılaştırma")
fig3 = px.bar(gelir_gider, x='Ad', y=['ToplamGelir', 'ToplamGider'], barmode='group', title='Gelir vs Gider')
st.plotly_chart(fig3)

