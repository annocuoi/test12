import json
import base64
import requests
import streamlit as st # type: ignore
import streamlit.components.v1 as components
import time
from PIL import Image
from datetime import datetime
import io

# Cấu hình giao diện ứng dụng (phải nằm trước mọi lệnh st.)
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
st.markdown(
    """
    <style>
    /* chặn thanh fixed dưới cùng */
    div[class*="viewerBadge"] {
        display:none !important;
    }

    /* mobile + desktop */
    div[style*="bottom: 0"],
    div[style*="bottom:0"] {
        display:none !important;
    }
    /* Ẩn thanh toolbar Streamlit trên cùng */
    [data-testid="stToolbar"] {
        display: none;
    }
    
    /* Ẩn header */
    [data-testid="stHeader"] {
        display: none;
    }
    
    /* Ẩn menu */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Ẩn footer */
    footer {
        visibility: hidden;
    }
    /* làm trong suốt ô selectbox */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.35) !important;
        border-radius:12px !important;
    }

    /* bỏ nền xám bên trong */
    div[data-baseweb="select"] input {
        background: transparent !important;
    }

    /* vùng chứa chữ */
    div[data-baseweb="select"] span {
        background: transparent !important;
    }
    /* ẩn gạch nhập trong selectbox */
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
    }
    /* tiêu đề tự co mọi màn hình */
    .title-hoi {
        display:flex;
        justify-content:center;
        align-items:center;
        gap:10px;

        font-size:clamp(22px, 6vw, 38px);

        font-weight:900;
        color:#000000;
        white-space:nowrap;
    }


    /* icon hoa tự co */
    .title-hoi span {
        white-space:nowrap;
    }
    /* chữ trong danh sách xổ xuống selectbox */
    div[role="option"],
    div[role="option"] *,
    ul[role="listbox"] *,
    [data-baseweb="popover"] * {
        color:#000000 !important;
        font-weight:700 !important;
    }


    /* nền dòng option */
    div[role="option"] {
        background:white !important;
    }

    /* chữ trong ô nhập */
    input {
        color:#000000 !important;
        font-weight:700 !important;
    }

    /* placeholder */
    input::placeholder {
        color:#555555 !important;
    }


    /* text area nếu có */
    textarea {
        color:#000000 !important;
    }
    /* ép toàn bộ chữ Streamlit */
    .stApp * {
        color:#111111 !important;
    }


    /* tiêu đề markdown HTML */
    
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {
        color:#000000 !important;
        font-weight:700 !important;
    }


    /* chữ trong container */
    .element-container,
    .element-container * {
        color:#000000 !important;
    }


    /* chữ tab */
    button[data-baseweb="tab"] *,
    button[data-baseweb="tab"] p {
        color:#111111 !important;
    }


    /* radio lọc cấp */
    [data-testid="stRadio"] * {
        color:#111111 !important;
    }


    /* metric */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color:#000 !important;
    }

    /* tiêu đề */
    h1, h2, h3, h4 {
        color:#1e293b !important;
        font-weight:900 !important;
        text-shadow: 1px 1px 3px white;
    }

    /* tab */
    button[data-baseweb="tab"] p {
        color:#111827 !important;
        font-weight:800;
    }


    /* số thống kê 22 - 5 */
    [data-testid="stMetricValue"] {
        color:#000000 !important;
        font-weight:900;
    }


    /* tên hoa */
    .flower-name {
        color:#000 !important;
        font-weight:900;
        text-shadow:1px 1px 2px white;
    }


    /* chữ trong nút */
    button {
        color:#111827 !important;
        font-weight:700 !important;
    }


    /* select + nhập liệu */
    input, textarea {
        color:black !important;
        font-weight:700;
    }

    div[data-baseweb="select"] * {
        color:black !important;
    }

    /* bỏ nền trắng chính giữa */
    .block-container {
        background: transparent !important;
    }


    /* các khung trắng */
    div[data-testid="stVerticalBlock"] {
        background: transparent !important;
    }


    /* tab */
    button[data-baseweb="tab"] {
        background: rgba(255,255,255,0.15);
        border-radius: 15px;
        color: white;
    }


    /* chữ toàn app */
    h1,h2,h3,p,span,label,div {
        color: white !important;
    }


    /* ô nhập */
    input {
        background: rgba(255,255,255,0.9)!important;
        color:black!important;
        border-radius:12px!important;
    }


    /* selectbox */
    div[data-baseweb="select"] {
        background:white;
        border-radius:12px;
    }


    </style>
    """,
    unsafe_allow_html=True
)

GRID_STYLE = """
<style>
html, body{
    overflow-x:hidden;
    max-width:100%;
}

.flower-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(80px, 1fr));
    gap:18px;

    width:100%;
    max-width:100%;
    overflow-x:hidden;

    padding-right:15px;
    box-sizing:border-box;
}

.flower-box{
    text-align:center;
}

.flower-box img{
    width:75px;
    height:75px;
    object-fit:cover;

    border-radius:10px;
    padding:3px;
    box-shadow:0 3px 8px rgba(0,0,0,.3);
}
.hoa-img{
    width:75px;
    height:75px;
    object-fit:cover;

    border:5px solid;
    border-radius:10px;
    padding:3px;

    box-shadow:0 3px 8px rgba(0,0,0,.3);
}

.flower-box img.cap-do{
    border:5px solid #ef4444;
}

.flower-box img.cap-tim{
    border:5px solid #c084fc;
}

.flower-box img.cap-xanh-la{
    border:5px solid #22c55e;
}

.flower-box img.cap-xanh-duong{
    border:5px solid #38bdf8;
}

.flower-box img.cap-cam{
    border:5px solid #f59e0b;
}

.flower-name{
    font-size:13px;
    font-weight:bold;
    margin-top:5px;
}


.member-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
}


.member-box{
    text-align:center;
    border:1px solid #ddd;
    border-radius:10px;
    padding:6px;
}


.avatar{
    width:45px;
    height:45px;
    border-radius:50%;
    background:#8b5cf6;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:auto;
    font-size:20px;
    font-weight:bold;
}


.member-name{
    font-size:11px;
    font-weight:bold;
}


.member-count{
    font-size:10px;
}


</style>
"""
def anh_html(data):
    if not data:
        return ""

    if isinstance(data, bytes):
        img64 = base64.b64encode(data).decode()
    else:
        img64 = data

    return f"data:image/jpeg;base64,{img64}"
def background_image(file):
    with open(file, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image: url("data:image/png;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .block-container {{
            background: rgba(255,255,255,0.75);
            border-radius:20px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )
background_image("nen.jpg")
def sap_xep_hoa(ds_hoa):

    thu_tu_cap = {
        "Đỏ": 1,
        "Cam": 2,
        "Tím": 3,
        "Xanh dương": 4,
        "Xanh lá": 5
    }

    return sorted(
        ds_hoa,
        key=lambda ten: thu_tu_cap.get(
            st.session_state.kho_hoa_tong.get(
                ten,
                {}
            ).get(
                "cap",
                ""
            ),
            99
        )
    )

# ====================================================
# ⚙️ CẤU HÌNH HỆ THỐNG (ĐỌC TOKEN TỪ SECRETS AN TOÀN)
# ====================================================
MAT_KHAU_HE_THONG = "111111"


if "GITHUB_TOKEN" in st.secrets:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
else:
    GITHUB_TOKEN = ""

REPO_NAME = "annocuoi/Hoa-vien-online"
FILE_PATH = "du_lieu_hoa1.json"
BRANCH = "main"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"

# ====================================================
# ----------------------------------------------------
# 📂 HÀM ĐỌC DỮ LIỆU TỪ GITHUB
# ----------------------------------------------------
def tai_du_lieu_tu_github():
    mac_dinh = {
        "kho_hoa_tong": {},
        "tai_khoan": {}
    }
    try:
        url_doc = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}&t={time.time()}"
        headers_doc = {"Accept": "application/vnd.github.v3.raw"}
        if GITHUB_TOKEN:
            headers_doc["Authorization"] = f"token {GITHUB_TOKEN}"
            
        response = requests.get(url_doc, headers=headers_doc, timeout=10)
        if response.status_code == 200:
            chuoi_thong_tin = response.text.strip()
            if not chuoi_thong_tin or chuoi_thong_tin == '""' or chuoi_thong_tin == '{}':
                return mac_dinh
                
            data = json.loads(chuoi_thong_tin)
            
            kho_tong = data.get("kho_hoa_tong", {})
            for ten_hoa in kho_tong:
                if kho_tong[ten_hoa].get("anh"):
                    try:
                        kho_tong[ten_hoa]["anh"] = base64.b64decode(kho_tong[ten_hoa]["anh"].encode("utf-8"))
                    except Exception:
                        kho_tong[ten_hoa]["anh"] = None
            return data
    except Exception as e:
        st.sidebar.warning(f"Đang kết nối đám mây... ({str(e)})")
    return mac_dinh
# ==========================
# KHỞI TẠO SESSION ĐĂNG NHẬP
# ==========================

if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "ten_tai_khoan" not in st.session_state:
    st.session_state.ten_tai_khoan = ""

if "quyen" not in st.session_state:
    st.session_state.quyen = None
# ==========================
# LOAD TÀI KHOẢN
# ==========================

if "tai_khoan" not in st.session_state:

    du_lieu_goc = tai_du_lieu_tu_github()

    st.session_state.tai_khoan = du_lieu_goc.get("tai_khoan", {})


# chỉ tạo admin lần đầu tiên khi github chưa có gì
if len(st.session_state.tai_khoan) == 0:

    st.session_state.tai_khoan["admin"] = {
        "pass": "111111",
        "quyen": "admin",
        "ngay_tao": datetime.now().strftime("%d/%m/%Y")
    }
def tao_ten_file_hoi(ten_hoi):

    ten = ten_hoi.lower()
    ten = ten.replace(" ","_")

    return f"hoi/{ten}.json"
def doc_du_lieu_hoi(ten_hoi):

    try:

        url = (
            f"https://api.github.com/repos/"
            f"{REPO_NAME}/contents/"
            f"{tao_ten_file_hoi(ten_hoi):}"
        )

        r = requests.get(
            url,
            headers=HEADERS
        )

        if r.status_code == 200:

            noi_dung = r.json()["content"]

            noi_dung = noi_dung.replace("\n", "")

            data = json.loads(
                base64.b64decode(noi_dung).decode("utf-8")
            )

            return data

        return {}

    except Exception as e:
        return {}

if not st.session_state.da_dang_nhap:

    ten_dang_nhap = st.text_input(
        "Tài khoản",
        placeholder="Nhập tài khoản..."
    )

    mat_khau_nhap = st.text_input(
        "Mật khẩu",
        type="password",
        placeholder="Nhập mật khẩu..."
    )


    if st.button("🔐 Đăng Nhập", use_container_width=True):

        dang_nhap_ok = False

        # admin + hội
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

            chu_so_huu = None


        # tài khoản xem trong từng hội
        else:

            for ten_hoi, info in st.session_state.tai_khoan.items():

                if info.get("quyen") != "hoi":
                    continue
                if info.get("trang_thai", "hoat_dong") == "khoa":
                    continue
                data_hoi = doc_du_lieu_hoi(ten_hoi)

                tk_xem = data_hoi.get(
                    "_tai_khoan_xem",
                    {}
                )


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

    if st.button(
        "🚪 Đăng xuất",
        type="secondary",
        use_container_width=True
    ):

        st.session_state.da_dang_nhap = False
        st.session_state.ten_tai_khoan = ""
        st.session_state.quyen = None
        # xóa dữ liệu hội đang lưu tạm
        if "du_lieu_hoi" in st.session_state:
            del st.session_state.du_lieu_hoi

        if "hoi_dang_mo" in st.session_state:
            del st.session_state.hoi_dang_mo

        st.rerun()
# ----------------------------------------------------
# 💾 HÀM GHI DỮ LIỆU LÊN GITHUB
# ----------------------------------------------------
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
                anh_str = info.get("anh") if isinstance(info.get("anh"), str) else None
                
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
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Lỗi lưu file: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Lỗi mạng: {str(e)}")
        return False
    
# ==========================
# DỮ LIỆU RIÊNG TỪNG HỘI
# ==========================
def luu_du_lieu_hoi(ten_hoi, data):

    try:

        file_path = tao_ten_file_hoi(ten_hoi)

        url = (
            f"https://api.github.com/repos/"
            f"{REPO_NAME}/contents/"
            f"{file_path}"
        )


        get_file = requests.get(
            url,
            headers=HEADERS
        )


        payload = {

            "message": f"Luu hoi {ten_hoi}",

            "content": base64.b64encode(
                json.dumps(
                    data,
                    ensure_ascii=False
                ).encode()
            ).decode()

        }


        if get_file.status_code == 200:

            payload["sha"] = get_file.json()["sha"]



        res = requests.put(
            url,
            headers=HEADERS,
            json=payload
        )


        if res.status_code in [200,201]:

            return True


        # chống lỗi bấm nhanh / nhiều người lưu cùng lúc
        if res.status_code == 409:

            time.sleep(1)

            return luu_du_lieu_hoi(
                ten_hoi,
                data
            )


        st.error(
            f"Lỗi lưu hội: {res.status_code}"
        )

        return False


    except Exception as e:

        st.error(e)

        return False
    
def xoa_du_lieu_hoi(ten_hoi):

    try:

        file_path = tao_ten_file_hoi(ten_hoi)

        url = (
            f"https://api.github.com/repos/"
            f"{REPO_NAME}/contents/"
            f"{file_path}"
        )

        lay = requests.get(
            url,
            headers=HEADERS
        )

        if lay.status_code != 200:
            return True


        data = {
            "message": f"xoa hoi {ten_hoi}",
            "sha": lay.json()["sha"]
        }


        xoa = requests.delete(
            url,
            headers=HEADERS,
            json=data
        )


        return xoa.status_code == 200


    except:

        return False
# ==========================
# LƯU THEO QUYỀN
# ==========================

def luu_du_lieu():

    if st.session_state.quyen == "admin":

        return luu_du_lieu_len_github()


    elif st.session_state.quyen == "hoi":

        return luu_du_lieu_hoi(
            st.session_state.ten_tai_khoan,
            st.session_state.du_lieu_hoi
        )


    return False
# Khởi tạo nạp dữ liệu
# ==========================
# KHỞI TẠO DỮ LIỆU
# ==========================

if "da_load_data" not in st.session_state:

    du_lieu_goc = tai_du_lieu_tu_github()

    st.session_state.kho_hoa_tong = du_lieu_goc.get(
        "kho_hoa_tong",
        {}
    )

    st.session_state.tai_khoan = du_lieu_goc.get(
        "tai_khoan",
        {}
    )

    if "admin" not in st.session_state.tai_khoan:
        st.session_state.tai_khoan["admin"] = {
            "pass": "111111",
            "quyen": "admin",
            "ngay_tao": datetime.now().strftime("%d/%m/%Y")
        }

    st.session_state.da_load_data = True
# chống mất session
if "du_lieu_thanh_vien" not in st.session_state:
    st.session_state.du_lieu_thanh_vien = {}

# ==============================
# CHỌN DATA SAU KHI ĐĂNG NHẬP
# ==============================

if st.session_state.quyen == "admin":

    du_lieu_hoi_dang_dung = {}


elif st.session_state.quyen == "hoi":

    ten = st.session_state.ten_tai_khoan


    if (
        "du_lieu_hoi" not in st.session_state
        or st.session_state.get("hoi_dang_mo") != ten
    ):

        st.session_state.du_lieu_hoi = doc_du_lieu_hoi(
            ten
        )

        st.session_state.hoi_dang_mo = ten


    du_lieu_hoi_dang_dung = (
        st.session_state.du_lieu_hoi
    )

elif st.session_state.quyen == "xem":

    hoi = st.session_state.chu_so_huu

    du_lieu_hoi_dang_dung = doc_du_lieu_hoi(
        hoi
    )

ten_hien_thi = "TÊN HỘI"

# tài khoản hội
if st.session_state.quyen == "hoi":

    ten_goc = st.session_state.ten_tai_khoan


# tài khoản xem
elif st.session_state.quyen == "xem":

    ten_goc = st.session_state.chu_so_huu


else:

    ten_goc = None


if ten_goc:

    ten_hien_thi = st.session_state.tai_khoan[
        ten_goc
    ].get(
        "ten_hien_thi",
        ten_goc
    )


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
    k:v
    for k,v in du_lieu_hoi_dang_dung.items()
    if not k.startswith("_")
}

tong_hoa_hoi_vien = sum(
    len(hoa)
    for hoa in du_lieu_dem.values()
)

tong_hoi_vien = len(
    du_lieu_dem
)


components.html(
f"""
<div style="
display:flex;
justify-content:center;
align-items:center;
gap:80px;
margin-top:10px;
margin-bottom:0px;
">

    <div style="text-align:center;">
        <div style="font-size:15px;">🌸 Tổng Hoa Hội Viên</div>
        <div style="font-size:28px;font-weight:bold;">
            {tong_hoa_hoi_vien}
        </div>
    </div>

    <div style="text-align:center;">
        <div style="font-size:15px;">👥 Hội viên</div>
        <div style="font-size:28px;font-weight:bold;">
            {tong_hoi_vien}
        </div>
    </div>

</div>
""",
height=75
)

st.write("---")
danh_sach_tv = [
    k for k in du_lieu_hoi_dang_dung.keys()
    if not k.startswith("_")
]

if st.session_state.quyen == "admin":

    tab_kho, tab_khach, tab_kiem_soat = st.tabs(
        [
            "📦 Kho",
            "👥 Khách hàng",
            "📊 Kiểm soát"
        ]
    )
elif st.session_state.quyen == "hoi":

    tab_suu_tap, tab_hoi_vien, tab_xep_hang, tab_thong_tin, tab_tai_khoan_xem = st.tabs(
        [
            "🌸 Bộ sưu tập",
            "👥 Hội viên",
            "🏆 Xếp hạng",
            "ℹ️ Thông tin",
            "🔑 TK xem"
        ]
    )


elif st.session_state.quyen == "xem":

    tab_suu_tap, tab_xep_hang, tab_thong_tin = st.tabs(
        [
            "🌸 Bộ sưu tập",
            "🏆 Xếp hạng",
            "ℹ️ Thông tin"
        ]
    )
# ====================================================
# KHU VỰC 1: QUẢN LÝ KHO HOA TỔNG
# ====================================================
if st.session_state.quyen == "admin":    
    with tab_kho:
        st.markdown("<h3 style='font-size: 18px;'>📦 1. Kho Hoa Tổng</h3>", unsafe_allow_html=True)
        col_kho1 = st.container()
        col_kho2 = st.container()
        
        with col_kho1:

            with st.expander(
                "➕ Thêm hoa mới",
                expanded=False
            ):
                if "key_them_hoa" not in st.session_state:
                    st.session_state.key_them_hoa = 0
                ten_hoa_moi = st.text_input(
                    "Tên hoa",
                    placeholder="Nhập tên hoa...",
                    key=f"txt_ten_hoa_moi_{st.session_state.key_them_hoa}"
                )
        
        
                cap_bac_moi = st.selectbox(
                    "Cấp bậc",
                    options=[
                        "Xanh lá",
                        "Xanh dương",
                        "Tím",
                        "Cam",
                        "Đỏ"
                    ],
                    key="sl_cap_bac_moi"
                )
        
        
                file_anh = st.file_uploader(
                    "Tải ảnh",
                    type=[
                        "png",
                        "jpg",
                        "jpeg"
                    ],
                    key=f"f_file_anh_{st.session_state.key_them_hoa}"
                )
        
        
                if st.button(
                    "📥 Thêm vào Kho",
                    use_container_width=True
                ):
        
                    ten_hoa_clean = ten_hoa_moi.strip()
        
        
                    if not ten_hoa_clean:
        
                        st.error(
                            "Vui lòng nhập tên!"
                        )
        
        
                    elif ten_hoa_clean in st.session_state.kho_hoa_tong:
        
        
                        st.warning(
                            "Đã tồn tại!"
                        )
        
        
                    else:
        
        
                        du_lieu_anh = None
        
        
                        if file_anh is not None:
        
                            try:
        
                                img = Image.open(file_anh)
        
        
                                if img.mode != "RGB":
        
                                    img = img.convert("RGB")
        
        
                                img.thumbnail(
                                    (300,300)
                                )
        
        
                                buffer = io.BytesIO()
        
        
                                img.save(
                                    buffer,
                                    format="JPEG",
                                    quality=70
                                )
        
        
                                du_lieu_anh = buffer.getvalue()
        
        
                            except Exception:
        
        
                                du_lieu_anh = file_anh.read()
        
        
                        st.session_state.kho_hoa_tong[
                            ten_hoa_clean
                        ] = {
        
                            "cap":cap_bac_moi,
        
                            "anh":du_lieu_anh
        
                        }
        
        
                        if luu_du_lieu():
                            st.session_state.key_them_hoa += 1
                            st.rerun()
        
        with col_kho2:
        
            st.markdown(
                "<p style='font-size:14px;font-weight:bold;'>📋 Danh sách hoa</p>",
                unsafe_allow_html=True
            )
        
            if not st.session_state.kho_hoa_tong:
        
                st.markdown(
                    "<p style='font-size:12px;color:gray;'>Kho đang trống.</p>",
                    unsafe_allow_html=True
                )
        
            else:

        # =============================
        # TÌM KIẾM + LỌC HOA
        # =============================

                ds_tim_hoa = [
                    "-- Chọn --"
                ] + list(st.session_state.kho_hoa_tong.keys())


                tim_hoa = st.selectbox(
                    "🔍 Tìm hoa",
                    ds_tim_hoa,
                    key="tim_hoa_kho"
                )
            
            
                dem_cap = {
                    "Đỏ": 0,
                    "Cam": 0,
                    "Tím": 0,
                    "Xanh dương": 0,
                    "Xanh lá": 0
                }

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

                loc_cap = (
                    loc_cap.split(":")[0]
                    .replace("🌈 ", "")
                    .replace("🔴 ", "")
                    .replace("🟠 ", "")
                    .replace("🟣 ", "")
                    .replace("🔵 ", "")
                    .replace("🟢 ", "")
                )
            
            
                danh_sach_loc = {}
            
            
                for ten_hoa, info in st.session_state.kho_hoa_tong.items():
            
            
                    if tim_hoa != "-- Chọn --":

                        if tim_hoa != ten_hoa:

                            continue
            
            
                    if loc_cap != "Tất cả":
            
                        if info["cap"] != loc_cap:
            
                            continue
            
            
                    danh_sach_loc[ten_hoa] = info
            
            
            
                if not danh_sach_loc:
            
                    st.info(
                        "Không tìm thấy hoa."
                    )
            
            
                else:
            
            
                    html = '<div class="flower-grid">'
            
            
                    for ten_hoa in sap_xep_hoa(danh_sach_loc.keys()):

                        info = danh_sach_loc[ten_hoa]

                        mau_cap = {
                            "Xanh lá": "cap-xanh-la",
                            "Xanh dương": "cap-xanh-duong",
                            "Tím": "cap-tim",
                            "Cam": "cap-cam",
                            "Đỏ": "cap-do"
                        }.get(info["cap"], "cap-do")


                        link_anh = anh_html(
                            info["anh"]
                        )
            
            
                        html += f"""
                        <div class="flower-box">

                            <img class="{mau_cap}"
                                src="{link_anh}">

                            <div class="flower-name">
                                {ten_hoa}
                            </div>

                        </div>
                        """
            
            
                    html += "</div>"
            
            
                    components.html(
                        GRID_STYLE + html,
                        height=450,
                        scrolling=True
                    )
        
        
                # =============================
                # XÓA HOA RIÊNG
                # =============================
        
                st.write("")
        
                hoa_xoa = st.selectbox(
                    "🗑️ Chọn hoa cần xóa",
                    ["-- Chọn hoa --"] + list(st.session_state.kho_hoa_tong.keys()),
                    key="chon_xoa_kho"
                )
        
        
                if st.button(
                    "🗑️ Xóa hoa khỏi kho",
                    use_container_width=True
                ):
        
                    if hoa_xoa != "-- Chọn hoa --":
        
                        del st.session_state.kho_hoa_tong[hoa_xoa]
        
        
                        for hoi in st.session_state.du_lieu_thanh_vien:

                            for tv in st.session_state.du_lieu_thanh_vien[hoi]:

                                st.session_state.du_lieu_thanh_vien[hoi][tv] = [
                                    h for h in st.session_state.du_lieu_thanh_vien[hoi][tv]
                                    if h != hoa_xoa
                                ]
        
        
                        if luu_du_lieu():
        
                            st.rerun()
        
        st.write("---")
# ====================================================
# KHU VỰC 2: CẤU HÌNH THÀNH VIÊN VÀ CẤP PHÁT
# ====================================================
if st.session_state.quyen == "hoi":
    with tab_hoi_vien:

        st.markdown(
            "<h3>👥 2. Hội Viên & Cấp Phát</h3>",
            unsafe_allow_html=True
        )

        col_tv1, col_tv2 = st.columns(2)


        # =====================
        # BÊN TRÁI: HỘI VIÊN
        # =====================
        with col_tv1:

            with st.expander(
                "➕ Quản lý hội viên",
                expanded=False
            ):
                if "key_them_tv" not in st.session_state:
                    st.session_state.key_them_tv = 0
                ten_tv_moi = st.text_input(
                    "➕ Nhập hội viên mới",
                    placeholder="Nhập tên...",
                    key=f"them_thanh_vien_{st.session_state.key_them_tv}"
                )
                
                if st.button(
                    "➕ Thêm hội viên",
                    use_container_width=True
                ):
                    ten_tv_clean = ten_tv_moi.strip()

                    if ten_tv_clean == "":
                        st.warning("⚠️ Vui lòng nhập tên hội viên")

                    elif ten_tv_clean.lower() in [
                        x.lower() for x in du_lieu_hoi_dang_dung.keys()
                    ]:
                        st.error("❌ Hội viên đã tồn tại")

                    else:
                        du_lieu_hoi_dang_dung[ten_tv_clean] = []

                        if luu_du_lieu():
                            st.session_state.key_them_tv += 1
                            st.success("✅ Đã thêm hội viên")
                            st.rerun()
                danh_sach_tv_that = [
                    x for x in du_lieu_hoi_dang_dung.keys()
                    if not x.startswith("_")
                ]
                tv_xoa = st.selectbox(
                    "🗑 Xóa hội viên",
                    ["-- Chọn --"] + danh_sach_tv_that,
                    key="xoa_tv"
                )

                if st.button(
                    "❌ Xóa",
                    use_container_width=True
                ):
                    if tv_xoa != "-- Chọn --":
                        del du_lieu_hoi_dang_dung[tv_xoa]

                        if luu_du_lieu():
                            st.rerun()


        # =====================
        # BÊN PHẢI: CẤP HOA
        # =====================
        with col_tv2:

            st.markdown("## 🪷 Thêm Hoa Cho Hội Viên")

            danh_sach_tv = (
                ["-- Chọn --"]
                +
                [
                    x for x in du_lieu_hoi_dang_dung.keys()
                    if not x.startswith("_")
                ]
            )


            tv_chon = st.selectbox(
                "👤 Chọn hội viên",
                danh_sach_tv,
                key="cap_tv"
            )

            # lấy hoa hội viên đang có
            if tv_chon == "-- Chọn --":

                hoa_da_co = []

            else:

                hoa_da_co = du_lieu_hoi_dang_dung.get(
                    tv_chon,
                    []
                )

            # lọc hoa chưa có
            hoa_chua_co = [
                hoa
                for hoa in st.session_state.kho_hoa_tong.keys()
                if hoa not in hoa_da_co
            ]


            if len(hoa_chua_co) > 0:

                hoa_chon = st.selectbox(
                    "🌸 Chọn hoa",
                    hoa_chua_co,
                    key="cap_hoa"
                )

                if "dang_them_hoa" not in st.session_state:
                    st.session_state.dang_them_hoa = False

                if st.button(
                    "🌺 Thêm Hoa",
                    use_container_width=True,
                    disabled=st.session_state.dang_them_hoa
                ):

                    st.session_state.dang_them_hoa = True

                    if not tv_chon or tv_chon == "-- Chọn --":
                        st.warning("⚠️ Vui lòng tạo hoặc chọn hội viên trước")

                    elif hoa_chon == "-- Chọn hoa --":
                        st.warning("⚠️ Vui lòng chọn hoa")

                    else:
                        du_lieu_hoi_dang_dung[tv_chon].append(
                            hoa_chon
                        )

                        if luu_du_lieu():

                            st.success(
                                "✅ Đã thêm hoa"
                            )

                            st.session_state.dang_them_hoa = False

                            st.rerun()

                        else:

                            st.session_state.dang_them_hoa = False

                            st.error(
                                "❌ Lưu thất bại, kiểm tra mạng"
                            )
            else:

                st.info("✅ Hội viên đã có tất cả hoa")
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

            dem = {
                "Đỏ":0,
                "Cam":0,
                "Tím":0,
                "Xanh dương":0,
                "Xanh lá":0
            }
            for hoa in ds_hoa:
                info = st.session_state.kho_hoa_tong.get(hoa,{})
                cap = info.get("cap","")

                if cap in dem:
                    dem[cap] += 1


            bang_xep_hang.append({
                "ten": ten_tv,
                "tong": len(ds_hoa),
                "cap": dem
            })


        bang_xep_hang.sort(
            key=lambda x: (
                x["tong"],                 # tổng hoa trước
                x["cap"]["Đỏ"],            # bằng tổng xét đỏ
                x["cap"]["Cam"],           # rồi cam
                x["cap"]["Tím"],           # rồi tím
                x["cap"]["Xanh dương"],    # xanh dương
                x["cap"]["Xanh lá"]        # xanh lá
            ),
            reverse=True
        )

        hang_xep = [
            bang_xep_hang[:1]   # top 1
        ]

        for i in range(1, len(bang_xep_hang), 2):
            hang_xep.append(
                bang_xep_hang[i:i+2]
            )


        html = ""
        so_top = 1


        for hang in hang_xep:

            cot = len(hang)

            html += f"""<div style="
    display:grid;
    grid-template-columns:repeat({cot},150px);
    justify-content:center;
    gap:12px;
    margin-bottom:6px;
    ">"""


            for tv in hang:

                if so_top == 1:
                    cup = "🥇"
                    vien = "#ffd700"
                    do_day_vien = "5px"

                elif so_top == 2:
                    cup = "🥈"
                    vien = "#c0c0c0"
                    do_day_vien = "4px"

                elif so_top == 3:
                    cup = "🥉"
                    vien = "#cd7f32"
                    do_day_vien = "4px"

                else:
                    cup = f"#{so_top}"
                    vien = "white"
                    do_day_vien = "2px"


                html += f"""
<div style="
border:{do_day_vien} solid {vien};
border-radius:8px;
width:140px;
height:140px;
background:rgba(255,255,255,0.85);
text-align:center;
font-size:14px;
line-height:1.15;
padding:3px;
overflow:hidden;
">

<div style="font-size:12px">{cup}</div>

<b>{tv['ten']}</b><br>

🌺 {tv['tong']}<br>

🔴 {tv['cap']['Đỏ']}
🟠 {tv['cap']['Cam']}<br>

🟣 {tv['cap']['Tím']}
🔵 {tv['cap']['Xanh dương']}
🟢 {tv['cap']['Xanh lá']}<br>

</div>
"""

                so_top += 1


            html += "</div>"


        st.markdown(
            html,
            unsafe_allow_html=True
        )
# ====================================================
# KHU VỰC 3: BỘ SƯU TẬP
# ====================================================
if st.session_state.quyen != "admin":
    with tab_suu_tap:
        st.markdown("<h3 style='font-size: 18px;'>🔍 3. Bộ Sưu Tập</h3>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(
            [
                "👤 Cá Nhân",
                "👥 Toàn Hội",
                "🔎 Tra cứu"
            ]
        )
        
        with tab1:
        
            danh_sach_tv = [
                x for x in danh_sach_tv
                if x != "-- Chọn --"
            ]

            tv_xem = st.selectbox(
                "Xem kho của:",
                ["-- Chọn --"] + danh_sach_tv,
                key="selectTV"
            )
        
        
            if tv_xem != "-- Chọn --" and tv_xem in du_lieu_hoi_dang_dung:
        
        
                kho_hoa_tv = du_lieu_hoi_dang_dung[tv_xem]
        
        
                if not kho_hoa_tv:
        
                    st.markdown(
                        "<p style='font-size:13px;'>Trống.</p>",
                        unsafe_allow_html=True
                    )
        
        
                else:
                    dem_cap = {
                        "Đỏ": 0,
                        "Cam": 0,
                        "Tím": 0,
                        "Xanh dương": 0,
                        "Xanh lá": 0
                    }

                    for ten in kho_hoa_tv:
                        info = st.session_state.kho_hoa_tong.get(ten, {})
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

                    if "Đỏ" in chon_cap:
                        loc_cap = "Đỏ"
                    elif "Cam" in chon_cap:
                        loc_cap = "Cam"
                    elif "Tím" in chon_cap:
                        loc_cap = "Tím"
                    elif "Xanh dương" in chon_cap:
                        loc_cap = "Xanh dương"
                    elif "Xanh lá" in chon_cap:
                        loc_cap = "Xanh lá"
                    else:
                        loc_cap = "Tất cả"
        
        
                    html = '<div class="flower-grid">'
        
        
                    for ten_hoa in sap_xep_hoa(kho_hoa_tv):
                        info = st.session_state.kho_hoa_tong.get(
                            ten_hoa,
                            {"anh": None}
                        )

                        if "Đỏ" in chon_cap and info.get("cap") != "Đỏ":
                            continue

                        if "Cam" in chon_cap and info.get("cap") != "Cam":
                            continue

                        if "Tím" in chon_cap and info.get("cap") != "Tím":
                            continue

                        if "Xanh dương" in chon_cap and info.get("cap") != "Xanh dương":
                            continue

                        if "Xanh lá" in chon_cap and info.get("cap") != "Xanh lá":
                            continue
        
        
                        info = st.session_state.kho_hoa_tong.get(
                            ten_hoa,
                            {"anh": None}
                        )
        
        
                        link_anh = anh_html(info["anh"])
                        cap = info.get("cap", "")

                        if cap == "Đỏ":
                            mau = "#ef4444"

                        elif cap == "Tím":
                            mau = "#c084fc"

                        elif cap == "Xanh lá":
                            mau = "#22c55e"

                        elif cap == "Xanh dương":
                            mau = "#38bdf8"

                        elif cap == "Cam":
                            mau = "#f59e0b"

                        else:
                            mau = "#d6a83d"
                            
        
                        html += f"""
                        <div class="flower-box">
                            <img src="{link_anh}" style="border:5px solid {mau};">
                            <div class="flower-name">
                                {ten_hoa}
                            </div>
                        </div>
                        """
        
        
                    html += "</div>"
        
        
                    components.html(
            GRID_STYLE + html,
            height=450,
            scrolling=True
        )
        
        
                    st.write("")
        
                    if st.session_state.quyen == "hoi":
                        hoa_thu_hoi = st.selectbox(
                            "↩️ Chọn hoa cần thu hồi",
                            ["-- Chọn hoa --"] + list(kho_hoa_tv),
                            key="chon_thu_hoi"
                        )
        
                
                        if st.button(
                            "↩️ Thu hồi hoa",
                            use_container_width=True
                        ):
            
            
                            if hoa_thu_hoi != "-- Chọn hoa --":
            
            
                                du_lieu_hoi_dang_dung[tv_xem].remove(
                                    hoa_thu_hoi
                                )
            
            
                                if luu_du_lieu():
            
            
                                    st.rerun()

        with tab2:

            # ==============================
            # ĐẾM CẤP HOA
            # ==============================
            dem_cap = {
                "Đỏ": 0,
                "Cam": 0,
                "Tím": 0,
                "Xanh dương": 0,
                "Xanh lá": 0
            }


            for ten_hoa, info in st.session_state.kho_hoa_tong.items():

                owners = [
                    tv
                    for tv, hoa_list
                    in du_lieu_hoi_dang_dung.items()
                    if ten_hoa in hoa_list
                ]

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


            if not st.session_state.kho_hoa_tong:

                st.markdown(
                    "<p style='font-size:13px;'>Chưa có hoa nào.</p>",
                    unsafe_allow_html=True
                )


            else:

                html = '<div class="flower-grid">'


                for ten_hoa in sap_xep_hoa(st.session_state.kho_hoa_tong.keys()):

                    info = st.session_state.kho_hoa_tong[ten_hoa]

                    cap = info.get("cap", "")


                    loc = chon_cap.split(":")[0]

                    loc = (
                        loc.replace("🌈 ", "")
                        .replace("🔴 ", "")
                        .replace("🟠 ", "")
                        .replace("🟣 ", "")
                        .replace("🔵 ", "")
                        .replace("🟢 ", "")
                    )


                    if loc != "Tất cả" and cap != loc:
                        continue


                    owners = [
                        tv
                        for tv, hoa_list
                        in du_lieu_hoi_dang_dung.items()
                        if ten_hoa in hoa_list
                    ]


                    if owners:


                        link_anh = anh_html(info["anh"])


                        if cap == "Đỏ":
                            mau = "#ef4444"

                        elif cap == "Tím":
                            mau = "#c084fc"

                        elif cap == "Xanh lá":
                            mau = "#22c55e"

                        elif cap == "Xanh dương":
                            mau = "#38bdf8"

                        elif cap == "Cam":
                            mau = "#f59e0b"

                        else:
                            mau = "#d6a83d"


                        html += f"""
                        <div class="flower-box">
                            <img src="{link_anh}" 
                            style="border:5px solid {mau};">

                            <div class="flower-name">
                                {ten_hoa}
                            </div>
                        </div>
                        """


                html += "</div>"


                components.html(
                    GRID_STYLE + html,
                    height=450,
                    scrolling=True
                )

        with tab3:

            st.markdown("## 🔍 Tra cứu hoa")

            ds_tim_so_huu = [
                "-- Chọn --"
            ] + list(st.session_state.kho_hoa_tong.keys())


            tim_so_huu = st.selectbox(
                "Nhập tên hoa",
                ds_tim_so_huu,
                key="tim_so_huu_tra_cuu"
            )

            if tim_so_huu != "-- Chọn --":

                ds_tim = [
                    tim_so_huu
                ]

                if ds_tim:

                    hoa_chon = ds_tim[0]

                    ds_co = []

                    for tv, hoa_list in du_lieu_hoi_dang_dung.items():

                        if hoa_chon in hoa_list:
                            ds_co.append(tv)


                    st.success(
                        f"🌺 {hoa_chon} - Có {len(ds_co)} thành viên sở hữu"
                    )


                    for tv in ds_co:
                        st.markdown(
                            f"""
                            <p style="
                                color:#000000 !important;
                                font-weight:800 !important;
                                font-size:16px !important;
                                margin:6px 0;
                            ">
                            👤 {tv}
                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.warning("❌ Không tìm thấy hoa")
if st.session_state.quyen != "admin":    
    with tab_thong_tin:

        st.markdown(
            """
            <div style="
            text-align:center;
            padding:20px;
            font-size:16px;
            ">


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
        # ==========================
        # 💾 SAO LƯU DỮ LIỆU HỘI
        # ==========================

        if st.session_state.quyen == "hoi":

            st.write("---")

            st.subheader("💾 Sao lưu dữ liệu hội")

            du_lieu_xuat = {}

            for ten_tv, ds_hoa in du_lieu_hoi_dang_dung.items():

                du_lieu_xuat[ten_tv] = ds_hoa


            file_json = json.dumps(
                du_lieu_xuat,
                ensure_ascii=False,
                indent=4
            )


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

                st.session_state.key_file_kp = (
                    st.session_state.get("key_file_kp",0) + 1
                )


            file_up = st.file_uploader(
                "Chọn file sao lưu",
                type=["json"],
                key=f"file_kp_{st.session_state.get('key_file_kp',0)}"
            )

            if file_up is not None:

                if st.button(
                    "♻️ Khôi phục dữ liệu",
                    use_container_width=True
                ):

                    try:

                        du_lieu_nhap = json.load(file_up)


                        if isinstance(du_lieu_nhap, dict):

                            # ghi đè dữ liệu hội hiện tại
                            du_lieu_hoi_dang_dung.clear()

                            du_lieu_hoi_dang_dung.update(
                                du_lieu_nhap
                            )


                            if luu_du_lieu():

                                st.success(
                                    "✅ Đã khôi phục dữ liệu"
                                )
                                time.sleep(2)

                                st.session_state.xoa_file_khoi_phuc = True

                                st.rerun()


                        else:

                            st.error(
                                "❌ File không đúng định dạng"
                            )


                    except Exception as e:

                        st.error(
                            f"❌ File bị lỗi: {e}"
                        )
# ==================================================
# 👥 QUẢN LÝ TÀI KHOẢN KHÁCH
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
        ten_moi = st.text_input(
            "Tên tài khoản hội",
            key="tao_user"
        )


        mat_khau_moi = st.text_input(
            "Mật khẩu",
            key="tao_pass"
        )

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

                # tạo file dữ liệu riêng cho hội
                luu_du_lieu_hoi(
                    ten_moi,
                    {}
                )

                luu_du_lieu_len_github()

                st.success("Đã tạo tài khoản hội")

                st.session_state.reset_tao_hoi = True

                st.rerun()
        # =========================
        # 🔑 ĐỔI MẬT KHẨU HỘI
        # =========================

        st.write("---")
        st.markdown("### 🔑 Đổi mật khẩu hội")

        ds_hoi = [
            ten
            for ten, info in st.session_state.tai_khoan.items()
            if info.get("quyen") == "hoi"
        ]


        hoi_doi_pass = st.selectbox(
            "Chọn hội",
            ["-- Chọn --"] + ds_hoi,
            index=0,
            key="doi_pass_hoi"
        )

        if "reset_mk_hoi" in st.session_state:
            st.session_state.mk_hoi_moi = ""
            del st.session_state.reset_mk_hoi
        mk_hoi_moi = st.text_input(
            "Mật khẩu mới cho hội",
            type="password",
            key="mk_hoi_moi"
        )


        if st.button(
            "💾 Lưu mật khẩu hội",
            use_container_width=True
        ):

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
        # =============================
        # 🔑 ĐỔI MẬT KHẨU ADMIN
        # =============================

        st.write("---")
        st.markdown("### 🔑 Đổi mật khẩu Admin")

        if "reset_admin_pass" in st.session_state:
            st.session_state.doi_pass_admin = ""
            del st.session_state.reset_admin_pass

        mk_admin_moi = st.text_input(
            "Mật khẩu admin mới",
            type="password",
            key="doi_pass_admin"
        )

        if st.button(
            "💾 Lưu mật khẩu admin",
            use_container_width=True
        ):

            if mk_admin_moi.strip() == "":
                st.warning("Nhập mật khẩu mới")

            else:
                st.session_state.tai_khoan["admin"]["pass"] = mk_admin_moi

                if luu_du_lieu():
                    st.success("✅ Đã đổi mật khẩu admin")
                    st.session_state.reset_admin_pass = True
                    st.rerun()
        # =========================
        # 🗑️ XÓA TÀI KHOẢN KHÁCH
        # =========================

        st.markdown("### 🗑️ Xóa tài khoản Hội")
        if "thong_bao_xoa" in st.session_state:

            st.success(
                st.session_state.thong_bao_xoa
            )

            del st.session_state.thong_bao_xoa


        ds_khach = [
            ten
            for ten, info in st.session_state.tai_khoan.items()
            if info.get("quyen") == "hoi"
        ]

        khach_xoa = st.selectbox(
            "Chọn khách cần xóa",
            ["-- Chọn --"] + ds_khach,
            key=f"xoa_khach_{st.session_state.key_xoa_khach}"
        )


        if st.button(
            "❌ Xóa Hội",
            use_container_width=True
        ):

            if khach_xoa == "-- Chọn --":

                st.warning("⚠️ Chọn khách cần xóa")

            else:

                # xóa tài khoản khách
                del st.session_state.tai_khoan[khach_xoa]


                # xóa dữ liệu hội viên của hội đó
                if khach_xoa in st.session_state.du_lieu_thanh_vien:

                    del st.session_state.du_lieu_thanh_vien[khach_xoa]


                # xóa luôn tài khoản xem thuộc hội đó
                ds_xoa = []

                for tk, info in st.session_state.tai_khoan.items():

                    if (
                        info.get("quyen") == "xem"
                        and info.get("chu_so_huu") == khach_xoa
                    ):

                        ds_xoa.append(tk)


                for tk in ds_xoa:

                    del st.session_state.tai_khoan[tk]


                # xóa file dữ liệu riêng của hội
                xoa_du_lieu_hoi(khach_xoa)


                if luu_du_lieu_len_github():

                    st.session_state.thong_bao_xoa = (
                        f"✅ Đã xóa hội {khach_xoa}"
                    )

                    st.session_state.key_xoa_khach += 1

                    st.rerun()
if st.session_state.quyen == "admin":

    with tab_kiem_soat:
        if "thong_bao_xoa" in st.session_state:

            st.success(
                st.session_state["thong_bao_xoa"]
            )

            del st.session_state["thong_bao_xoa"]

        st.subheader("📊 Kiểm soát khách hàng")

        tong_khach = 0

        for ten, info in st.session_state.tai_khoan.items():

            if info.get("quyen") == "hoi":
                tong_khach += 1


        st.metric(
            "👥 Tổng khách hàng",
            tong_khach
        )


        for ten, info in st.session_state.tai_khoan.items():

            if info.get("quyen") == "hoi":

                du_lieu_hoi = doc_du_lieu_hoi(ten)

                so_tv = len(du_lieu_hoi)
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
                ten_moi = st.text_input(
                    "Tên hiển thị",
                    value=info.get(
                        "ten_hien_thi",
                        ten
                    ),
                    key=f"doi_ten_{ten}"
                )


                if st.button(
                    "💾 Lưu tên",
                    key=f"luu_ten_{ten}"
                ):

                    st.session_state.tai_khoan[ten]["ten_hien_thi"] = ten_moi

                    if luu_du_lieu():

                        st.session_state.thong_bao = "✅ Đã đổi tên hội thành công"

                        st.rerun()
                if info.get("trang_thai", "hoat_dong") == "hoat_dong":

                    if st.button(
                        "🔒 Ngưng hoạt động",
                        key=f"khoa_{ten}"
                    ):

                        st.session_state.tai_khoan[ten]["trang_thai"] = "khoa"

                        luu_du_lieu()

                        st.rerun()

                else:

                    st.error("⛔ Hội đang ngưng hoạt động")

                    if st.button(
                        "🔓 Mở lại",
                        key=f"mo_{ten}"
                    ):

                        st.session_state.tai_khoan[ten]["trang_thai"] = "hoat_dong"

                        luu_du_lieu()

                        st.rerun()

# =========================
# TÀI KHOẢN XEM CỦA HỘI
# =========================

if st.session_state.quyen == "hoi":

    with tab_tai_khoan_xem:
        if "force_reload" in st.session_state:

            del st.session_state.force_reload

            st.rerun()

        st.subheader("🔑 Tài khoản xem cho thành viên")

        ten_hoi = (
            st.session_state.chu_so_huu
            if st.session_state.get("chu_so_huu")
            else st.session_state.ten_tai_khoan
        )
        du_lieu_hoi_dang_dung = doc_du_lieu_hoi(
            ten_hoi
        )

        tk_xem_info = du_lieu_hoi_dang_dung.get(
            "_tai_khoan_xem",
            None
        )


        if tk_xem_info:

            st.success(
                f"Đang có tài khoản xem: {tk_xem_info.get('user')}"
            )

            st.write("---")

            st.subheader("🔑 Đổi mật khẩu")
            if "thong_bao_mk" in st.session_state:

                st.success(
                    st.session_state.thong_bao_mk
                )

                del st.session_state.thong_bao_mk


            if "key_mk_xem" not in st.session_state:
                st.session_state.key_mk_xem = 0


            mk_moi = st.text_input(
                "Mật khẩu mới",
                type="password",
                key=f"mk_xem_moi_{st.session_state.key_mk_xem}"
            )


            if st.button(
                "💾 Lưu mật khẩu mới",
                use_container_width=True
            ):

                if mk_moi.strip() == "":

                    st.warning("Nhập mật khẩu mới")

                else:

                    du_lieu_hoi_dang_dung["_tai_khoan_xem"]["pass"] = mk_moi

                    if luu_du_lieu_hoi(
                        ten_hoi,
                        du_lieu_hoi_dang_dung
                    ):

                        st.session_state.thong_bao_mk = "✅ Đã đổi mật khẩu thành công"

                        st.session_state.key_mk_xem += 1

                        st.rerun()

        else:

            if "key_tk_xem" not in st.session_state:
                st.session_state.key_tk_xem = 0


            tk_xem = st.text_input(
                "Tên đăng nhập xem",
                key=f"tk_xem_{st.session_state.key_tk_xem}"
            )

            mk_xem = st.text_input(
                "Mật khẩu",
                type="password",
                key=f"mk_xem_{st.session_state.key_tk_xem}"
            )


            if st.button("➕ Tạo tài khoản xem"):

                trung = False

                # kiểm tra admin + hội
                if tk_xem in st.session_state.tai_khoan:
                    trung = True


                # kiểm tra tài khoản xem các hội khác
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


                    if luu_du_lieu_hoi(
                        ten_hoi,
                        du_lieu_hoi_dang_dung
                    ):

                        st.session_state.key_tk_xem += 1

                        st.session_state.force_reload = True

                        st.rerun()
