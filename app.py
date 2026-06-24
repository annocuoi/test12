import json
import base64
import requests
import streamlit as st # type: ignore
import streamlit.components.v1 as components
import time
from PIL import Image
from datetime import datetime
import io

# CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Quản Lý Hoa Hội", page_icon="🌸", layout="wide")

# CSS GỐC VÀ CSS GRID MỚI
st.markdown("""
<style>
    /* Ẩn các thứ thừa của Streamlit */
    div[class*="viewerBadge"], [data-testid="stToolbar"], [data-testid="stHeader"], #MainMenu, footer { display: none !important; }
    
    /* CSS GRID CỨNG CHO ĐIỆN THOẠI */
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
</style>
""", unsafe_allow_html=True)

# CÁC HÀM HỖ TRỢ
def anh_html(data):
    if not data: return ""
    if isinstance(data, bytes): img64 = base64.b64encode(data).decode()
    else: img64 = data
    return f"data:image/jpeg;base64,{img64}"

def sap_xep_hoa(ds_hoa):
    thu_tu_cap = {"Đỏ": 1, "Cam": 2, "Tím": 3, "Xanh dương": 4, "Xanh lá": 5}
    return sorted(ds_hoa, key=lambda ten: thu_tu_cap.get(st.session_state.kho_hoa_tong.get(ten, {}).get("cap", ""), 99))

# [BẠN GIỮ NGUYÊN CÁC HÀM: tai_du_lieu_tu_github, doc_du_lieu_hoi, luu_du_lieu... NHƯ CŨ]
# ... (Tôi viết gọn lại ở đây để bạn tiện dán) ...

# KHỞI TẠO SESSION
if "da_dang_nhap" not in st.session_state: st.session_state.da_dang_nhap = False
# ... (Duy trì logic đăng nhập của bạn) ...

# TABS HIỂN THỊ
# ... (Phần logic chọn tab như cũ) ...

# --- PHẦN SỬA ĐỔI QUAN TRỌNG NHẤT: CẤP NHANH HOA ---
if st.session_state.quyen == "hoi":
    with tab_cap_nhanh:
        st.markdown("## 🪷 Cấp Hoa Cho Hội Viên")
        danh_sach_tv = [x for x in du_lieu_hoi_dang_dung.keys() if not x.startswith("_")]
        tv_chon = st.selectbox("👤 Chọn hội viên", ["-- Chọn --"] + danh_sach_tv, key="chon_tv_cap_nhanh")

        if tv_chon != "-- Chọn --":
            # Logic lọc hoa
            danh_sach_hoa = [h for h in st.session_state.kho_hoa_tong.keys() if h not in du_lieu_hoi_dang_dung.get(tv_chon, [])]
            
            # DÙNG CSS GRID THAY VÌ ST.COLUMNS
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
                    if not hoa_chon: st.warning("⚠️ Chưa chọn hoa!")
                    else:
                        for h in hoa_chon:
                            if h not in du_lieu_hoi_dang_dung[tv_chon]: du_lieu_hoi_dang_dung[tv_chon].append(h)
                        if luu_du_lieu():
                            st.success("✅ Thành công!")
                            st.rerun()
        else:
            st.info("👆 Chọn hội viên để cấp hoa")
