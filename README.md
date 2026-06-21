# Gambarin - AI Image Generator & Editor

Aplikasi web untuk generate dan edit gambar dari teks — **100% gratis, $0**, ditenagai [Pollinations.ai](https://pollinations.ai). Dibangun dengan Streamlit.

## Fitur

- 🎨 **Generate Gambar dari Teks** — pilih gaya (Realistis/Kartun/Anime/Watercolor/dll), ukuran, dan model (Flux / Z-Image)
- ✏️ **Edit Gambar** — ubah gambar yang sudah dibuat dengan instruksi teks (model Kontext), misal "ubah jadi malam hari"
- 🖼️ **Galeri Sesi** — semua gambar yang dibuat tersimpan, bisa di-download atau dihapus
- 🔒 **Proteksi Password (opsional)** — set `APP_PASSWORD` di Secrets
- 📱 **Dropdown Navigasi** — ringkas dan mobile-friendly

## Kenapa gratis?

Aplikasi ini memakai [Pollinations.ai](https://pollinations.ai), platform open-source yang menyediakan akses gratis ke model gambar (Flux, Z-Image, Kontext) tanpa API key wajib. Mendaftar API key (gratis, opsional) di [enter.pollinations.ai](https://enter.pollinations.ai) hanya menaikkan limit & menghilangkan watermark — bukan syarat wajib.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. (Opsional) Daftar API Key gratis

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
Keduanya opsional — app tetap berfungsi normal tanpa diisi (tanpa proteksi password, dan tanpa key memakai limit gratis standar).

## 4. Jalankan aplikasi

```bash
streamlit run app.py
```

## 5. Cara pakai

1. Pilih **🎨 Generate Gambar** → tulis deskripsi, pilih gaya & ukuran, klik "Buat Gambar"
2. Pindah ke **🖼️ Galeri & Edit** → lihat semua gambar, klik "✏️ Edit gambar ini" untuk transformasi lebih lanjut, atau download

## Catatan teknis

- **Model**: `flux` (default — satu-satunya model yang dijamin gratis selamanya oleh Pollinations) dan `zimage` (alternatif gaya) untuk generate; `kontext` untuk edit gambar berbasis instruksi
- ⚠️ Fitur **Edit Gambar** memakai model `kontext`, yang **belum dipastikan gratis tanpa batas** seperti Flux. Kalau bikin API key di Pollinations, batasi budget-nya ke angka kecil (misal 1-2 Pollen) sebagai jaring pengaman.
- **Determinisme**: setiap gambar pakai `seed` acak yang disimpan, supaya gambar yang sama bisa di-edit ulang secara konsisten
- **Galeri hanya tersimpan selama sesi browser aktif** (`st.session_state`) — refresh halaman akan menghapusnya
- Tidak ada token/cost tracker di app ini karena memang **tidak ada biaya** — beda dengan SummaRise yang pakai Gemini API
