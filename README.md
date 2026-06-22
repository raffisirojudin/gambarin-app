# Gambarin - AI Image Generator

Aplikasi web untuk generate gambar dari teks — **100% gratis, $0, tanpa pengecualian** — ditenagai [Pollinations.ai](https://pollinations.ai). Dibangun dengan Streamlit.

## Fitur

- 🎭 **Tema "Atelier Senja"** — identitas visual khas studio pelukis: latar netral hangat (aman buat gambar warna apapun), aksen terracotta-teal yang saling melengkapi, tipografi serif (Fraunces + Karla)
- 🎨 **Generate Gambar dari Teks** — pilih gaya (Realistis/Kartun/Anime/Watercolor/dll), ukuran, dan model (Flux / Z-Image)
- 🔀 **Variasi Gambar** — generate 1, 2, atau 4 variasi sekaligus dari prompt yang sama
- 💡 **Ide Acak** — tombol kasih prompt contoh random kalau lagi buntu ide
- 🖼️ **Galeri Sesi** — semua gambar yang dibuat tersimpan, bisa di-download atau dihapus, lengkap dengan info detail (prompt, model, seed, ukuran)
- 🔒 **Proteksi Password (opsional)** — set `APP_PASSWORD` di Secrets
- 📱 **Dropdown Navigasi** — ringkas dan mobile-friendly

## Kenapa gratis?

Aplikasi ini memakai model **Flux** dari [Pollinations.ai](https://pollinations.ai), yang menurut dokumentasi resmi mereka **gratis tanpa batas, selamanya**, tanpa API key wajib. Mendaftar API key (gratis, opsional) di [enter.pollinations.ai](https://enter.pollinations.ai) hanya menaikkan limit & menghilangkan watermark — bukan syarat wajib.

> **Catatan:** versi awal app ini sempat punya fitur edit gambar (model `kontext`), tapi ternyata model itu memakai sistem kredit "Pollen" berbayar — bukan gratis seperti Flux. Fitur edit dihapus supaya app ini benar-benar 100% gratis tanpa jebakan biaya tersembunyi.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. (Opsional) Daftar API Key gratis

Hanya diperlukan kalau mau limit lebih tinggi & tanpa watermark — generate gambar tetap berfungsi penuh tanpa ini.

1. Buka https://enter.pollinations.ai
2. Daftar gratis, salin API key-nya
3. Masukkan di sidebar app, atau simpan permanen lewat Secrets (lihat di bawah)

## 3. Simpan API Key & Password permanen (Secrets) — opsional

**Untuk lokal:** salin `.streamlit/secrets.toml.example` jadi `.streamlit/secrets.toml`, isi sesuai kebutuhan. Jangan upload file ini ke GitHub.

**Untuk Streamlit Cloud:** Settings → Secrets, isi:
```toml
POLLINATIONS_API_KEY = "key-kamu"
APP_PASSWORD = "password-kamu"
```
Keduanya opsional — app tetap berfungsi normal tanpa diisi.

## 4. Jalankan aplikasi

```bash
streamlit run app.py
```

## 5. Cara pakai

1. Pilih **🖌️ Generate Gambar** → tulis deskripsi (atau klik "Ide Acak"), pilih gaya, ukuran, model, dan jumlah variasi
2. Klik "Buat Gambar"
3. Pindah ke **🖼️ Galeri** untuk lihat semua gambar yang sudah dibuat, download, atau hapus

## Catatan teknis

- **Model**: `flux` (default — gratis tanpa batas selamanya) dan `zimage` (alternatif gaya)
- **Determinisme**: setiap gambar pakai `seed` acak yang disimpan dan ditampilkan di Info Detail
- **Galeri hanya tersimpan selama sesi browser aktif** (`st.session_state`) — refresh halaman akan menghapusnya
- Tidak ada token/cost tracker di app ini karena memang **tidak ada biaya** — beda dengan SummaRise yang pakai Gemini API
