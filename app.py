import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import base64
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pyvi import ViTokenizer

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Agoda Recommender System", page_icon="🌎", layout="wide")

# --- HÀM LOAD ẢNH LOCAL THÀNH BASE64 ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Đọc file ảnh local và chuyển thành mã Base64 để nhúng vào CSS"""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# Tự động tìm file ảnh tên 'banner.jpg' nằm cùng thư mục với app.py
img_base64 = get_base64_of_bin_file('banner.jpg')

if img_base64:
    # Lớp phủ mỏng để hiện rõ ảnh nền
    bg_img_css = f"background-image: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)), url('data:image/jpeg;base64,{img_base64}');"
else:
    # Nếu không tìm thấy ảnh, dùng màu xanh gradient mặc định
    bg_img_css = "background: linear-gradient(135deg, #003580 0%, #0071C2 100%);"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; color: #2A2A2E; }}
    .stApp {{ background-color: #F7F9FA; }}
    
    [data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; box-shadow: 2px 0 10px rgba(0,0,0,0.03);}}
    [data-testid="stSidebar"] h2 {{ color: #003580 !important; font-weight: 800 !important; font-size: 22px !important; letter-spacing: -0.5px;}}
    .stRadio label {{ font-size: 15px !important; font-weight: 600 !important; color: #475569 !important; cursor: pointer; }}
    
    .team-box {{ background: linear-gradient(135deg, #003580 0%, #005eb8 100%); border-radius: 12px; padding: 20px; color: #FFFFFF !important; box-shadow: 0 10px 20px -5px rgba(0,53,128,0.3); margin-top: 20px;}}
    .team-box b {{ color: #FFB700; font-size: 15px; text-transform: uppercase; letter-spacing: 1px;}}
    .team-box p {{ margin: 5px 0 5px 0; font-size: 14px; opacity: 0.9;}}
    
    .hotel-card {{ background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); height: 100%; display: flex; flex-direction: column; justify-content: space-between;}}
    .hotel-card:hover {{ transform: translateY(-6px); box-shadow: 0 15px 25px -5px rgba(0,53,128,0.12); border-color: #003580;}}
    .hotel-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;}}
    .hotel-title {{ color: #003580; font-size: 1.15rem; font-weight: 800; line-height: 1.3; max-width: 75%;}}
    .hotel-score-badge {{ background: #003580; color: #FFFFFF; padding: 6px 10px; border-radius: 8px 8px 8px 0; font-weight: 800; font-size: 15px; box-shadow: 0 2px 4px rgba(0,53,128,0.3);}}
    .hotel-loc {{ color: #64748B; font-size: 14px; margin-bottom: 10px; display: flex; align-items: center; gap: 5px;}}
    
    /* Thiết kế riêng cho hộp Thông kê Thông minh (Smart Stats) */
    .hotel-smart-stats {{ background-color: #F0F9FF; border-left: 4px solid #0071C2; padding: 12px 15px; margin-bottom: 15px; border-radius: 0 6px 6px 0; font-size: 13.5px; color: #334155; }}
    .hotel-smart-stats ul {{ list-style-type: none; padding-left: 0; margin: 0; }}
    .hotel-smart-stats li {{ margin-bottom: 6px; }}
    .hotel-smart-stats li:last-child {{ margin-bottom: 0; }}
    
    /* UI Huy hiệu nổi bật (Micro-badges) */
    .micro-badge {{ display: inline-block; padding: 4px 10px; margin-right: 6px; margin-bottom: 8px; border-radius: 12px; font-size: 12px; font-weight: 700; }}
    .badge-loc {{ background-color: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }}
    .badge-clean {{ background-color: #FEF08A; color: #B45309; border: 1px solid #FDE047; }}
    .badge-srv {{ background-color: #FCE7F3; color: #BE185D; border: 1px solid #FBCFE8; }}
    
    /* UI Thiết kế bản địa hiện đại (HTML5 Details/Summary) */
    details.modern-details {{ margin-top: 5px; margin-bottom: 10px; }}
    details.modern-details summary {{
        cursor: pointer; font-size: 13px; font-weight: 700; color: #0071C2;
        list-style: none; outline: none; padding: 5px 0; transition: color 0.2s;
    }}
    details.modern-details summary::-webkit-details-marker {{ display: none; }}
    details.modern-details summary:hover {{ color: #005eb8; }}
    details.modern-details[open] summary {{ color: #E11D48; }}
    
    .details-content {{
        font-size: 13px; color: #475569; line-height: 1.6; margin-top: 8px;
        padding: 12px; background-color: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;
        max-height: 150px; overflow-y: auto;
    }}
    
    .hotel-footer {{ margin-top: auto; padding-top: 15px; border-top: 1px dashed #E2E8F0; font-size: 13px; color: #008009; font-weight: 700;}}
    
    .stButton>button {{ background: #0071C2 !important; color: white !important; font-size: 16px !important; font-weight: 700 !important; border-radius: 8px !important; padding: 0.6rem 2rem !important; border: none !important; width: 100%; box-shadow: 0 4px 6px rgba(0,113,194,0.2) !important;}}
    .stButton>button:hover {{ background: #005eb8 !important; box-shadow: 0 6px 12px rgba(0,113,194,0.3) !important; }}
    .search-container {{ background: #FFFFFF; padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #EAEAEA;}}
    h1, h2, h3 {{ color: #003580; font-weight: 800; letter-spacing: -0.5px;}}
    
    .main-header {{ 
        {bg_img_css}
        background-size: cover;
        background-position: center;
        padding: 80px 20px; 
        border-radius: 16px; 
        margin-bottom: 30px; 
        color: white; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0);
    }}
    .main-header b {{ font-size: 16px; letter-spacing: 2px; text-transform: uppercase; color: #FFffff; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); margin-bottom: 10px; }}
    .main-header h1 {{ 
        color: white !important; 
        margin: 0 0 12px 0 !important; 
        font-size: 46px !important; 
        font-weight: 800 !important; 
        letter-spacing: 1px !important;
        text-transform: uppercase;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.6); 
    }}
    .main-header span {{ 
        font-size: 24px !important; 
        color: #F8FAFC; 
        font-weight: 600;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.6);
    }}
    
    .stPlotlyChart {{ background-color: #FFFFFF; border-radius: 12px; padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }}
    </style>
""", unsafe_allow_html=True)

# --- HÀM TẢI DỮ LIỆU VÀ MÔ HÌNH ---
# --- HÀM TẢI DỮ LIỆU VÀ MÔ HÌNH (ĐÃ FIX ABSOLUTE PATH) ---
@st.cache_data
def load_data():
    # Lấy đường dẫn tuyệt đối của thư mục chứa file app.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(BASE_DIR, 'data', 'hotel_info_cleaned.csv')
    
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    return pd.DataFrame()

@st.cache_resource
def load_models():
    # Lấy đường dẫn tuyệt đối của thư mục chứa file app.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    models_dict = {}
    model_files = ['gensim_dictionary.pkl', 'gensim_tfidf.pkl', 'gensim_index.pkl', 'surprise_svd.pkl', 'hotel_insights.pkl']
    
    for f_name in model_files:
        path = os.path.join(BASE_DIR, 'models', f_name)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                models_dict[f_name.split('.')[0]] = pickle.load(f)
        else:
            models_dict[f_name.split('.')[0]] = None
    return models_dict

df_info = load_data()
models = load_models()

def get_gensim_candidates(query, top_n=50):
    if models['gensim_dictionary'] is None: return []
    query_wt = ViTokenizer.tokenize(query.lower()).split()
    query_bow = models['gensim_dictionary'].doc2bow(query_wt)
    sim_scores = models['gensim_index'][models['gensim_tfidf'][query_bow]]
    top_indices = sorted(range(len(sim_scores)), key=lambda i: sim_scores[i], reverse=True)[:top_n]
    return top_indices

def check_user_exists(svd_model, user_id):
    if svd_model is None: return False
    try:
        svd_model.trainset.to_inner_uid(user_id)
        return True
    except ValueError:
        return False

def format_score(score_val):
    try:
        return f"{float(score_val):.1f}"
    except (ValueError, TypeError):
        return "N/A"

# --- SIDEBAR ---
st.sidebar.title("🌍 Agoda Platform")
st.sidebar.markdown("<br>", unsafe_allow_html=True)
menu = st.sidebar.radio("MENU CHÍNH", ("📖 Câu chuyện Dữ liệu", "📊 Đánh giá Thuật toán", "🏨 Nền tảng Gợi ý (Demo)"))
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="team-box">
    <b style="color: #FFD700; font-size: 15px;">👨‍💻 GIẢNG VIÊN HƯỚNG DẪN</b><br><br>
    <div style="font-size: 14px; font-weight: 600; line-height: 1.6;">
        Cô Khuất Thùy Phương
    </div>
</div>              

<div class="team-box">
    <b style="color: #FFD700; font-size: 15px;">👨‍💻 THÀNH VIÊN THỰC HIỆN</b><br><br>
    <div style="font-size: 14px; font-weight: 600; line-height: 1.6;">
        Học viên: <br>
        1. Phan Phúc Lộc<br>
        2. Nguyễn Nhật Trường
    </div>
</div>
""", unsafe_allow_html=True)

# --- HEADER CỐ ĐỊNH TRÊN CÙNG ---
st.markdown("""
<div class="main-header">
    <b>TRUNG TÂM TIN HỌC - ĐẠI HỌC KHOA HỌC TỰ NHIÊN TPHCM</b>
    <h1>🏨 Đồ án tốt nghiệp Data Science</h1>
    <span>Agoda Recommender System</span>
</div>
""", unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH ---
if menu == "📖 Câu chuyện Dữ liệu":
    st.markdown("""
    ### 🌍 Bối cảnh Thực tế
    **Agoda** phục vụ hàng triệu lượt tìm kiếm mỗi ngày. Hệ thống cần gợi ý thông minh để tối ưu hóa trải nghiệm khách hàng và giải quyết bài toán "Nghịch lý của sự lựa chọn" (Paradox of Choice).
    
    ### 🎯 Tầm nhìn Hệ thống
    1. **Recommender System:** Ứng dụng Kiến trúc Lai (Hybrid Pipeline) kết hợp sức mạnh phân tích Ngôn ngữ tự nhiên (NLP) và Lọc cộng tác (Collaborative Filtering) giải quyết triệt để Cold-Start.
    2. **Business Insights:** Bóc tách dữ liệu phản hồi giúp chủ khách sạn (Partners) định vị được chất lượng dịch vụ.
    """)

elif menu == "📊 Đánh giá Thuật toán":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#fff; padding:20px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border-top:4px solid #003580;">
        <h3 style="margin-top:0;">🤖 Collaborative Filtering</h3>
        <p><b>Thuật toán:</b> Surprise SVD & PySpark ALS</p>
        <p><b>Hiệu suất (RMSE):</b> SVD (0.9213) | ALS (0.9407)</p>
        <p><b>Xử lý Cold-start:</b> Lưới lọc an toàn (Safety Net) đẩy về Popularity Ranking khi phát hiện ID ảo.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#fff; padding:20px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border-top:4px solid #FF567D;">
        <h3 style="margin-top:0;">📝 Content-Based Filtering</h3>
        <p><b>Thuật toán:</b> Cosine Similarity & Gensim (TF-IDF)</p>
        <p><b>NLP:</b> Khử nhiễu văn bản sâu, tokenization tiếng Việt (PyVi).</p>
        <p><b>Mục tiêu:</b> Tạo rổ ứng viên (Candidate Generation) theo bối cảnh Real-time.</p>
        </div>
        """, unsafe_allow_html=True)

elif menu == "🏨 Nền tảng Gợi ý (Demo)":
    if df_info.empty:
        st.error("Không tìm thấy dữ liệu. Vui lòng kiểm tra thư mục 'data/'.")
        st.stop()
    
    all_insights = models.get('hotel_insights')
    insights_dict = all_insights.get('hotel_insights', {}) if all_insights else {}
        
    tab1, tab2, tab3 = st.tabs(["🔍 Tìm kiếm (CB)", "✨ Agoda Smart Recommend (Hybrid)", "📈 Partner Insights (Admin)"])

    # --- TAB 1: CB (TÌM KIẾM VÃNG LAI) ---
    with tab1:
        st.markdown("""<div class="search-container">
            <h4 style='margin-top:0; color:#003580;'>Bạn muốn đi đâu, trải nghiệm gì?</h4>
        </div>""", unsafe_allow_html=True)
        
        col_search, col_btn = st.columns([8, 2])
        with col_search:
            query_t1 = st.text_input("", placeholder="VD: Khách sạn 5 sao sang trọng gần biển...", key="q1", label_visibility="collapsed")
        with col_btn:
            btn_tab1 = st.button("Tìm phòng ngay")
            
        if btn_tab1:
            if query_t1:
                top_indices = get_gensim_candidates(query_t1, top_n=6)
                if top_indices:
                    st.markdown("<br><h4>💡 Kết quả nổi bật dành cho bạn:</h4>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    for i, idx in enumerate(top_indices):
                        hotel = df_info.iloc[idx]
                        h_id = hotel['Hotel_ID']
                        score_fmt = format_score(hotel.get('Total_Score', ''))
                        
                        raw_desc = str(hotel.get('Hotel_Description', 'Đang cập nhật thông tin mô tả cho khách sạn này.'))
                        desc = raw_desc.replace('\n', '<br>').strip()
                        
                        badges = []
                        if pd.to_numeric(hotel.get('Location', 0), errors='coerce') >= 9.0:
                            badges.append(f"<span class='micro-badge badge-loc'>📍 Vị trí {format_score(hotel.get('Location'))}</span>")
                        if pd.to_numeric(hotel.get('Cleanliness', 0), errors='coerce') >= 9.0:
                            badges.append(f"<span class='micro-badge badge-clean'>✨ Sạch sẽ {format_score(hotel.get('Cleanliness'))}</span>")
                        if pd.to_numeric(hotel.get('Service', 0), errors='coerce') >= 9.0:
                            badges.append(f"<span class='micro-badge badge-srv'>🤝 Dịch vụ {format_score(hotel.get('Service'))}</span>")
                        
                        badges_html = f"<div style='margin-bottom: 12px;'>{''.join(badges)}</div>" if badges else ""
                        
                        # --- FIX LỖI RENDER HTML: Gộp thành một chuỗi liên tục, không có khoảng trắng dư thừa ---
                        card_html = f"<div class='hotel-card'><div><div class='hotel-header'><div class='hotel-title'>{hotel['Hotel_Name']}</div><div class='hotel-score-badge'>⭐ {score_fmt}</div></div><div class='hotel-loc'>📍 {hotel.get('Hotel_Address', 'Vị trí đắc địa')}</div>{badges_html}<details class='modern-details'><summary>+ Xem chi tiết mô tả</summary><div class='details-content'>{desc}</div></details></div><div class='hotel-footer'>✓ Phù hợp với tìm kiếm của bạn</div></div>"
                        
                        with cols[i % 3]:
                            st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.error("Hệ thống AI đang khởi động, vui lòng thử lại sau.")
            else:
                st.warning("Vui lòng nhập bối cảnh chuyến đi của bạn.")

    # --- TAB 2: HYBRID RECOMMENDER CHUYÊN SÂU ---
    with tab2:
        st.markdown("""<div class="search-container">
            <h4 style='margin-top:0; color:#003580;'>🤖 Công cụ Đề xuất Đa tầng (Context-Aware)</h4>
            <p style='color:#666; font-size:14px;'>Hệ thống kết hợp nhu cầu hiện tại và sở thích lịch sử của bạn để đưa ra gợi ý chính xác nhất.</p>
        </div>""", unsafe_allow_html=True)
        
        col_q, col_u, col_b = st.columns([4, 4, 2])
        with col_q:
            hybrid_query = st.text_input("1. Tiêu chí chuyến đi (Tùy chọn):", placeholder="VD: yên tĩnh, có buffet sáng...")
        with col_u:
            hybrid_user = st.text_input("2. Mã thành viên Agoda (Tùy chọn):", placeholder="VD: 1_1_1 hoặc nhập mã ảo...")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            hybrid_pressed = st.button("Đề xuất Tối ưu")
            
        if hybrid_pressed:
            candidate_df = df_info.copy()
            candidate_df['Total_Score_Num'] = pd.to_numeric(candidate_df.get('Total_Score', 0), errors='coerce').fillna(0)
            
            if hybrid_query:
                cand_indices = get_gensim_candidates(hybrid_query, top_n=50)
                if cand_indices:
                    candidate_df = df_info.iloc[cand_indices].copy()
                    candidate_df['Total_Score_Num'] = pd.to_numeric(candidate_df.get('Total_Score', 0), errors='coerce').fillna(0)
            
            svd_model = models.get('surprise_svd')
            is_warm_start = False
            
            if hybrid_user and check_user_exists(svd_model, hybrid_user):
                is_warm_start = True
                candidate_ids = candidate_df['Hotel_ID'].tolist()
                predictions = [svd_model.predict(uid=hybrid_user, iid=hid) for hid in candidate_ids]
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_6_ids = [p.iid for p in predictions[:6]]
                
                final_df = candidate_df[candidate_df['Hotel_ID'].isin(top_6_ids)]
                final_df = final_df.set_index('Hotel_ID').loc[top_6_ids].reset_index()
                st.success(f"🎉 Chào mừng thành viên **{hybrid_user}**. Chúng tôi đã chuẩn bị danh sách theo đúng gu của bạn!")
                footer_text = "✓ Trùng khớp sở thích lịch sử"
            else:
                if hybrid_user:
                    st.warning(f"⚠️ Thành viên '{hybrid_user}' chưa có dữ liệu lịch sử. Chuyển sang Gợi ý Xu hướng.")
                else:
                    st.info("👋 Chào mừng bạn. Dưới đây là các lựa chọn hàng đầu hiện nay.")
                
                final_df = candidate_df.sort_values(by='Total_Score_Num', ascending=False).head(6)
                footer_text = "🔥 Đang thịnh hành trên hệ thống"

            cols = st.columns(3)
            for i, (_, hotel) in enumerate(final_df.iterrows()):
                with cols[i % 3]:
                    h_id = hotel['Hotel_ID']
                    score_fmt = format_score(hotel.get('Total_Score', ''))
                    
                    raw_desc = str(hotel.get('Hotel_Description', 'Đang cập nhật thông tin mô tả cho khách sạn này.'))
                    desc = raw_desc.replace('\n', '<br>').strip() 
                    
                    h_in = insights_dict.get(h_id, {})
                    match_str = ""
                    if is_warm_start:
                        est = svd_model.predict(uid=hybrid_user, iid=h_id).est
                        match_pct = (est / 10.0) * 100
                        match_str = f"<li>🔥 Phù hợp <b>{match_pct:.0f}%</b> với 'gu' của bạn</li>"
                    
                    rank_str = str(hotel.get('Hotel_Rank', '')).split(' ')[0]
                    rank_html = f"<li>🌟 <b>Phân khúc:</b> {rank_str} sao</li>" if rank_str and rank_str != 'nan' else ""
                    
                    group_dist = h_in.get('group_dist', {})
                    demo_str = f"<li>👨‍👩‍👧‍👦 Lựa chọn Top 1 của <b>{max(group_dist, key=group_dist.get)}</b></li>" if group_dist else ""
                    
                    smart_stats_html = f"<div class='hotel-smart-stats'><ul>{match_str}{rank_html}{demo_str}</ul></div>" if (match_str or rank_html or demo_str) else ""
                    
                    # --- FIX LỖI RENDER HTML TẠI TAB 2 ---
                    card_html = f"<div class='hotel-card'><div><div class='hotel-header'><div class='hotel-title'>{hotel['Hotel_Name']}</div><div class='hotel-score-badge'>⭐ {score_fmt}</div></div><div class='hotel-loc'>📍 {hotel.get('Hotel_Address','N/A')}</div>{smart_stats_html}<details class='modern-details'><summary>+ Xem chi tiết mô tả</summary><div class='details-content'>{desc}</div></details></div><div class='hotel-footer'>{footer_text}</div></div>"
                    
                    st.markdown(card_html, unsafe_allow_html=True)

    # --- TAB 3: ADMIN BÁO CÁO TOÀN DIỆN ---
    with tab3:
        st.subheader("Bảng điều khiển Báo cáo Quản trị (Dành cho Partner)")
        if 'admin_auth' not in st.session_state:
            st.session_state.admin_auth = False

        if not st.session_state.admin_auth:
            st.warning("🔒 Vui lòng xác thực quyền Quản trị viên.")
            col_pwd, col_login = st.columns([3, 2])
            with col_pwd:
                pwd = st.text_input("Mật khẩu:", type="password", label_visibility="collapsed", placeholder="Nhập mật khẩu(agoda2026)")
            with col_login:
                if st.button("Đăng nhập"):
                    if pwd == "agoda2026":
                        st.session_state.admin_auth = True
                        st.rerun()
                    else:
                        st.error("Sai mật khẩu!")
        else:
            col_msg, col_logout = st.columns([8, 2])
            with col_msg:
                st.success("✅ Xác thực thành công!")
            with col_logout:
                if st.button("🚪 Đăng xuất"):
                    st.session_state.admin_auth = False
                    st.rerun()
            
            st.markdown("---")
            hotel_names = df_info['Hotel_Name'].tolist()
            selected_name = st.selectbox("📌 Chọn Đối tác Khách sạn để phân tích:", hotel_names)
            selected_id = df_info[df_info['Hotel_Name'] == selected_name]['Hotel_ID'].values[0]
            
            if all_insights and selected_id in insights_dict:
                h_insight = insights_dict[selected_id]
                sys_avg = all_insights.get('system_averages', {})
                
                st.markdown(f"### 📊 Báo cáo Insights: **{selected_name}**")
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Tổng tương tác khách hàng", f"{h_insight.get('total_comments', 0):,} lượt")
                pos_val = h_insight.get('sentiment_pct', {}).get('Positive', 0)
                kpi2.metric("Tỷ lệ Hài lòng (Tích cực)", f"{pos_val:.1f}%")
                
                trend_data = h_insight.get('trend', {})
                if trend_data:
                    df_trend = pd.DataFrame(list(trend_data.items()), columns=['Tháng', 'Lượt đánh giá']).sort_values('Tháng')
                    fig_trend = px.line(df_trend, x='Tháng', y='Lượt đánh giá', title="Xu hướng đánh giá (12 tháng gần nhất)", markers=True, color_discrete_sequence=['#0071C2'])
                    st.plotly_chart(fig_trend, use_container_width=True)

                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    pcts = h_insight.get('sentiment_pct', {})
                    fig_pie = px.pie(values=list(pcts.values()), names=list(pcts.keys()), title="Thống kê Tỉ lệ Hài lòng", color_discrete_sequence=['#008009', '#FFB700', '#FF567D'])
                    fig_pie.update_traces(hole=0.4) 
                    st.plotly_chart(fig_pie, use_container_width=True)
                with c2:
                    cats = ['Location', 'Cleanliness', 'Service', 'Facilities', 'Value_for_money']
                    try:
                        target_rank = df_info[df_info['Hotel_ID']==selected_id]['Hotel_Rank'].values[0]
                        peer_df = df_info[df_info['Hotel_Rank'] == target_rank]
                        
                        h_vals = [pd.to_numeric(df_info[df_info['Hotel_ID']==selected_id][c].values[0], errors='coerce') for c in cats]
                        s_vals = [pd.to_numeric(peer_df[c], errors='coerce').mean() for c in cats]
                        
                        fig_bar = go.Figure(data=[
                            go.Bar(name='Cơ sở này', x=cats, y=h_vals, marker_color='#003580'),
                            go.Bar(name=f'Trung bình đối thủ ({target_rank})', x=cats, y=s_vals, marker_color='#38BDF8')
                        ])
                        fig_bar.update_layout(title="Benchmark Năng lực với Đối thủ Cùng Phân khúc", barmode='group')
                        st.plotly_chart(fig_bar, use_container_width=True)
                    except Exception:
                        st.warning("Thiếu dữ liệu chi tiết so sánh cho khách sạn này.")

                st.markdown("---")
                st.markdown("#### 🌍 Nhân khẩu học Khách hàng")
                c3, c4 = st.columns(2)
                with c3:
                    nat_dist = h_insight.get('nationality_dist', {})
                    if nat_dist:
                        df_nat = pd.DataFrame(list(nat_dist.items()), columns=['Quốc tịch', 'Số lượng']).sort_values('Số lượng', ascending=True)
                        fig_nat = px.bar(df_nat, x='Số lượng', y='Quốc tịch', orientation='h', title="Top 5 Quốc tịch", color_discrete_sequence=['#0071C2'])
                        st.plotly_chart(fig_nat, use_container_width=True)
                    else:
                        st.info("Chưa có dữ liệu Quốc tịch.")
                with c4:
                    grp_dist = h_insight.get('group_dist', {})
                    if grp_dist:
                        fig_grp = px.pie(values=list(grp_dist.values()), names=list(grp_dist.keys()), title="Thành phần Nhóm khách", color_discrete_sequence=px.colors.qualitative.Pastel)
                        st.plotly_chart(fig_grp, use_container_width=True)
                    else:
                        st.info("Chưa có dữ liệu Nhóm khách.")

                st.markdown("---")
                st.markdown("#### ☁️ Bóc tách Từ khóa Nhận xét (NLP)")
                c5, c6 = st.columns(2)
                with c5:
                    st.markdown("**✅ Điểm Sáng cần phát huy (Khách hàng khen ngợi)**")
                    pos_kw = h_insight.get('pos_keywords', {})
                    if pos_kw:
                        wordcloud_pos = WordCloud(width=600, height=400, background_color='white', colormap='viridis', max_words=60).generate_from_frequencies(pos_kw)
                        fig_wc_pos, ax = plt.subplots(figsize=(6, 4))
                        ax.imshow(wordcloud_pos, interpolation='bilinear')
                        ax.axis("off")
                        fig_wc_pos.patch.set_facecolor('white')
                        st.pyplot(fig_wc_pos)
                    else:
                        st.write("Không đủ dữ liệu từ khóa tích cực.")
                
                with c6:
                    st.markdown("**⚠️ Điểm cần quan tâm (Khách hàng phàn nàn/cần cải thiện)**")
                    neg_kw = h_insight.get('neg_keywords', {})
                    if neg_kw:
                        wordcloud_neg = WordCloud(width=600, height=400, background_color='white', colormap='magma', max_words=60).generate_from_frequencies(neg_kw)
                        fig_wc_neg, ax = plt.subplots(figsize=(6, 4))
                        ax.imshow(wordcloud_neg, interpolation='bilinear')
                        ax.axis("off")
                        fig_wc_neg.patch.set_facecolor('white')
                        st.pyplot(fig_wc_neg)
                    else:
                        st.success("Tuyệt vời! Khách sạn này không có điểm trừ nổi bật nào.")
            else:
                st.error("Chưa có dữ liệu Insights phân tích cho khách sạn này.")
