import json
import base64
import requests
import streamlit as st # type: ignore
import streamlit.components.v1 as components
import time
from PIL import Image
from datetime import datetime
import io

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="Quản Lý Hoa Hội",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS GỐC VÀ CSS GRID FIX MOBILE ---
st.markdown(
    """
    <style>
    /* CSS GRID FIX MOBILE - ÉP 3 CỘT */
    .grid-force {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 10px;
    }
    @media (max-width: 600px) {
        .grid-force {
            grid-template-columns: repeat(3, 1fr) !important;
        }
    }
    .hoa-item {
        text-align: center;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 5px;
        background: rgba(255,255,255,0.05);
    }
    /* Các style cũ của bạn */
    div[class*="viewerBadge"], [data-testid="stToolbar"], [data-testid="stHeader"], #MainMenu, footer { display:none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- CÁC HÀM TIỆN ÍCH ---
def anh_html(data):
    if not data: return ""
    if isinstance(data, bytes): return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    return data

def background_image(file):
    try:
        with open(file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            st.markdown(f"<style>.stApp {{ background-image: url('data:image/png;base64,{data}'); background-size: cover; background-attachment: fixed; }}</style>", unsafe_allow_html=True)
    except: pass

def sap_xep_hoa(ds_hoa):
    thu_tu_cap = {"Đỏ": 1, "Cam": 2, "Tím": 3, "Xanh dương": 4, "Xanh lá": 5}
    return sorted(ds_hoa, key=lambda ten: thu_tu_cap.get(st.session_state.kho_hoa_tong.get(ten, {}).get("cap", ""), 99))

# --- CẤU HÌNH GITHUB ---
MAT_KHAU_HE_THONG = "111111"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"] if "GITHUB_TOKEN" in st.secrets else ""
REPO_NAME = "annocuoi/test12"
FILE_PATH = "du_lieu_chung.json"
BRANCH = "main"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

# --- HÀM SYNC GITHUB (GIỮ NGUYÊN) ---
def tai_du_lieu_tu_github():
    # ... (Hàm này giữ nguyên logic cũ của bạn) ...
    mac_dinh = {"kho_hoa_tong": {}, "tai_khoan": {}}
    try:
        url_doc = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}&t={time.time()}"
        headers_doc = {"Accept": "application/vnd.github.v3.raw", "Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url_doc, headers=headers_doc, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            for ten_hoa in data.get("kho_hoa_tong", {}):
                if data["kho_hoa_tong"][ten_hoa].get("anh"):
                    try: data["kho_hoa_tong"][ten_hoa]["anh"] = base64.b64decode(data["kho_hoa_tong"][ten_hoa]["anh"].encode("utf-8"))
                    except: data["kho_hoa_tong"][ten_hoa]["anh"] = None
            return data
    except: pass
    return mac_dinh

# --- PHẦN LOGIN (GIỮ NGUYÊN) ---
if "da_dang_nhap" not in st.session_state: st.session_state.da_dang_nhap = False
if not st.session_state.da_dang_nhap:
    ten_dang_nhap = st.text_input("Tài khoản")
    mat_khau_nhap = st.text_input("Mật khẩu", type="password")
    if st.button("🔐 Đăng Nhập"):
        # ... (Logic đăng nhập của bạn) ...
        st.rerun()
    st.stop()

# [SAU ĐÂY LÀ PHẦN TABS - TÌM TAB CẤP NHANH VÀ SỬA]
# ... (Phần logic các tab của bạn) ...

# --- SỬA ĐỔI TẠI ĐÂY: tab_cap_nhanh ---
with tab_cap_nhanh:
    st.markdown("## 🪷 Cấp Hoa Cho Hội Viên")
    danh_sach_tv = [x for x in du_lieu_hoi_dang_dung.keys() if not x.startswith("_")]
    tv_chon = st.selectbox("👤 Chọn hội viên", ["-- Chọn --"] + danh_sach_tv, key="chon_tv_cap_nhanh")

    if tv_chon != "-- Chọn --":
        danh_sach_hoa = [h for h in st.session_state.kho_hoa_tong.keys() if h not in du_lieu_hoi_dang_dung.get(tv_chon, [])]
        
        # SỬ DỤNG CSS GRID MỚI - KHÔNG DÙNG ST.COLUMNS
        with st.form(key="form_cap_hoa"):
            st.markdown('<div class="grid-force">', unsafe_allow_html=True)
            hoa_chon = []
            for hoa in danh_sach_hoa:
                info = st.session_state.kho_hoa_tong.get(hoa, {})
                link = anh_html(info.get("anh"))
                
                st.markdown(f'''
                <div class="hoa-item">
                    <img src="{link}" style="width:100%; border-radius:5px;">
                    <div style="font-size:10px; font-weight:bold; margin-top:4px;">{hoa}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.checkbox("Chọn", key=f"cap_{tv_chon}_{hoa}"):
                    hoa_chon.append(hoa)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.form_submit_button("🌺 Hoàn thành cấp hoa"):
                if not hoa_chon: st.warning("⚠️ Chưa chọn!")
                else:
                    for h in hoa_chon:
                        if h not in du_lieu_hoi_dang_dung[tv_chon]: du_lieu_hoi_dang_dung[tv_chon].append(h)
                    if luu_du_lieu():
                        st.success("✅ Thành công!")
                        st.rerun()
    else:
        st.info("👆 Chọn hội viên để cấp hoa")
