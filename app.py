import json
import base64
import requests
import streamlit as st # type: ignore
import streamlit.components.v1 as components
import time
from PIL import Image
from datetime import datetime
import io
from streamlit_local_storage import LocalStorage

# Cấu hình giao diện ứng dụng
st.set_page_config(
    page_title="Quản Lý Hoa Hội",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)
storage = LocalStorage()

st.markdown(
    """
    <style>
    div[class*="viewerBadge"] { display:none !important; }
    div[style*="bottom: 0"], div[style*="bottom:0"] { display:none !important; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.35) !important;
        border-radius:12px !important;
    }
    div[data-baseweb="select"] input { background: transparent !important; caret-color: transparent !important; }
    div[data-baseweb="select"] span { background: transparent !important; }
    
    .title-hoi {
        display:flex; justify-content:center; align-items:center; gap:10px;
        font-size:clamp(22px, 6vw, 38px); font-weight:900; color:#000000; white-space:nowrap;
    }
    div[data-testid="stElementToolbar"] { display: none; }
    .title-hoi span { white-space:nowrap; }
    
    div[role="option"], div[role="option"] *, ul[role="listbox"] *, [data-baseweb="popover"] * {
        color:#000000 !important; font-weight:700 !important;
    }
    div[role="option"] { background:white !important; }
    input, textarea { color:#000000 !important; font-weight:700 !important; }
    input::placeholder { color:#555555 !important; }
    
    button[data-baseweb="tab"] *, button[data-baseweb="tab"] p { color:#111111 !important; }
    [data-testid="stRadio"] * { color:#111111 !important; }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color:#000 !important; }
    
    h1, h2, h3, h4 { color:#1e293b !important; font-weight:900 !important; text-shadow: 1px 1px 3px white; }
    button[data-baseweb="tab"] p { color:#111827 !important; font-weight:800; }
    [data-testid="stMetricValue"] { color:#000000 !important; font-weight:900; }
    .flower-name { color:#000 !important; font-weight:900; text-shadow:1px 1px 2px white; }
    button { color:#111827 !important; font-weight:700 !important; }
    div[data-baseweb="select"] * { color:black !important; }
    
    .block-container { background: transparent !important; }
    div[data-testid="stVerticalBlock"] { background: transparent !important; }
    button[data-baseweb="tab"] { background: rgba(255,255,255,0.15); border-radius: 15px; color: white; }
    input { background: rgba(255,255,255,0.9)!important; color:black!important; border-radius:12px!important; }
    div[data-baseweb="select"] { background:white; border-radius:12px; }
    </style>
    """,
    unsafe_allow_html=True
)

GRID_STYLE = """
<style>
html, body{ overflow-x:hidden; max-width:100%; }
.flower-grid{
    display:grid; grid-template-columns:repeat(auto-fit, minmax(80px, 1fr));
    gap:18px; width:100%; max-width:100%; overflow-x:hidden; padding-right:15px; box-sizing:border-box;
}
.flower-box{ text-align:center; }
.flower-box img{
    width:75px; height:75px; object-fit:cover; border-radius:10px; padding:3px; box-shadow:0 3px 8px rgba(0,0,0,.3);
}
.flower-box img.cap-do{ border:5px solid #ef4444; }
.flower-box img.cap-tim{ border:5px solid #c084fc; }
.flower-box img.cap-xanh-la{ border:5px solid #22c55e; }
.flower-box img.cap-xanh-duong{ border:5px solid #38bdf8; }
.flower-box img.cap-cam{ border:5px solid #f59e0b; }
.flower-name{ font-size:13px; font-weight:bold; margin-top:5px; }
</style>
"""

def anh_html(data):
    """Xử lý chuẩn hóa dữ liệu ảnh ra link src Base64 cho thẻ HTML img"""
    if not data:
        return ""
    if isinstance(data, bytes):
        img64 = base64.b64encode(data).decode('utf-8')
    elif isinstance(data, str):
        if data.startswith("data:image"):
            return data
        elif data.startswith("b'") or data.startswith('b"'):
            img64 = data[2:-1]
        else:
            img64 = data
    else:
        return ""
    return f"data:image/jpeg;base64,{img64}"

def background_image(file):
    try:
        with open(file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{data}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            .block-container {{ background: rgba(255,255,255,0.75); border-radius:20px; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        pass

background_image("nen.jpg")

def sap_xep_hoa(ds_hoa, kho_hoa_su_dung):
    thu_tu_cap = {"Đỏ": 1, "Cam": 2, "Tím": 3, "Xanh dương": 4, "Xanh lá": 5}
    return sorted(
        ds_hoa,
        key=lambda ten: thu_tu_cap.get(
            kho_hoa_su_dung.get(ten, {}).get("cap", ""), 99
        )
    )

# ====================================================
# ⚙️ CẤU HÌNH HỆ THỐNG
# ====================================================
MAT_KHAU_HE_THONG = "111111"

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except Exception:
    GITHUB_TOKEN = ""

REPO_NAME = "annocuoi/test12"
FILE_PATH = "du_lieu_chung.json"
BRANCH = "main"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

# ====================================================
# 📂 HÀM ĐỌC DỮ LIỆU TỪ GITHUB
# ====================================================
def tai_du_lieu_tu_github():
    mac_dinh = {"kho_hoa_tong": {}, "tai_khoan": {}}
    try:
        url_doc = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}&t={time.time()}"
        headers_doc = {"Accept": "application/vnd.github.v3.raw"}
        if GITHUB_TOKEN:
            headers_doc["Authorization"] = f"token {GITHUB_TOKEN}"
            
        response = requests.get(url_doc, headers=headers_doc, timeout=10)
        if response.status_code == 200:
            chuoi_thong_tin = response.text.strip()
            if not chuoi_thong_tin or chuoi_thong_tin in ['""', '{}']:
                return mac_dinh
            return json.loads(chuoi_thong_tin)
    except Exception as e:
        st.sidebar.warning(f"Đang kết nối đám mây... ({str(e)})")
    return mac_dinh

# ==========================
# KHỞI TẠO SESSION & DỮ LIỆU
# ==========================
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "ten_tai_khoan" not in st.session_state:
    st.session_state.ten_tai_khoan = ""

if "quyen" not in st.session_state:
    st.session_state.quyen = None

if "da_load_data" not in st.session_state:
    du_lieu_goc = tai_du_lieu_tu_github()
    st.session_state.kho_hoa_tong = du_lieu_goc.get("kho_hoa_tong", {})
    st.session_state.tai_khoan = du_lieu_goc.get("tai_khoan", {})

    if "admin" not in st.session_state.tai_khoan:
        st.session_state.tai_khoan["admin"] = {
            "pass": MAT_KHAU_HE_THONG,
            "quyen": "admin",
            "ngay_tao": datetime.now().strftime("%d/%m/%Y")
        }

    st.session_state.da_load_data = True

def tao_ten_file_hoi(ten_hoi):
    ten = ten_hoi.lower().replace(" ", "_")
    return f"hoi/{ten}.json"

def doc_du_lieu_hoi(ten_hoi):
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{tao_ten_file_hoi(ten_hoi)}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            noi_dung = r.json()["content"].replace("\n", "")
            return json.loads(base64.b64decode(noi_dung).decode("utf-8"))
        return {}
    except Exception:
        return {}

# ==========================
# GIAO DIỆN ĐĂNG NHẬP
# ==========================
if not st.session_state.da_dang_nhap:
    st.markdown(
        """
        <div style='text-align:center; margin-top:30px; margin-bottom:25px;'>
            <div style='font-size:clamp(24px,5vw,42px); font-weight:900; white-space:nowrap;'>🌸 QUẢN LÝ HOA HỘI 🌸</div>
            <div style='font-size:clamp(12px,3vw,18px); font-weight:700; white-space:nowrap;'>🌺 Bộ sưu tập • Hội viên • Xếp hạng 🌺</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    tk_luu = storage.getItem("nho_tai_khoan_login") or ""
    mk_luu = storage.getItem("nho_mat_khau_login") or ""
    
    ten_dang_nhap = st.text_input("Tài khoản", value=tk_luu, placeholder="Nhập tài khoản..")
    mat_khau_nhap = st.text_input("Mật khẩu", value=mk_luu, type="password", placeholder="Nhập mật khẩu...")
    
    tick_luu = storage.getItem("nho_tick_login")
    tick_mac_dinh = True if tick_luu == "1" else False

    nho_dang_nhap = st.checkbox("💾 Nhớ tài khoản và mật khẩu", value=tick_mac_dinh)

    if st.button("🔐 Đăng Nhập", use_container_width=True):
        dang_nhap_ok = False
        quyen_login = None
        chu_so_huu = None

        if (
            ten_dang_nhap in st.session_state.tai_khoan
            and mat_khau_nhap == st.session_state.tai_khoan[ten_dang_nhap].get("pass")
        ):
            info_login = st.session_state.tai_khoan[ten_dang_nhap]
            if info_login.get("trang_thai", "hoat_dong") == "khoa":
                st.error("⛔ Tài khoản đã ngưng hoạt động")
                st.stop()

            dang_nhap_ok = True
            quyen_login = info_login["quyen"]
        else:
            for ten_hoi, info in st.session_state.tai_khoan.items():
                if info.get("quyen") != "hoi" or info.get("trang_thai", "hoat_dong") == "khoa":
                    continue
                data_hoi = doc_du_lieu_hoi(ten_hoi)
                tk_xem = data_hoi.get("_tai_khoan_xem", {})

                if (
                    ten_dang_nhap == tk_xem.get("user")
                    and mat_khau_nhap == tk_xem.get("pass")
                ):
                    dang_nhap_ok = True
                    quyen_login = "xem"
                    chu_so_huu = ten_hoi
                    st.session_state.hoi_dang_xem = ten_hoi
                    break

        if dang_nhap_ok:
            if nho_dang_nhap:
                storage.setItem("nho_tick_login", "1", key="luu_tick_login")
                storage.setItem("nho_tai_khoan_login", ten_dang_nhap, key="luu_tk_login")
                storage.setItem("nho_mat_khau_login", mat_khau_nhap, key="luu_mk_login")
            else:
                storage.setItem("nho_tick_login", "0", key="bo_tick_login")
                try:
                    if storage.getItem("nho_tai_khoan_login"):
                        storage.deleteItem("nho_tai_khoan_login", key="xoa_tk_login")
                    if storage.getItem("nho_mat_khau_login"):
                        storage.deleteItem("nho_mat_khau_login", key="xoa_mk_login")
                except Exception:
                    pass

            time.sleep(0.5)

            st.session_state.da_dang_nhap = True
            st.session_state.quyen = quyen_login

            if quyen_login == "xem":
                st.session_state.ten_tai_khoan = chu_so_huu
                st.session_state.chu_so_huu = chu_so_huu
            else:
                st.session_state.ten_tai_khoan = ten_dang_nhap
                st.session_state.chu_so_huu = None

            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu")

    st.stop()

# ==========================
# NÚT ĐĂNG XUẤT
# ==========================
col_title, col_logout = st.columns([8, 2])
with col_logout:
    if st.button("🚪 Đăng xuất", type="secondary", use_container_width=True):
        st.session_state.da_dang_nhap = False
        st.session_state.ten_tai_khoan = ""
        st.session_state.quyen = None
        if "du_lieu_hoi" in st.session_state:
            del st.session_state.du_lieu_hoi
        if "hoi_dang_mo" in st.session_state:
            del st.session_state.hoi_dang_mo
        st.rerun()

# ----------------------------------------------------
# 💾 HÀM CHUẨN HÓA VÀ LƯU DỮ LIỆU
# ----------------------------------------------------
def chuan_hoa_data_hoi(data):
    import copy
    data_copy = copy.deepcopy(data)
    kho_rieng = data_copy.get("_kho_hoa_rieng", {})
    for ten_hoa, info in kho_rieng.items():
        if info.get("anh") and isinstance(info["anh"], bytes):
            info["anh"] = base64.b64encode(info["anh"]).decode("utf-8")
    return data_copy

def luu_du_lieu_len_github():
    if not GITHUB_TOKEN:
        st.error("Chưa cấu hình GITHUB_TOKEN!")
        return False

    try:
        kho_tong_copy = {}
        for ten_hoa, info in st.session_state.kho_hoa_tong.items():
            if info.get("anh") and isinstance(info["anh"], bytes):
                anh_str = base64.b64encode(info["anh"]).decode("utf-8")
            else:
                anh_str = info.get("anh")
                
            kho_tong_copy[ten_hoa] = {
                "cap": info["cap"],
                "anh": anh_str
            }

        data_to_save = {
            "kho_hoa_tong": kho_tong_copy,
            "tai_khoan": st.session_state.tai_khoan
        }
        
        json_str = json.dumps(data_to_save, ensure_ascii=False, indent=4)
        content_b64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": "Cập nhật dữ liệu từ ứng dụng Quản Lý Hoa",
            "content": content_b64,
            "branch": BRANCH
        }
        
        get_sha_res = requests.get(API_URL, headers=HEADERS, timeout=5)
        if get_sha_res.status_code == 200:
            payload["sha"] = get_sha_res.json()["sha"]
            
        response = requests.put(API_URL, headers=HEADERS, json=payload, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"Lỗi mạng: {str(e)}")
        return False

def luu_du_lieu_hoi(ten_hoi, data):
    try:
        file_path = tao_ten_file_hoi(ten_hoi)
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
        get_file = requests.get(url, headers=HEADERS, timeout=5)

        data_save = chuan_hoa_data_hoi(data)

        payload = {
            "message": f"Luu hoi {ten_hoi}",
            "content": base64.b64encode(json.dumps(data_save, ensure_ascii=False).encode()).decode()
        }

        if get_file.status_code == 200:
            payload["sha"] = get_file.json()["sha"]

        res = requests.put(url, headers=HEADERS, json=payload, timeout=10)
        if res.status_code in [200, 201]:
            return True

        if res.status_code == 409:
            time.sleep(1)
            return luu_du_lieu_hoi(ten_hoi, data)

        st.error(f"Lỗi lưu hội: {res.status_code}")
        return False
    except Exception as e:
        st.error(str(e))
        return False

def luu_du_lieu():
    if st.session_state.quyen == "admin":
        return luu_du_lieu_len_github()
    elif st.session_state.quyen == "hoi":
        return luu_du_lieu_hoi(
            st.session_state.ten_tai_khoan,
            st.session_state.du_lieu_hoi
        )
    return False

# ==============================
# CHỌN DATA SAU KHI ĐĂNG NHẬP
# ==============================
if st.session_state.quyen == "admin":
    du_lieu_hoi_dang_dung = {}
    kho_hoa_kha_dung = st.session_state.kho_hoa_tong
elif st.session_state.quyen in ["hoi", "xem"]:
    ten = st.session_state.ten_tai_khoan if st.session_state.quyen == "hoi" else st.session_state.chu_so_huu
    if "du_lieu_hoi" not in st.session_state or st.session_state.get("hoi_dang_mo") != ten:
        st.session_state.du_lieu_hoi = doc_du_lieu_hoi(ten)
        st.session_state.hoi_dang_mo = ten
    du_lieu_hoi_dang_dung = st.session_state.du_lieu_hoi
    
    kho_hoa_kha_dung = st.session_state.kho_hoa_tong.copy()
    kho_hoa_kha_dung.update(du_lieu_hoi_dang_dung.get("_kho_hoa_rieng", {}))

ten_hien_thi = "TÊN HỘI"
if st.session_state.quyen == "hoi":
    ten_goc = st.session_state.ten_tai_khoan
elif st.session_state.quyen == "xem":
    ten_goc = st.session_state.chu_so_huu
else:
    ten_goc = None

if ten_goc and ten_goc in st.session_state.tai_khoan:
    ten_hien_thi = st.session_state.tai_khoan[ten_goc].get("ten_hien_thi", ten_goc)

st.markdown(
    f"""
    <div class="title-hoi">
        <span>🌸</span>
        <span>{ten_hien_thi.upper()}</span>
        <span>🌸</span>
    </div>
    """,
    unsafe_allow_html=True
)

du_lieu_dem = {
    k: v for k, v in du_lieu_hoi_dang_dung.items()
    if not k.startswith("_")
}

tong_hoa_hoi_vien = sum(len(hoa) for hoa in du_lieu_dem.values())
tong_hoi_vien = len(du_lieu_dem)

components.html(
    f"""
    <div style="display:flex; justify-content:center; align-items:center; gap:80px; margin-top:10px; margin-bottom:0px;">
        <div style="text-align:center;">
            <div style="font-size:15px;">🌸 Tổng Hoa Hội Viên</div>
            <div style="font-size:28px;font-weight:bold;">{tong_hoa_hoi_vien}</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:15px;">👥 Hội viên</div>
            <div style="font-size:28px;font-weight:bold;">{tong_hoi_vien}</div>
        </div>
    </div>
    """,
    height=75
)

st.write("---")

# ====================================================
# ĐIỀU HƯỚNG TAB THEO QUYỀN
# ====================================================
if st.session_state.quyen == "admin":
    tab_kho, tab_khach, tab_kiem_soat = st.tabs(["📦 Kho", "👥 Khách hàng", "📊 Kiểm soát"])
elif st.session_state.quyen == "hoi":
    tab_suu_tap, tab_hoi_vien, tab_xep_hang, tab_thong_tin, tab_tai_khoan_xem = st.tabs(
        ["🌸 Bộ sưu tập", "👥 Hội viên", "🏆 Xếp hạng", "ℹ️ Thông tin", "🔑 TK xem"]
    )
elif st.session_state.quyen == "xem":
    tab_suu_tap, tab_xep_hang, tab_thong_tin = st.tabs(["🌸 Bộ sưu tập", "🏆 Xếp hạng", "ℹ️ Thông tin"])

# ====================================================
# KHU VỰC 1: QUẢN LÝ KHO HOA TỔNG (ADMIN)
# ====================================================
if st.session_state.quyen == "admin":    
    with tab_kho:
        st.markdown("<h3 style='font-size: 18px;'>📦 Kho Hoa Chung (Admin)</h3>", unsafe_allow_html=True)
        col_kho1 = st.container()
        col_kho2 = st.container()
        
        with col_kho1:
            with st.expander("➕ Thêm hoa mới vào Kho Chung", expanded=False):
                if "key_them_hoa" not in st.session_state:
                    st.session_state.key_them_hoa = 0
                
                ten_hoa_moi = st.text_input(
                    "Tên hoa",
                    placeholder="Nhập tên hoa...",
                    key=f"txt_ten_hoa_moi_{st.session_state.key_them_hoa}"
                )
                cap_bac_moi = st.selectbox(
                    "Cấp bậc",
                    options=["Xanh lá", "Xanh dương", "Tím", "Cam", "Đỏ"],
                    key="sl_cap_bac_moi"
                )
                file_anh = st.file_uploader(
                    "Tải ảnh",
                    type=["png", "jpg", "jpeg"],
                    key=f"f_file_anh_{st.session_state.key_them_hoa}"
                )
        
                if st.button("📥 Thêm vào Kho Chung", use_container_width=True):
                    ten_hoa_clean = ten_hoa_moi.strip()
        
                    if not ten_hoa_clean:
                        st.error("Vui lòng nhập tên!")
                    elif ten_hoa_clean in st.session_state.kho_hoa_tong:
                        st.warning("Đã tồn tại!")
                    else:
                        du_lieu_anh = None
                        if file_anh is not None:
                            try:
                                img = Image.open(file_anh)
                                if img.mode != "RGB":
                                    img = img.convert("RGB")
                                img.thumbnail((300, 300))
                                buffer = io.BytesIO()
                                img.save(buffer, format="JPEG", quality=70)
                                du_lieu_anh = base64.b64encode(buffer.getvalue()).decode('utf-8')
                            except Exception:
                                du_lieu_anh = base64.b64encode(file_anh.read()).decode('utf-8')
        
                        st.session_state.kho_hoa_tong[ten_hoa_clean] = {
                            "cap": cap_bac_moi,
                            "anh": du_lieu_anh
                        }
        
                        if luu_du_lieu():
                            st.session_state.key_them_hoa += 1
                            st.rerun()
        
        with col_kho2:
            st.markdown("<p style='font-size:14px;font-weight:bold;'>📋 Danh sách hoa chung</p>", unsafe_allow_html=True)
            if not st.session_state.kho_hoa_tong:
                st.markdown("<p style='font-size:12px;color:gray;'>Kho đang trống.</p>", unsafe_allow_html=True)
            else:
                ds_tim_hoa = ["-- Chọn --"] + list(st.session_state.kho_hoa_tong.keys())
                tim_hoa = st.selectbox("🔍 Tìm hoa", ds_tim_hoa, key="tim_hoa_kho")
            
                dem_cap = {"Đỏ": 0, "Cam": 0, "Tím": 0, "Xanh dương": 0, "Xanh lá": 0}
                for ten_hoa, info in st.session_state.kho_hoa_tong.items():
                    cap = info.get("cap", "")
                    if cap in dem_cap:
                        dem_cap[cap] += 1

                tong_hoa = sum(dem_cap.values())

                def reset_tim_hoa():
                    st.session_state.tim_hoa_kho = "-- Chọn --"

                loc_cap = st.radio(
                    "Lọc cấp",
                    [
                        f"🌈 Tất cả: {tong_hoa}",
                        f"🔴 Đỏ: {dem_cap['Đỏ']}",
                        f"🟠 Cam: {dem_cap['Cam']}",
                        f"🟣 Tím: {dem_cap['Tím']}",
                        f"🔵 Xanh dương: {dem_cap['Xanh dương']}",
                        f"🟢 Xanh lá: {dem_cap['Xanh lá']}",
                    ],
                    horizontal=True,
                    key="loc_cap_kho",
                    on_change=reset_tim_hoa
                )

                loc_cap_clean = (
                    loc_cap.split(":")[0]
                    .replace("🌈 ", "").replace("🔴 ", "").replace("🟠 ", "")
                    .replace("🟣 ", "").replace("🔵 ", "").replace("🟢 ", "")
                )
            
                danh_sach_loc = {}
                for ten_hoa, info in st.session_state.kho_hoa_tong.items():
                    if tim_hoa != "-- Chọn --" and tim_hoa != ten_hoa:
                        continue
                    if loc_cap_clean != "Tất cả" and info["cap"] != loc_cap_clean:
                        continue
                    danh_sach_loc[ten_hoa] = info
            
                if not danh_sach_loc:
                    st.info("Không tìm thấy hoa.")
                else:
                    html = '<div class="flower-grid">'
                    for ten_hoa in sap_xep_hoa(danh_sach_loc.keys(), st.session_state.kho_hoa_tong):
                        info = danh_sach_loc[ten_hoa]
                        mau_cap = {
                            "Xanh lá": "cap-xanh-la",
                            "Xanh dương": "cap-xanh-duong",
                            "Tím": "cap-tim",
                            "Cam": "cap-cam",
                            "Đỏ": "cap-do"
                        }.get(info["cap"], "cap-do")

                        link_anh = anh_html(info.get("anh"))
                        html += f"""
                        <div class="flower-box">
                            <img class="{mau_cap}" src="{link_anh}">
                            <div class="flower-name">{ten_hoa}</div>
                        </div>
                        """
                    html += "</div>"
            
                    components.html(GRID_STYLE + html, height=450, scrolling=True)

# ====================================================
# KHU VỰC 2: CẤU HÌNH THÀNH VIÊN VÀ CẤP PHÁT (HỘI)
# ====================================================
if st.session_state.quyen == "hoi":
    with tab_hoi_vien:
        tab_cap_phat, tab_cap_nhanh, tab_ds_tv, tab_kho_rieng = st.tabs(
            ["👥 Hội viên", "🌸 Cấp nhanh hoa", "📋 Danh sách hội viên", "🌺 Thêm Hoa Mới (Kho Riêng)"]
        )
        
        with tab_kho_rieng:
            st.markdown("## 🌺 Thêm Hoa Mới Vào Kho Riêng Của Hội")
            st.info("💡 Hoa do Hội thêm ở đây sẽ thuộc về kho riêng của Hội này, không ảnh hưởng đến các Hội khác.")
            
            if "_kho_hoa_rieng" not in du_lieu_hoi_dang_dung:
                du_lieu_hoi_dang_dung["_kho_hoa_rieng"] = {}
                
            if "key_them_hoa_hoi" not in st.session_state:
                st.session_state.key_them_hoa_hoi = 0
                
            ten_hoa_hoi = st.text_input(
                "Tên hoa mới",
                placeholder="Nhập tên hoa mới...",
                key=f"txt_ten_hoa_hoi_{st.session_state.key_them_hoa_hoi}"
            )
            cap_hoa_hoi = st.selectbox(
                "Cấp bậc",
                options=["Xanh lá", "Xanh dương", "Tím", "Cam", "Đỏ"],
                key="sl_cap_hoa_hoi"
            )
            file_anh_hoi = st.file_uploader(
                "Hình ảnh hoa",
                type=["png", "jpg", "jpeg"],
                key=f"f_anh_hoi_{st.session_state.key_them_hoa_hoi}"
            )
            
            if st.button("📥 Thêm vào Kho riêng của Hội", use_container_width=True):
                ten_clean = ten_hoa_hoi.strip()
                if not ten_clean:
                    st.error("Vui lòng nhập tên hoa!")
                elif ten_clean in kho_hoa_kha_dung:
                    st.warning("Hoa này đã tồn tại trong kho chung hoặc kho riêng!")
                else:
                    data_anh = None
                    if file_anh_hoi is not None:
                        try:
                            img = Image.open(file_anh_hoi)
                            if img.mode != "RGB":
                                img = img.convert("RGB")
                            img.thumbnail((300, 300))
                            buffer = io.BytesIO()
                            img.save(buffer, format="JPEG", quality=70)
                            data_anh = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        except Exception:
                            data_anh = base64.b64encode(file_anh_hoi.read()).decode('utf-8')
                            
                    du_lieu_hoi_dang_dung["_kho_hoa_rieng"][ten_clean] = {
                        "cap": cap_hoa_hoi,
                        "anh": data_anh
                    }
                    
                    if luu_du_lieu():
                        st.session_state.key_them_hoa_hoi += 1
                        st.success(f"✅ Đã thêm '{ten_clean}' vào kho riêng thành công!")
                        st.rerun()

        with tab_cap_phat:
            st.markdown("## 👥 Thêm + Xóa Hội Viên")
            col_tv1 = st.container()
            with col_tv1:
                with st.expander("➕ Quản lý hội viên", expanded=False):
                    if "key_them_tv" not in st.session_state:
                        st.session_state.key_them_tv = 0
                    
                    ten_tv_moi = st.text_input(
                        "➕ Nhập hội viên mới",
                        placeholder="Nhập tên...",
                        key=f"them_thanh_vien_{st.session_state.key_them_tv}"
                    )
                    
                    if st.button("➕ Thêm hội viên", use_container_width=True):
                        ten_tv_clean = ten_tv_moi.strip()
                        if ten_tv_clean == "":
                            st.warning("⚠️ Vui lòng nhập tên hội viên")
                        elif ten_tv_clean.lower() in [x.lower() for x in du_lieu_hoi_dang_dung.keys()]:
                            st.error("❌ Hội viên đã tồn tại")
                        else:
                            du_lieu_hoi_dang_dung[ten_tv_clean] = []
                            if luu_du_lieu():
                                st.session_state.key_them_tv += 1
                                st.success("✅ Đã thêm hội viên")
                                st.rerun()

                    danh_sach_tv_that = [x for x in du_lieu_hoi_dang_dung.keys() if not x.startswith("_")]
                    tv_xoa = st.selectbox("🗑 Xóa hội viên", ["-- Chọn --"] + danh_sach_tv_that, key="xoa_tv")

                    if st.button("❌ Xóa", use_container_width=True):
                        if tv_xoa != "-- Chọn --":
                            del du_lieu_hoi_dang_dung[tv_xoa]
                            if luu_du_lieu():
                                st.rerun()

        with tab_cap_nhanh:
            st.markdown("## 🪷 Cấp Hoa Cho Hội Viên")
            danh_sach_tv_cn = [x for x in du_lieu_hoi_dang_dung.keys() if not x.startswith("_")]

            tv_chon = st.selectbox("👤 Chọn hội viên", ["-- Chọn --"] + danh_sach_tv_cn, key="chon_tv_cap_nhanh")
            
            if "tv_chon_cu" not in st.session_state:
                st.session_state.tv_chon_cu = tv_chon

            if st.session_state.tv_chon_cu != tv_chon:
                st.session_state.hoa_dang_chon = []
                st.session_state.tv_chon_cu = tv_chon
                st.rerun()

            if tv_chon != "-- Chọn --":
                hoa_da_co = du_lieu_hoi_dang_dung.get(tv_chon, [])
                danh_sach_hoa_goc = [
                    hoa for hoa in kho_hoa_kha_dung.keys()
                    if hoa not in hoa_da_co
                ]

                st.markdown("""
                <div style="font-size:22px; font-weight:700; color:#222; margin-top:0; margin-bottom:6px;">
                🌈 Chọn màu hoa để hiển thị danh sách
                </div>
                """, unsafe_allow_html=True)
                
                mau_chon = st.radio(
                    "",
                    ["🔴 Đỏ", "🟠 Cam", "🟣 Tím", "🔵 Xanh dương", "🟢 Xanh lá"],
                    horizontal=True,
                    index=0,
                    label_visibility="collapsed",
                    key="loc_mau_cap_hoa"
                )
                
                danh_sach_hoa = danh_sach_hoa_goc.copy()

                if mau_chon:
                    ten_mau = (
                        mau_chon
                        .replace("🔴 ", "").replace("🟠 ", "").replace("🟣 ", "")
                        .replace("🔵 ", "").replace("🟢 ", "")
                    )
                    danh_sach_hoa = [
                        hoa for hoa in danh_sach_hoa
                        if kho_hoa_kha_dung.get(hoa, {}).get("cap") == ten_mau
                    ]

                    tim_hoa = st.text_input("🔍 Tìm hoa", placeholder="Nhập tên hoa...", key="tim_hoa_cap_nhanh")
                    if tim_hoa.strip():
                        danh_sach_hoa = [
                            hoa for hoa in danh_sach_hoa
                            if tim_hoa.lower().strip() in hoa.lower()
                        ]

                cot1, cot2 = st.columns(2)
                with cot1:
                    bam_hoan_thanh = st.button("🌺 Hoàn thành", use_container_width=True, key="hoan_thanh_tren")
                with cot2:
                    bo_chon_tat_ca = st.button("❎ Bỏ chọn", use_container_width=True, key="bo_chon_tat_ca")

                st.markdown("### 🌸 Chọn hoa")
                thong_bao = st.empty()

                if "thong_bao" in st.session_state:
                    thong_bao.success(st.session_state.thong_bao)
                    del st.session_state.thong_bao

                if bo_chon_tat_ca:
                    st.session_state.hoa_dang_chon = []
                    for hoa in danh_sach_hoa:
                        key = f"capnhanh_{tv_chon}_{hoa}"
                        if key in st.session_state:
                            st.session_state[key] = False
                    st.rerun()

                with st.container(height=650):
                    cols = st.columns(4)
                    if "hoa_dang_chon" not in st.session_state:
                        st.session_state.hoa_dang_chon = []

                    for i, hoa in enumerate(danh_sach_hoa):
                        with cols[i % 4]:
                            thong_tin = kho_hoa_kha_dung.get(hoa, {})
                            cap = thong_tin.get("cap")
                            mau_chu = {
                                "Đỏ": "#d60000",
                                "Cam": "#ff6600",
                                "Tím": "#8e44ad",
                                "Xanh dương": "#005eff",
                                "Xanh lá": "#009900"
                            }.get(cap, "black")

                            tick = st.checkbox(
                                "",
                                value=hoa in st.session_state.hoa_dang_chon,
                                key=f"capnhanh_{tv_chon}_{hoa}"
                            )

                            st.markdown(
                                f"""
                                <div style="margin-top:-42px; margin-left:35px; color:{mau_chu}; font-weight:700; font-size:16px; white-space:nowrap; height:35px;">
                                    {hoa}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            if tick and hoa not in st.session_state.hoa_dang_chon:
                                st.session_state.hoa_dang_chon.append(hoa)
                            elif not tick and hoa in st.session_state.hoa_dang_chon:
                                st.session_state.hoa_dang_chon.remove(hoa)

                if bam_hoan_thanh:
                    if not st.session_state.hoa_dang_chon:
                        thong_bao.warning("⚠️ Chưa chọn hoa")
                    else:
                        for hoa in st.session_state.hoa_dang_chon:
                            if hoa not in du_lieu_hoi_dang_dung[tv_chon]:
                                du_lieu_hoi_dang_dung[tv_chon].append(hoa)

                        if luu_du_lieu():
                            so_hoa = len(st.session_state.hoa_dang_chon)
                            st.session_state.thong_bao = f"✅ Đã thêm {so_hoa} hoa cho {tv_chon}"
                            st.session_state.hoa_dang_chon = []
                            for k in list(st.session_state.keys()):
                                if k.startswith("capnhanh_"):
                                    del st.session_state[k]
                            st.rerun()
            else:
                st.info("👆 Chọn hội viên để cấp hoa")

        with tab_ds_tv:
            st.markdown("## 📋 Danh sách hội viên")
            danh_sach_tv_tab = [tv for tv in du_lieu_hoi_dang_dung.keys() if not tv.startswith("_")]
            st.info(f"👥 Tổng hội viên: {len(danh_sach_tv_tab)}")

            bang_tv = []
            for ten_tv, ds_hoa in du_lieu_hoi_dang_dung.items():
                if ten_tv.startswith("_"):
                    continue

                dem = {"Đỏ": 0, "Cam": 0, "Tím": 0, "Xanh dương": 0, "Xanh lá": 0}
                for hoa in ds_hoa:
                    thong_tin = kho_hoa_kha_dung.get(hoa, {})
                    mau = thong_tin.get("mau") or thong_tin.get("cap")
                    if mau in dem:
                        dem[mau] += 1

                tong = sum(dem.values())
                bang_tv.append({
                    "👤 Hội viên": ten_tv,
                    "🌸 Tổng": tong,
                    "🔴 Đỏ": dem["Đỏ"],
                    "🟠 Cam": dem["Cam"],
                    "🟣 Tím": dem["Tím"],
                    "🔵 Xanh dương": dem["Xanh dương"],
                    "🟢 Xanh lá": dem["Xanh lá"]
                })

            bang_tv = sorted(bang_tv, key=lambda x: x["🌸 Tổng"], reverse=True)
            st.dataframe(bang_tv, hide_index=True, use_container_width=True)

# ====================================================
# KHU VỰC: BẢNG XẾP HẠNG (HỘI / XEM)
# ====================================================
if st.session_state.quyen != "admin":
    with tab_xep_hang:
        st.markdown(
            """
            <div style="text-align:center;white-space:nowrap;margin-bottom:15px;">
                <div style="font-size:40px;line-height:1;">🏆</div>
                <div style="font-size:22px;font-weight:700;">Bảng Xếp Hạng Hội Viên</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        bang_xep_hang = []
        for ten_tv, ds_hoa in du_lieu_hoi_dang_dung.items():
            if ten_tv.startswith("_"):
                continue

            dem = {"Đỏ": 0, "Cam": 0, "Tím": 0, "Xanh dương": 0, "Xanh lá": 0}
            for hoa in ds_hoa:
                info = kho_hoa_kha_dung.get(hoa, {})
                cap = info.get("cap", "")
                if cap in dem:
                    dem[cap] += 1

            bang_xep_hang.append({
                "ten": ten_tv,
                "tong": len(ds_hoa),
                "cap": dem
            })

        bang_xep_hang.sort(
            key=lambda x: (
                x["tong"],
                x["cap"]["Đỏ"],
                x["cap"]["Cam"],
                x["cap"]["Tím"],
                x["cap"]["Xanh dương"],
                x["cap"]["Xanh lá"]
            ),
            reverse=True
        )

        hang_xep = [bang_xep_hang[:1]] if bang_xep_hang else []
        for i in range(1, len(bang_xep_hang), 2):
            hang_xep.append(bang_xep_hang[i:i+2])

        html = ""
        so_top = 1

        for hang in hang_xep:
            cot = len(hang)
            html += f'<div style="display:grid; grid-template-columns:repeat({cot},150px); justify-content:center; gap:12px; margin-bottom:6px;">'

            for tv in hang:
                if so_top == 1:
                    cup, vien, do_day_vien = "🥇", "#ffd700", "5px"
                elif so_top == 2:
                    cup, vien, do_day_vien = "🥈", "#c0c0c0", "4px"
                elif so_top == 3:
                    cup, vien, do_day_vien = "🥉", "#cd7f32", "4px"
                else:
                    cup, vien, do_day_vien = f"#{so_top}", "white", "2px"

                html += f"""
                <div style="border:{do_day_vien} solid {vien}; border-radius:8px; width:140px; height:140px; background:rgba(255,255,255,0.85); text-align:center; font-size:14px; line-height:1.15; padding:3px; overflow:hidden;">
                    <div style="font-size:12px">{cup}</div>
                    <b>{tv['ten']}</b><br>
                    🌺 {tv['tong']}<br>
                    🔴 {tv['cap']['Đỏ']} 🟠 {tv['cap']['Cam']}<br>
                    🟣 {tv['cap']['Tím']} 🔵 {tv['cap']['Xanh dương']} 🟢 {tv['cap']['Xanh lá']}<br>
                </div>
                """
                so_top += 1
            html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

# ====================================================
# KHU VỰC 3: BỘ SƯU TẬP (HỘI / XEM)
# ====================================================
if st.session_state.quyen != "admin":
    with tab_suu_tap:
        tab1, tab2, tab3 = st.tabs(["👤 Cá Nhân", "👥 Toàn Hội", "🔎 Tra cứu"])
        
        with tab1:
            danh_sach_tv_st = [x for x in du_lieu_hoi_dang_dung.keys() if not x.startswith("_")]
            tv_xem = st.selectbox("Xem kho của:", ["-- Chọn --"] + danh_sach_tv_st, key="selectTV")
        
            if tv_xem != "-- Chọn --" and tv_xem in du_lieu_hoi_dang_dung:
                kho_hoa_tv = du_lieu_hoi_dang_dung[tv_xem]
                if not kho_hoa_tv:
                    st.markdown("<p style='font-size:13px;'>Trống.</p>", unsafe_allow_html=True)
                else:
                    dem_cap = {"Đỏ": 0, "Cam": 0, "Tím": 0, "Xanh dương": 0, "Xanh lá": 0}
                    for ten in kho_hoa_tv:
                        info = kho_hoa_kha_dung.get(ten, {})
                        cap = info.get("cap", "")
                        if cap in dem_cap:
                            dem_cap[cap] += 1

                    tong_hoa = sum(dem_cap.values())
                    chon_cap = st.radio(
                        "Lọc cấp:",
                        [
                            f"🌈 Tất cả: {tong_hoa}",
                            f"🔴 Đỏ: {dem_cap['Đỏ']}",
                            f"🟠 Cam: {dem_cap['Cam']}",
                            f"🟣 Tím: {dem_cap['Tím']}",
                            f"🔵 Xanh dương: {dem_cap['Xanh dương']}",
                            f"🟢 Xanh lá: {dem_cap['Xanh lá']}"
                        ],
                        horizontal=True
                    )

                    html = '<div class="flower-grid">'
                    for ten_hoa in sap_xep_hoa(kho_hoa_tv, kho_hoa_kha_dung):
                        info = kho_hoa_kha_dung.get(ten_hoa, {"anh": None})

                        if "Đỏ" in chon_cap and info.get("cap") != "Đỏ": continue
                        if "Cam" in chon_cap and info.get("cap") != "Cam": continue
                        if "Tím" in chon_cap and info.get("cap") != "Tím": continue
                        if "Xanh dương" in chon_cap and info.get("cap") != "Xanh dương": continue
                        if "Xanh lá" in chon_cap and info.get("cap") != "Xanh lá": continue

                        link_anh = anh_html(info.get("anh"))
                        cap = info.get("cap", "")
                        mau = {
                            "Đỏ": "#ef4444", "Tím": "#c084fc", "Xanh lá": "#22c55e",
                            "Xanh dương": "#38bdf8", "Cam": "#f59e0b"
                        }.get(cap, "#d6a83d")

                        html += f"""
                        <div class="flower-box">
                            <img src="{link_anh}" style="border:5px solid {mau};">
                            <div class="flower-name">{ten_hoa}</div>
                        </div>
                        """
                    html += "</div>"
                    components.html(GRID_STYLE + html, height=450, scrolling=True)
        
                    st.write("")
                    if st.session_state.quyen == "hoi":
                        hoa_thu_hoi = st.selectbox(
                            "↩️ Chọn hoa cần thu hồi",
                            ["-- Chọn hoa --"] + list(kho_hoa_tv),
                            key="chon_thu_hoi"
                        )
                        if st.button("↩️ Thu hồi hoa", use_container_width=True):
                            if hoa_thu_hoi != "-- Chọn hoa --":
                                du_lieu_hoi_dang_dung[tv_xem].remove(hoa_thu_hoi)
                                if luu_du_lieu():
                                    st.rerun()

        with tab2:
            dem_cap = {"Đỏ": 0, "Cam": 0, "Tím": 0, "Xanh dương": 0, "Xanh lá": 0}
            for ten_hoa, info in kho_hoa_kha_dung.items():
                owners = [tv for tv, hoa_list in du_lieu_hoi_dang_dung.items() if ten_hoa in hoa_list]
                if owners:
                    cap = info.get("cap", "")
                    if cap in dem_cap:
                        dem_cap[cap] += 1

            tong_hoa = sum(dem_cap.values())
            chon_cap = st.radio(
                "Lọc cấp:",
                [
                    f"🌈 Tất cả: {tong_hoa}",
                    f"🔴 Đỏ: {dem_cap['Đỏ']}",
                    f"🟠 Cam: {dem_cap['Cam']}",
                    f"🟣 Tím: {dem_cap['Tím']}",
                    f"🔵 Xanh dương: {dem_cap['Xanh dương']}",
                    f"🟢 Xanh lá: {dem_cap['Xanh lá']}"
                ],
                horizontal=True,
                key="loc_cap_toan_hoi"
            )

            if not kho_hoa_kha_dung:
                st.markdown("<p style='font-size:13px;'>Chưa có hoa nào.</p>", unsafe_allow_html=True)
            else:
                html = '<div class="flower-grid">'
                for ten_hoa in sap_xep_hoa(kho_hoa_kha_dung.keys(), kho_hoa_kha_dung):
                    info = kho_hoa_kha_dung[ten_hoa]
                    cap = info.get("cap", "")

                    loc = (
                        chon_cap.split(":")[0]
                        .replace("🌈 ", "").replace("🔴 ", "").replace("🟠 ", "")
                        .replace("🟣 ", "").replace("🔵 ", "").replace("🟢 ", "")
                    )

                    if loc != "Tất cả" and cap != loc:
                        continue

                    owners = [tv for tv, hoa_list in du_lieu_hoi_dang_dung.items() if ten_hoa in hoa_list]
                    if owners:
                        link_anh = anh_html(info.get("anh"))
                        mau = {
                            "Đỏ": "#ef4444", "Tím": "#c084fc", "Xanh lá": "#22c55e",
                            "Xanh dương": "#38bdf8", "Cam": "#f59e0b"
                        }.get(cap, "#d6a83d")

                        html += f"""
                        <div class="flower-box">
                            <img src="{link_anh}" style="border:5px solid {mau};">
                            <div class="flower-name">{ten_hoa}</div>
                        </div>
                        """
                html += "</div>"
                components.html(GRID_STYLE + html, height=450, scrolling=True)

        with tab3:
            st.markdown("## 🔍 Tra cứu hoa")
            ds_tim_so_huu = ["-- Chọn --"] + list(kho_hoa_kha_dung.keys())
            tim_so_huu = st.selectbox("Nhập tên hoa", ds_tim_so_huu, key="tim_so_huu_tra_cuu")

            if tim_so_huu != "-- Chọn --":
                ds_co = [tv for tv, hoa_list in du_lieu_hoi_dang_dung.items() if tim_so_huu in hoa_list]
                st.success(f"🌺 {tim_so_huu} - Có {len(ds_co)} thành viên sở hữu")
                for tv in ds_co:
                    st.markdown(
                        f"""
                        <p style="color:#000000 !important; font-weight:800 !important; font-size:16px !important; margin:6px 0;">
                        👤 {tv}
                        </p>
                        """,
                        unsafe_allow_html=True
                    )

# ====================================================
# KHU VỰC THÔNG TIN VÀ SAO LƯU (HỘI / XEM)
# ====================================================
if st.session_state.quyen != "admin":    
    with tab_thong_tin:
        st.markdown(
            """
            <div style="text-align:center; padding:20px; font-size:16px;">
                <p>
                👑 Sáng tạo bởi: <b>Đức Tài</b><br><br>
                📱 Điện thoại: <b>0373.30.30.55</b><br><br>
                🌺 Phiên bản: <b>1.0</b><br>
                💻 Ứng dụng quản lý hoa hội
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.quyen == "hoi":
            st.write("---")
            st.subheader("💾 Sao lưu dữ liệu hội")

            du_lieu_xuat = chuan_hoa_data_hoi(du_lieu_hoi_dang_dung)
            file_json = json.dumps(du_lieu_xuat, ensure_ascii=False, indent=4)

            st.download_button(
                label="⬇️ Tải dữ liệu về máy",
                data=file_json,
                file_name=f"{st.session_state.ten_tai_khoan}.json",
                mime="application/json",
                use_container_width=True
            )
            st.write("---")
            st.subheader("📂 Khôi phục dữ liệu hội")

            if "xoa_file_khoi_phuc" in st.session_state:
                del st.session_state.xoa_file_khoi_phuc
                st.session_state.key_file_kp = st.session_state.get("key_file_kp", 0) + 1

            file_up = st.file_uploader(
                "Chọn file sao lưu",
                type=["json"],
                key=f"file_kp_{st.session_state.get('key_file_kp',0)}"
            )

            if file_up is not None:
                if st.button("♻️ Khôi phục dữ liệu", use_container_width=True):
                    try:
                        du_lieu_nhap = json.load(file_up)
                        if isinstance(du_lieu_nhap, dict):
                            du_lieu_hoi_dang_dung.clear()
                            du_lieu_hoi_dang_dung.update(du_lieu_nhap)

                            if luu_du_lieu():
                                st.success("✅ Đã khôi phục dữ liệu")
                                time.sleep(1)
                                st.session_state.xoa_file_khoi_phuc = True
                                st.rerun()
                        else:
                            st.error("❌ File không đúng định dạng")
                    except Exception as e:
                        st.error(f"❌ File bị lỗi: {e}")

# ==================================================
# 👥 QUẢN LÝ TÀI KHOẢN KHÁCH & KIỂM SOÁT (ADMIN)
# ==================================================
if st.session_state.quyen == "admin":
    with tab_khach:
        if "key_xoa_khach" not in st.session_state:
            st.session_state.key_xoa_khach = 0

        st.markdown("### 👥 Quản lý tài khoản hội")
        if "reset_tao_hoi" in st.session_state:
            st.session_state.tao_user = ""
            st.session_state.tao_pass = ""
            del st.session_state.reset_tao_hoi

        ten_moi = st.text_input("Tên tài khoản hội", key="tao_user")
        mat_khau_moi = st.text_input("Mật khẩu", key="tao_pass")

        if st.button("➕ Tạo tài khoản hội"):
            if ten_moi.strip() == "" or mat_khau_moi.strip() == "":
                st.warning("Nhập đủ tài khoản và mật khẩu")
            elif ten_moi in st.session_state.tai_khoan:
                st.error("Tài khoản đã tồn tại")
            else:
                st.session_state.tai_khoan[ten_moi] = {
                    "pass": mat_khau_moi,
                    "quyen": "hoi",
                    "trang_thai": "hoat_dong",
                    "ten_hien_thi": ten_moi,
                    "ngay_tao": datetime.now().strftime("%d/%m/%Y")
                }
                luu_du_lieu_hoi(ten_moi, {})
                luu_du_lieu_len_github()
                st.success("Đã tạo tài khoản hội")
                st.session_state.reset_tao_hoi = True
                st.rerun()

        st.write("---")
        st.markdown("### 🔑 Đổi mật khẩu hội")
        ds_hoi = [ten for ten, info in st.session_state.tai_khoan.items() if info.get("quyen") == "hoi"]

        hoi_doi_pass = st.selectbox("Chọn hội", ["-- Chọn --"] + ds_hoi, index=0, key="doi_pass_hoi")

        if "reset_mk_hoi" in st.session_state:
            st.session_state.mk_hoi_moi = ""
            del st.session_state.reset_mk_hoi

        mk_hoi_moi = st.text_input("Mật khẩu mới cho hội", type="password", key="mk_hoi_moi")

        if st.button("💾 Lưu mật khẩu hội", use_container_width=True):
            if hoi_doi_pass == "-- Chọn --":
                st.warning("Chọn hội cần đổi")
            elif mk_hoi_moi.strip() == "":
                st.warning("Nhập mật khẩu mới")
            else:
                st.session_state.tai_khoan[hoi_doi_pass]["pass"] = mk_hoi_moi
                if luu_du_lieu():
                    st.success("Đã đổi mật khẩu hội")
                    st.session_state.reset_mk_hoi = True
                    st.rerun()

        st.write("---")
        st.markdown("### 🔑 Đổi mật khẩu Admin")

        if "reset_admin_pass" in st.session_state:
            st.session_state.doi_pass_admin = ""
            del st.session_state.reset_admin_pass

        mk_admin_moi = st.text_input("Mật khẩu admin mới", type="password", key="doi_pass_admin")

        if st.button("💾 Lưu mật khẩu admin", use_container_width=True):
            if mk_admin_moi.strip() == "":
                st.warning("Nhập mật khẩu mới")
            else:
                st.session_state.tai_khoan["admin"]["pass"] = mk_admin_moi
                if luu_du_lieu():
                    st.success("✅ Đã đổi mật khẩu admin")
                    st.session_state.reset_admin_pass = True
                    st.rerun()

        st.markdown("### 🗑️ Xóa tài khoản Hội")
        if "thong_bao_xoa" in st.session_state:
            st.success(st.session_state.thong_bao_xoa)
            del st.session_state.thong_bao_xoa

        ds_khach = [ten for ten, info in st.session_state.tai_khoan.items() if info.get("quyen") == "hoi"]
        khach_xoa = st.selectbox("Chọn khách cần xóa", ["-- Chọn --"] + ds_khach, key=f"xoa_khach_{st.session_state.key_xoa_khach}")

        if st.button("❌ Xóa Hội", use_container_width=True):
            if khach_xoa == "-- Chọn --":
                st.warning("⚠️ Chọn khách cần xóa")
            else:
                del st.session_state.tai_khoan[khach_xoa]
                ds_xoa = [
                    tk for tk, info in st.session_state.tai_khoan.items()
                    if info.get("quyen") == "xem" and info.get("chu_so_huu") == khach_xoa
                ]
                for tk in ds_xoa:
                    del st.session_state.tai_khoan[tk]

                if luu_du_lieu_len_github():
                    st.session_state.thong_bao_xoa = f"✅ Đã xóa hội {khach_xoa}"
                    st.session_state.key_xoa_khach += 1
                    st.rerun()

    with tab_kiem_soat:
        if "thong_bao_xoa" in st.session_state:
            st.success(st.session_state["thong_bao_xoa"])
            del st.session_state["thong_bao_xoa"]

        st.subheader("📊 Kiểm soát khách hàng")
        tong_khach = sum(1 for info in st.session_state.tai_khoan.values() if info.get("quyen") == "hoi")
        st.metric("👥 Tổng khách hàng", tong_khach)

        for ten, info in st.session_state.tai_khoan.items():
            if info.get("quyen") == "hoi":
                du_lieu_hoi = doc_du_lieu_hoi(ten)
                so_tv = len([k for k in du_lieu_hoi.keys() if not k.startswith("_")])
                
                st.markdown(
                    f"""
                    ### 👤 {ten}
                    📅 Ngày tạo: {info.get("ngay_tao","Không rõ")}
                    👥 Hội viên: {so_tv}
                    ---
                    """
                )

                if "thong_bao" in st.session_state:
                    st.success(st.session_state.thong_bao)
                    del st.session_state.thong_bao

                ten_moi = st.text_input("Tên hiển thị", value=info.get("ten_hien_thi", ten), key=f"doi_ten_{ten}")

                if st.button("💾 Lưu tên", key=f"luu_ten_{ten}"):
                    st.session_state.tai_khoan[ten]["ten_hien_thi"] = ten_moi
                    if luu_du_lieu():
                        st.session_state.thong_bao = "✅ Đã đổi tên hội thành công"
                        st.rerun()

                if info.get("trang_thai", "hoat_dong") == "hoat_dong":
                    if st.button("🔒 Ngưng hoạt động", key=f"khoa_{ten}"):
                        st.session_state.tai_khoan[ten]["trang_thai"] = "khoa"
                        luu_du_lieu()
                        st.rerun()
                else:
                    st.error("⛔ Hội đang ngưng hoạt động")
                    if st.button("🔓 Mở lại", key=f"mo_{ten}"):
                        st.session_state.tai_khoan[ten]["trang_thai"] = "hoat_dong"
                        luu_du_lieu()
                        st.rerun()

# ==================================================
# TÀI KHOẢN XEM CỦA HỘI (HỘI)
# ==================================================
if st.session_state.quyen == "hoi":
    with tab_tai_khoan_xem:
        if "force_reload" in st.session_state:
            del st.session_state.force_reload
            st.rerun()

        st.subheader("🔑 Tài khoản xem cho thành viên")
        ten_hoi = st.session_state.chu_so_huu if st.session_state.get("chu_so_huu") else st.session_state.ten_tai_khoan
        du_lieu_hoi_dang_dung = doc_du_lieu_hoi(ten_hoi)
        tk_xem_info = du_lieu_hoi_dang_dung.get("_tai_khoan_xem", None)

        if tk_xem_info:
            st.success(f"Đang có tài khoản xem: {tk_xem_info.get('user')}")
            st.write("---")
            st.subheader("🔑 Đổi mật khẩu")

            if "thong_bao_mk" in st.session_state:
                st.success(st.session_state.thong_bao_mk)
                del st.session_state.thong_bao_mk

            if "key_mk_xem" not in st.session_state:
                st.session_state.key_mk_xem = 0

            mk_moi = st.text_input("Mật khẩu mới", type="password", key=f"mk_xem_moi_{st.session_state.key_mk_xem}")

            if st.button("💾 Lưu mật khẩu mới", use_container_width=True):
                if mk_moi.strip() == "":
                    st.warning("Nhập mật khẩu mới")
                else:
                    du_lieu_hoi_dang_dung["_tai_khoan_xem"]["pass"] = mk_moi
                    if luu_du_lieu_hoi(ten_hoi, du_lieu_hoi_dang_dung):
                        st.session_state.thong_bao_mk = "✅ Đã đổi mật khẩu thành công"
                        st.session_state.key_mk_xem += 1
                        st.rerun()
        else:
            if "reset_tk_xem" in st.session_state:
                st.session_state.key_tk_xem = st.session_state.get("key_tk_xem", 0) + 1
                del st.session_state.reset_tk_xem

            if "key_tk_xem" not in st.session_state:
                st.session_state.key_tk_xem = 0

            tk_xem = st.text_input("Tên đăng nhập xem", key=f"tk_xem_{st.session_state.key_tk_xem}")
            mk_xem = st.text_input("Mật khẩu", type="password", key=f"mk_xem_{st.session_state.key_tk_xem}")

            if st.button("➕ Tạo tài khoản xem"):
                trung = False
                if tk_xem in st.session_state.tai_khoan:
                    trung = True

                for ten, info in st.session_state.tai_khoan.items():
                    if info.get("quyen") == "hoi":
                        data_check = doc_du_lieu_hoi(ten)
                        tk = data_check.get("_tai_khoan_xem", {})
                        if tk.get("user") == tk_xem:
                            trung = True
                            break

                if trung:
                    st.error("Tên đăng nhập đã tồn tại")
                else:
                    du_lieu_hoi_dang_dung["_tai_khoan_xem"] = {
                        "user": tk_xem,
                        "pass": mk_xem,
                        "ngay_tao": datetime.now().strftime("%d/%m/%Y")
                    }
                    if luu_du_lieu_hoi(ten_hoi, du_lieu_hoi_dang_dung):
                        st.session_state.reset_tk_xem = True
                        st.session_state.force_reload = True
                        st.rerun()
