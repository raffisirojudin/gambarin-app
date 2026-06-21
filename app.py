"""
Gambarin - AI Image Generator & Editor
Streamlit app: generate dan edit gambar dari teks, 100% gratis,
menggunakan Pollinations.ai (Flux / Z-Image / Kontext).
"""

import base64
import random
import urllib.parse
from datetime import datetime

import requests
import streamlit as st

# ============================================================
# KONFIGURASI HALAMAN & KONSTANTA
# ============================================================
st.set_page_config(page_title="Gambarin", page_icon="🖌️", layout="centered")

APP_VERSION = "v1.0"
IMAGE_API_BASE = "https://image.pollinations.ai/prompt/"
EDITS_API_URL = "https://gen.pollinations.ai/v1/images/edits"
IMAGE_MIME_MAP = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}

BRUSHSTROKE_SVG = """
<div style="margin: 0.25rem 0 1.75rem 0;">
<svg width="100%" height="16" viewBox="0 0 600 16" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="brushGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D97A4D"/>
      <stop offset="100%" stop-color="#2B7A78"/>
    </linearGradient>
  </defs>
  <path d="M2,9 C60,3 120,14 180,7 C260,-1 340,15 420,6 C480,0 540,12 598,7"
        stroke="url(#brushGrad)" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.9"/>
</svg>
</div>
"""

STYLE_PRESETS = {
    "Default (tanpa gaya tambahan)": "",
    "Realistis": "photorealistic, highly detailed, professional photography, sharp focus",
    "Kartun": "cartoon style, vibrant colors, clean line art, playful",
    "Anime": "anime style, Japanese animation art, vibrant colors, detailed",
    "Watercolor": "watercolor painting style, soft brush strokes, artistic, flowing colors",
    "Cyberpunk": "cyberpunk style, neon lights, futuristic city, dramatic lighting",
    "Lukisan Klasik": "classical oil painting style, renaissance art, masterpiece, museum quality",
    "Sketsa Pensil": "pencil sketch, black and white, hand-drawn line art, detailed shading",
}

SIZE_PRESETS = {
    "Persegi (1024x1024)": (1024, 1024),
    "Potret (768x1024)": (768, 1024),
    "Lanskap (1024x768)": (1024, 768),
}

MODEL_PRESETS = {
    "Flux (gratis selamanya)": "flux",
    "Z-Image (alternatif gaya)": "zimage",
}

VARIATION_OPTIONS = [1, 2, 4]

EXAMPLE_PROMPTS = [
    "kucing oranye duduk di jendela sambil melihat hujan turun",
    "kota futuristik di malam hari dengan lampu neon menyala",
    "pegunungan bersalju saat matahari terbenam, langit jingga",
    "robot kecil sedang merawat tanaman di taman ajaib",
    "kedai kopi tradisional Jepang dengan suasana hangat",
    "naga berwarna biru terbang di atas lautan awan",
    "perpustakaan tua dengan rak buku menjulang tinggi dan cahaya matahari",
    "astronot duduk santai di permukaan bulan sambil minum teh",
    "rumah pohon kecil di tengah hutan yang dipenuhi kunang-kunang",
    "pasar tradisional yang ramai saat pagi hari, penuh warna",
]


def set_random_prompt():
    st.session_state["prompt_input"] = random.choice(EXAMPLE_PROMPTS)


# ============================================================
# PROTEKSI PASSWORD (opsional -- aktif kalau APP_PASSWORD diisi di Secrets)
# ============================================================
def get_app_password():
    try:
        return st.secrets["APP_PASSWORD"]
    except Exception:
        return None


_app_password = get_app_password()
if _app_password:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🖌️ Gambarin")
        st.caption("🔒 Aplikasi ini dilindungi password.")
        pwd_input = st.text_input("Masukkan password", type="password", key="app_password_gate")
        if st.button("Masuk", type="primary"):
            if pwd_input == _app_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password salah, coba lagi.")
        st.stop()


# ============================================================
# HEADER
# ============================================================
st.title("🖌️ Gambarin")
st.caption("Atelier digital — lukis apa saja dari kata-kata, sepenuhnya gratis.")
st.markdown(BRUSHSTROKE_SVG, unsafe_allow_html=True)

badge_col1, badge_col2, badge_col3 = st.columns(3)
with badge_col1:
    st.badge("Flux & Z-Image", icon="🖌️", color="orange")
with badge_col2:
    st.badge("Gratis $0", icon="🌿", color="green")
with badge_col3:
    st.badge(APP_VERSION, icon="🖼️", color="blue")

st.divider()


# ============================================================
# SESSION STATE
# ============================================================
def init_session_state():
    defaults = {"gallery": []}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()


def reset_all():
    keys_to_clear = [
        "gallery", "prompt_input", "style_choice", "size_choice",
        "model_choice", "variation_count", "last_batch",
        "own_photo_uploader", "own_photo_instruction", "own_photo_size", "last_own_edit",
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)


# ============================================================
# HELPER: API KEY & PEMANGGILAN POLLINATIONS
# ============================================================
def get_secret_pollinations_key():
    try:
        return st.secrets["POLLINATIONS_API_KEY"]
    except Exception:
        return None


def build_image_url(prompt, model, width, height, seed, reference_image_url=None):
    encoded_prompt = urllib.parse.quote(prompt)
    params = {"model": model, "width": width, "height": height, "seed": seed, "nologo": "true"}
    if reference_image_url:
        params["image"] = reference_image_url
    query = urllib.parse.urlencode(params)
    return f"{IMAGE_API_BASE}{encoded_prompt}?{query}"


def fetch_image(url, api_key=None):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    return response.content


def handle_image_error(e):
    msg = str(e)
    if "timeout" in msg.lower():
        st.error("⏳ Server gambar lambat merespons (timeout). Coba lagi sebentar.")
    elif "429" in msg:
        st.error("⏳ Terlalu banyak request. Tunggu sebentar lalu coba lagi.")
    elif "401" in msg or "403" in msg:
        st.error("🔑 API Key Pollinations tidak valid. Cek lagi di sidebar, atau hapus untuk pakai tanpa key.")
    else:
        st.error(f"Gagal memproses gambar: {msg}")


def edit_uploaded_image(image_bytes, filename, prompt, size, api_key):
    if not api_key:
        raise ValueError("Fitur ini butuh API Key Pollinations. Masukkan dulu di sidebar.")
    ext = filename.lower().split(".")[-1]
    mime_type = IMAGE_MIME_MAP.get(ext, "image/png")
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"image": (filename, image_bytes, mime_type)}
    data = {"prompt": prompt, "model": "kontext", "size": size}
    response = requests.post(EDITS_API_URL, headers=headers, files=files, data=data, timeout=120)
    response.raise_for_status()
    result = response.json()
    item = result["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    elif item.get("url"):
        img_response = requests.get(item["url"], timeout=60)
        img_response.raise_for_status()
        return img_response.content
    raise ValueError("Format respons API tidak dikenali.")


def add_to_gallery(prompt, model, width, height, seed, image_bytes, source_url, parent_prompt=None, parent_image_bytes=None):
    st.session_state.gallery.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "seed": seed,
        "image_bytes": image_bytes,
        "source_url": source_url,
        "parent_prompt": parent_prompt,
        "parent_image_bytes": parent_image_bytes,
    })


# ============================================================
# SIDEBAR
# ============================================================
secret_key = get_secret_pollinations_key()

with st.sidebar:
    st.markdown("### 🖌️ Gambarin")
    st.caption("Atelier Digital")
    st.divider()

    st.header("⚙️ Konfigurasi")
    if secret_key:
        pollinations_key = secret_key
        st.success("✅ API Key aktif (dari Secrets)")
    else:
        pollinations_key = st.text_input(
            "Pollinations API Key (opsional)",
            type="password",
            help="Bisa dikosongkan untuk pakai gratis tanpa key. Daftar gratis di enter.pollinations.ai untuk limit lebih tinggi & hilangkan watermark.",
        )
        st.markdown("[➜ Daftar API Key gratis (opsional)](https://enter.pollinations.ai)")
    st.caption("💰 Generate gambar di app ini selalu **$0**, tidak ada biaya per-gambar.")

    st.divider()
    st.button("🧹 Reset Semua", on_click=reset_all, use_container_width=True)


# ============================================================
# PILIH FITUR
# ============================================================
FEATURE_OPTIONS = ["🖌️ Generate Gambar", "📤 Edit Foto Sendiri", "🖼️ Galeri & Edit"]
selected_feature = st.selectbox("🧭 Pilih fitur", FEATURE_OPTIONS, key="feature_select")
st.divider()

# ---------- FITUR: GENERATE GAMBAR ----------
if selected_feature == "🖌️ Generate Gambar":
    st.button("🎲 Ide Acak", on_click=set_random_prompt, key="btn_random_prompt")
    prompt = st.text_area(
        "Deskripsikan gambar yang kamu mau",
        height=120,
        placeholder="Contoh: kucing oranye duduk di jendela sambil melihat hujan",
        key="prompt_input",
    )

    col1, col2 = st.columns(2)
    with col1:
        style_choice = st.selectbox("Gaya", list(STYLE_PRESETS.keys()), key="style_choice")
    with col2:
        size_choice = st.selectbox("Ukuran", list(SIZE_PRESETS.keys()), key="size_choice")

    col3, col4 = st.columns(2)
    with col3:
        model_choice = st.radio("Model", list(MODEL_PRESETS.keys()), key="model_choice")
    with col4:
        variation_count = st.radio("Jumlah variasi", VARIATION_OPTIONS, horizontal=True, key="variation_count")

    if st.button("🖌️ Buat Gambar", type="primary", use_container_width=True, key="btn_generate"):
        if not prompt.strip():
            st.warning("Tulis deskripsi gambar yang kamu mau terlebih dahulu.")
        else:
            style_suffix = STYLE_PRESETS[style_choice]
            full_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt
            width, height = SIZE_PRESETS[size_choice]
            model = MODEL_PRESETS[model_choice]

            generated_batch = []
            try:
                with st.spinner(f"Sedang membuat {variation_count} gambar... (bisa sampai 30 detik per gambar)"):
                    for _ in range(variation_count):
                        seed = random.randint(0, 999_999)
                        url = build_image_url(full_prompt, model, width, height, seed)
                        image_bytes = fetch_image(url, pollinations_key)
                        add_to_gallery(prompt, model, width, height, seed, image_bytes, url)
                        generated_batch.append(image_bytes)
                st.session_state.last_batch = generated_batch
            except Exception as e:
                handle_image_error(e)

    if st.session_state.get("last_batch"):
        batch = st.session_state.last_batch
        with st.container(border=True):
            st.subheader("🖼️ Hasil")
            cols = st.columns(len(batch))
            for idx, (col, img) in enumerate(zip(cols, batch)):
                with col:
                    st.image(img, use_container_width=True)
                    st.download_button(
                        "📥 Download" if len(batch) == 1 else f"📥 #{idx + 1}",
                        data=img,
                        file_name=f"gambarin_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx + 1}.jpg",
                        mime="image/jpeg",
                        key=f"dl_batch_{idx}",
                        use_container_width=True,
                    )

# ---------- FITUR: EDIT FOTO SENDIRI ----------
elif selected_feature == "📤 Edit Foto Sendiri":
    st.caption("Upload foto kamu sendiri, lalu beri instruksi buat mengubahnya dengan AI.")

    if not pollinations_key:
        st.warning(
            "⚠️ Fitur ini butuh API Key Pollinations (gratis, beda dari Generate Gambar biasa). "
            "Masukkan di sidebar, atau daftar di [enter.pollinations.ai](https://enter.pollinations.ai)."
        )

    uploaded_photo = st.file_uploader(
        "Upload foto (JPG/PNG/WEBP)", type=["jpg", "jpeg", "png", "webp"], key="own_photo_uploader"
    )
    if uploaded_photo:
        st.image(uploaded_photo, caption="Foto asli", use_container_width=True)

    edit_prompt = st.text_input(
        "Instruksi edit (contoh: 'ubah jadi gaya lukisan cat air', 'tambahkan salju di latar')",
        key="own_photo_instruction",
    )
    size_choice_own = st.selectbox("Ukuran hasil", list(SIZE_PRESETS.keys()), key="own_photo_size")

    if st.button("✨ Edit Foto", type="primary", use_container_width=True, key="btn_edit_own_photo"):
        if not pollinations_key:
            st.error("Masukkan API Key Pollinations di sidebar terlebih dahulu.")
        elif not uploaded_photo:
            st.warning("Upload foto terlebih dahulu.")
        elif not edit_prompt.strip():
            st.warning("Tulis instruksi edit terlebih dahulu.")
        else:
            width, height = SIZE_PRESETS[size_choice_own]
            try:
                with st.spinner("Sedang mengedit foto kamu..."):
                    original_bytes = uploaded_photo.getvalue()
                    edited_bytes = edit_uploaded_image(
                        original_bytes, uploaded_photo.name, edit_prompt,
                        size=f"{width}x{height}", api_key=pollinations_key,
                    )
                add_to_gallery(
                    edit_prompt, "kontext", width, height, "N/A", edited_bytes,
                    source_url=None, parent_prompt="(Foto upload sendiri)", parent_image_bytes=original_bytes,
                )
                st.session_state.last_own_edit = edited_bytes
            except Exception as e:
                handle_image_error(e)

    if st.session_state.get("last_own_edit"):
        with st.container(border=True):
            st.subheader("✨ Hasil Edit")
            st.image(st.session_state.last_own_edit, use_container_width=True)
            st.download_button(
                "📥 Download Hasil",
                data=st.session_state.last_own_edit,
                file_name=f"gambarin_edit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                mime="image/jpeg",
                key="dl_own_edit",
            )

# ---------- FITUR: GALERI & EDIT ----------
elif selected_feature == "🖼️ Galeri & Edit":
    st.caption("Semua gambar yang dibuat di sesi ini. Klik 'Edit' untuk mengubah gambar tertentu.")

    if not st.session_state.gallery:
        st.info("Belum ada gambar. Coba buat satu dulu di tab 'Generate Gambar'.")
    else:
        for i, item in enumerate(st.session_state.gallery):
            with st.container(border=True):
                if item.get("parent_image_bytes"):
                    col_before, col_after = st.columns(2)
                    with col_before:
                        st.image(item["parent_image_bytes"], caption="Sebelum", use_container_width=True)
                    with col_after:
                        st.image(item["image_bytes"], caption="Sesudah", use_container_width=True)
                else:
                    st.image(item["image_bytes"], use_container_width=True)

                label = item["prompt"][:80] + ("..." if len(item["prompt"]) > 80 else "")
                st.caption(f"🕒 {item['time']} · _{label}_")

                with st.expander("ℹ️ Info Detail"):
                    st.write(f"**Prompt:** {item['prompt']}")
                    st.write(f"**Model:** `{item['model']}`")
                    st.write(f"**Ukuran:** {item['width']} x {item['height']}")
                    st.write(f"**Seed:** {item['seed']}")
                    if item.get("parent_prompt"):
                        st.write(f"**Diedit dari prompt:** {item['parent_prompt']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "📥 Download",
                        data=item["image_bytes"],
                        file_name=f"gambarin_{i}.jpg",
                        mime="image/jpeg",
                        key=f"dl_gallery_{i}",
                        use_container_width=True,
                    )
                with col_b:
                    if item.get("source_url"):
                        edit_open = st.toggle("✏️ Edit gambar ini", key=f"edit_toggle_{i}")
                    else:
                        edit_open = False
                        st.caption("✏️ Edit lanjutan belum didukung untuk foto upload di sini.")

                if edit_open:
                    edit_instruction = st.text_input(
                        "Instruksi edit (contoh: 'ubah jadi malam hari', 'tambahkan topi merah')",
                        key=f"edit_instruction_{i}",
                    )
                    if st.button("✨ Terapkan Edit", key=f"btn_edit_{i}", use_container_width=True):
                        if not edit_instruction.strip():
                            st.warning("Tulis instruksi edit terlebih dahulu.")
                        else:
                            edit_seed = random.randint(0, 999_999)
                            edit_url = build_image_url(
                                edit_instruction, "kontext", item["width"], item["height"],
                                edit_seed, reference_image_url=item["source_url"],
                            )
                            try:
                                with st.spinner("Sedang mengedit gambar..."):
                                    edited_bytes = fetch_image(edit_url, pollinations_key)
                                add_to_gallery(
                                    edit_instruction, "kontext", item["width"], item["height"],
                                    edit_seed, edited_bytes, edit_url, parent_prompt=item["prompt"],
                                    parent_image_bytes=item["image_bytes"],
                                )
                                st.rerun()
                            except Exception as e:
                                handle_image_error(e)

        st.divider()
        if st.button("🗑️ Hapus Semua Gambar di Galeri", key="btn_clear_gallery"):
            st.session_state.gallery = []
            st.rerun()

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(f"🖌️ Gambarin {APP_VERSION} · Ditenagai Pollinations.ai (gratis) · Proyek pembelajaran AI API")
