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
import datetime
import streamlit.components.v1 as components
import re

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Agoda AI Platform", page_icon="🌎", layout="wide")

# --- QUẢN LÝ TRẠNG THÁI ---
if 'search_step' not in st.session_state: st.session_state.search_step = 'search' 
if 'selected_hotel' not in st.session_state: st.session_state.selected_hotel = None
if 'has_searched' not in st.session_state: st.session_state.has_searched = False
if 'display_limit' not in st.session_state: st.session_state.display_limit = 5  
if 'chip_query' not in st.session_state: st.session_state.chip_query = ""

if 'num_rooms' not in st.session_state: st.session_state.num_rooms = 1
if 'num_adults' not in st.session_state: st.session_state.num_adults = 2
if 'num_children' not in st.session_state: st.session_state.num_children = 0
if 'booking_dates' not in st.session_state: st.session_state.booking_dates = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))
if 'num_nights' not in st.session_state: st.session_state.num_nights = 1

if 'ai_step' not in st.session_state: st.session_state.ai_step = 'search' 
if 'ai_selected_hotel' not in st.session_state: st.session_state.ai_selected_hotel = None
if 'ai_has_searched' not in st.session_state: st.session_state.ai_has_searched = False
if 'ai_display_limit' not in st.session_state: st.session_state.ai_display_limit = 5  
if 'ai_chip_query' not in st.session_state: st.session_state.ai_chip_query = ""
if 'ai_num_rooms' not in st.session_state: st.session_state.ai_num_rooms = 1
if 'ai_num_adults' not in st.session_state: st.session_state.ai_num_adults = 2
if 'ai_num_children' not in st.session_state: st.session_state.ai_num_children = 0
if 'ai_booking_dates' not in st.session_state: st.session_state.ai_booking_dates = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))
if 'ai_num_nights' not in st.session_state: st.session_state.ai_num_nights = 1

if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
if 'admin_owned_hotel' not in st.session_state: st.session_state.admin_owned_hotel = None

# --- HÀM LOAD ẢNH LOCAL ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(BASE_DIR, bin_file)
        with open(img_path, 'rb') as f: data = f.read()
        return base64.b64encode(data).decode()
    except Exception: return None

img_base64 = get_base64_of_bin_file('banner.jpg')
bg_img_css = f"background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('data:image/jpeg;base64,{img_base64}');" if img_base64 else "background: linear-gradient(135deg, #003580 0%, #0071C2 100%);"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; color: #2A2A2E; }}
    .stApp {{ background-color: #F7F9FA; }}
    [data-testid="stSidebar"] {{ background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; box-shadow: 2px 0 10px rgba(0,0,0,0.03);}}
    [data-testid="stSidebar"] h2 {{ color: #003580 !important; font-weight: 800 !important; font-size: 20px !important; letter-spacing: -0.5px;}}
    .stRadio label {{ font-size: 14.5px !important; font-weight: 600 !important; color: #475569 !important; cursor: pointer; padding: 4px 0;}}
    .team-box {{ background: linear-gradient(135deg, #003580 0%, #005eb8 100%); border-radius: 12px; padding: 20px; color: #FFFFFF !important; box-shadow: 0 10px 20px -5px rgba(0,53,128,0.3); margin-top: 20px;}}
    .main-header {{ {bg_img_css} background-size: cover; background-position: center; padding: 60px 20px; border-radius: 16px; margin-bottom: 30px; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
    .main-header b {{ font-size: 14px; letter-spacing: 2px; text-transform: uppercase; color: #FFD700; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); margin-bottom: 10px; }}
    .main-header h1 {{ color: white !important; margin: 0 0 10px 0 !important; font-size: 40px !important; font-weight: 800 !important; text-transform: uppercase; text-shadow: 2px 2px 8px rgba(0,0,0,0.6); }}
    
    .auth-card {{ background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; margin-bottom: 25px; }}
    .auth-card-guest {{ border-top: 4px solid #0071C2; }}
    .auth-card-member {{ border-top: 4px solid #E11D48; }}
    .auth-card-admin {{ border-top: 4px solid #059669; }}
    .auth-icon {{ font-size: 45px; margin-bottom: 10px; }}
    .auth-title {{ font-size: 22px; font-weight: 800; color: #003580; margin-bottom: 8px; }}
    .auth-desc {{ font-size: 14px; color: #64748B; margin-bottom: 15px; line-height: 1.5; }}
    
    .search-bar-wrap {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #E2E8F0;}}
    .filter-header {{ font-size: 15px; font-weight: 800; color: #2A2A2E; margin-top: 15px; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #E2E8F0;}}
    .hotel-list-card {{ display: flex; flex-direction: row; background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: all 0.3s ease; overflow: hidden; }}
    .checkout-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-bottom: 20px;}}
    .checkout-header {{ font-size: 18px; font-weight: 700; color: #003580; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0;}}
    .stButton>button {{ background: #5392F9 !important; color: white !important; font-size: 15px !important; font-weight: 700 !important; border-radius: 8px !important; padding: 0.5rem 1.5rem !important; border: none !important; width: 100%; box-shadow: 0 4px 6px rgba(0,113,194,0.2) !important; transition: 0.2s;}}
    .stButton>button:hover {{ background: #3B71CA !important; }}
    .chip-btn > button {{ background: transparent !important; color: #475569 !important; border: 1px solid #CBD5E1 !important; border-radius: 20px !important; font-size: 13px !important; padding: 0.2rem 0.8rem !important; margin-bottom: 8px !important; box-shadow: none !important;}}
    .chip-btn > button:hover {{ background: #F1F5F9 !important; border-color: #94A3B8 !important; }}
    .btn-load-more > button {{ background: #FFFFFF !important; color: #0071C2 !important; border: 1px solid #0071C2 !important; margin-top: 10px; }}
    
    .member-insight-box {{ background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%); border-left: 4px solid #E11D48; padding: 12px 15px; border-radius: 8px; margin-top: 12px; margin-bottom: 8px; }}
    .member-insight-title {{ font-size: 12px; font-weight: 800; color: #BE123C; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }}
    .member-insight-text {{ font-size: 13.5px; color: #881337; font-weight: 500; line-height: 1.4; }}
    
    .admin-card-title {{ font-size: 18px; font-weight: 800; color: #003580; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; margin-top: 20px; }}
    .alert-box {{ background: #FEF2F2; border-left: 4px solid #EF4444; padding: 15px; border-radius: 4px; margin-bottom: 15px; }}
    .rec-box {{ background: #F0FDF4; border-left: 4px solid #10B981; padding: 15px; border-radius: 4px; margin-bottom: 15px; }}
    
    /* FOOTER CSS */
    .footer-container {{ text-align: center; color: #94A3B8; font-size: 14px; margin-top: 60px; padding-top: 20px; padding-bottom: 20px; border-top: 1px solid #E2E8F0; font-weight: 500; letter-spacing: 0.5px; }}
    </style>
""", unsafe_allow_html=True)

# --- THUẬT TOÁN ĐỊNH GIÁ ĐỘNG (DYNAMIC PRICING) ---
def get_dynamic_price(base_price, start_date, nights, rooms):
    total = 0
    surge_applied = False
    for i in range(nights):
        current_date = start_date + datetime.timedelta(days=i)
        if current_date.weekday() in [4, 5]: # Thứ 6, Thứ 7
            total += base_price * 1.15
            surge_applied = True
        else: total += base_price
    return int(total * rooms), surge_applied

# --- HÀM TẢI DỮ LIỆU & MOCK DATA TỈNH THÀNH ---
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    info_path = os.path.join(BASE_DIR, 'data', 'hotel_info_cleaned.csv')
    comments_path = os.path.join(BASE_DIR, 'data', 'hotel_comments_cleaned.csv')
    
    df_info = pd.read_csv(info_path) if os.path.exists(info_path) else pd.DataFrame()
    df_comments = pd.read_csv(comments_path) if os.path.exists(comments_path) else pd.DataFrame()
    
    if not df_comments.empty and 'Sentiment' not in df_comments.columns and 'Score Level' in df_comments.columns:
        score_level_to_sentiment = {'Hài Lòng': 'Negative', 'Rất tốt': 'Neutral', 'Tuyệt vời': 'Positive', 'Trên cả tuyệt vời': 'Positive'}
        df_comments['Sentiment'] = df_comments['Score Level'].map(score_level_to_sentiment).fillna('Neutral')
        
    if not df_info.empty:
        def extract_city(address):
            if pd.isna(address): return "Khác"
            addr = str(address).lower()
            if 'nha trang' in addr: return 'Nha Trang'
            elif 'cam ranh' in addr: return 'Cam Ranh'
            elif 'phú quốc' in addr: return 'Phú Quốc'
            elif 'đà lạt' in addr: return 'Đà Lạt'
            elif 'hồ chí minh' in addr or 'saigon' in addr: return 'TP. Hồ Chí Minh'
            else:
                parts = str(address).split(',')
                if len(parts) >= 3: return parts[-3].strip() if 'việt' in parts[-2].lower() or 'viet' in parts[-2].lower() else parts[-2].strip()
                return "Khác"
        df_info['City_Region'] = df_info['Hotel_Address'].apply(extract_city)
        
        def extract_type(name):
            if pd.isna(name): return "Khách sạn"
            n = str(name).lower()
            if 'resort' in n or 'nghỉ dưỡng' in n: return "Resort / Khu nghỉ dưỡng"
            elif 'căn hộ' in n or 'apartment' in n or 'studio' in n: return "Căn hộ / Studio"
            else: return "Khách sạn"
        df_info['Acc_Type'] = df_info['Hotel_Name'].apply(extract_type)
        
        def extract_amenities(desc):
            d = str(desc).lower()
            pool = any(k in d for k in ['hồ bơi', 'bể bơi', 'pool', 'swimming'])
            free_cancel = any(k in d for k in ['hủy', 'hoàn tiền', 'cancellation'])
            pay_later = any(k in d for k in ['thanh toán tại', 'trả tiền liền', 'pay later', 'không cần thẻ'])
            return pd.Series([pool, free_cancel, pay_later])
        df_info[['Has_Pool', 'Free_Cancel', 'Pay_Later']] = df_info['Hotel_Description'].apply(extract_amenities)

        def estimate_price(row):
            try: star = float(str(row.get('Hotel_Rank', '3')).split(' ')[0])
            except: star = 3.0
            try: score = float(str(row.get('Total_Score', '8.0')).replace(',', '.'))
            except: score = 8.0
            star_base = {5: 2500000, 4: 1200000, 3: 600000, 2: 400000, 1: 300000}
            base = star_base.get(int(star), 500000)
            price = base + (score * 50000) + (len(str(row.get('Hotel_Name',''))) * 8000)
            return int(round(price / 10000) * 10000)
        df_info['Data_Price'] = df_info.apply(estimate_price, axis=1)
        
        np.random.seed(42)
        df_info['Max_Guests'] = np.random.randint(2, 13, df_info.shape[0]) 
        df_info['Total_Rooms'] = np.random.randint(50, 300, df_info.shape[0])
    
    return df_info, df_comments

@st.cache_resource
def load_models():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    models_dict = {}
    model_files = ['gensim_dictionary.pkl', 'gensim_tfidf.pkl', 'gensim_index.pkl', 'surprise_svd.pkl', 'hotel_insights.pkl']
    for f_name in model_files:
        path = os.path.join(BASE_DIR, 'models', f_name)
        if os.path.exists(path):
            with open(path, 'rb') as f: models_dict[f_name.split('.')[0]] = pickle.load(f)
        else: models_dict[f_name.split('.')[0]] = None
    return models_dict

df_info, df_comments = load_data()
models = load_models()

def extract_intent(query):
    query_lower = str(query).lower()
    star_match = re.search(r'([1-5])\s*sao', query_lower)
    return star_match.group(1) if star_match else None

# --- LÕI TÌM KIẾM (HYBRID SEARCH ENGINE) ---
def get_gensim_candidates(query, top_n=100, threshold=0.02):
    if models['gensim_dictionary'] is None: return list(range(len(df_info)))
    clean_query = re.sub(r'([1-5])\s*sao', '', str(query).lower()).strip()
    if not clean_query: return list(range(len(df_info)))
        
    query_wt = ViTokenizer.tokenize(clean_query).split()
    query_bow = models['gensim_dictionary'].doc2bow(query_wt)
    nlp_indices = []
    if query_bow:
        sim_scores = models['gensim_index'][models['gensim_tfidf'][query_bow]]
        valid_items = [(i, score) for i, score in enumerate(sim_scores) if score >= threshold]
        top_items = sorted(valid_items, key=lambda x: x[1], reverse=True)[:top_n]
        nlp_indices = [item[0] for item in top_items]
        
    text_indices = []
    query_words = [w for w in clean_query.split() if len(w) > 2]
    
    for idx, row in df_info.iterrows():
        h_name = str(row.get('Hotel_Name', '')).lower()
        if (len(h_name) > 5 and h_name in clean_query) or (clean_query in h_name):
            text_indices.insert(0, idx) 
            continue
        if not query_words: continue
        match_count = sum(1 for w in query_words if w in h_name)
        if match_count >= min(2, len(query_words)):
            text_indices.append(idx)
        elif match_count == 1 and len(query_words) == 1:
            text_indices.append(idx)
            
    combined = []
    for idx in text_indices:
        if idx not in combined: combined.append(idx)
    for idx in nlp_indices:
        if idx not in combined: combined.append(idx)
        
    return combined[:top_n]

def check_user_exists(svd_model, user_id):
    if svd_model is None: return False
    try:
        svd_model.trainset.to_inner_uid(user_id)
        return True
    except ValueError: return False

def get_score_text(score_str):
    try:
        s = float(score_str.replace(',', '.'))
        if s >= 9.0: return "Tuyệt hảo"
        elif s >= 8.0: return "Rất tốt"
        elif s >= 7.0: return "Tốt"
        else: return "Đạt"
    except: return "Đánh giá"

def get_stars_icon(rank_str):
    try: return "⭐" * int(float(str(rank_str).split(' ')[0]))
    except: return "✨"

def match_star(rank_str, target_star):
    try: return int(float(str(rank_str).split(' ')[0])) == int(target_star)
    except: return False

def render_text_stats(kw_dict, color_hex):
    if not kw_dict: return "<span style='color:#666; font-size:13px;'>Không đủ dữ liệu văn bản.</span>"
    total = sum(kw_dict.values())
    top_kws = sorted(kw_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    html_out = ""
    for kw, count in top_kws:
        pct = (count / total) * 100
        html_out += f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; color: #334155;">
                <span style="font-weight: 600;">{kw.capitalize()}</span>
                <span>{pct:.1f}% ({count})</span>
            </div>
            <div style="width: 100%; background-color: #F1F5F9; border-radius: 4px; height: 8px;">
                <div style="width: {pct}%; background-color: {color_hex}; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """
    return html_out

# --- HÀM TẠO DỮ LIỆU ADMIN TỔNG HỢP ---
def prepare_admin_reviews(hotel_id, df_comments):
    h_revs = df_comments[df_comments['Hotel ID'] == hotel_id].copy()
    if h_revs.empty: return h_revs
    
    seed_val = sum(ord(c) for c in str(hotel_id))
    np.random.seed(42 + seed_val) 
    
    random_days = np.random.randint(0, 365, size=len(h_revs))
    base_date = pd.to_datetime('2026-08-01')
    h_revs['Ngày Checkout'] = [base_date - pd.Timedelta(days=int(d)) for d in random_days]
    h_revs['Ngày Nhận Phòng'] = h_revs['Ngày Checkout'] - pd.to_timedelta(np.random.randint(1, 5, size=len(h_revs)), unit='d')
    h_revs['Trạng thái'] = np.random.choice(['Đã hoàn tất', 'Đã hoàn tất', 'Đã hủy', 'No Show'], len(h_revs), p=[0.7, 0.15, 0.1, 0.05])
    h_revs['Doanh Thu'] = h_revs['Score'] * 250000 * np.random.randint(1, 4, size=len(h_revs))
    
    cities = ['TP. Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'Khác']
    probs = [0.4, 0.3, 0.1, 0.05, 0.05, 0.1]
    
    is_vn = h_revs['Nationality'].astype(str).str.contains('Viet|Việt', case=False, na=False)
    random_cities = np.random.choice(cities, size=len(h_revs), p=probs)
    h_revs['Guest_City'] = np.where(is_vn, random_cities, 'Quốc tế')
    
    def categorize_score(s):
        if s >= 9: return "Tuyệt vời (9-10)"
        elif s >= 8: return "Rất tốt (8-8.9)"
        elif s >= 7: return "Tốt (7-7.9)"
        else: return "Cần cải thiện (<7)"
    h_revs['Phân khúc điểm'] = pd.to_numeric(h_revs['Score']).apply(categorize_score)
    return h_revs


# ==========================================
# CẤU TRÚC MENU MỚI (TỐI ƯU UX)
# ==========================================
st.sidebar.title("🌍 Agoda AI Platform")
menu = st.sidebar.radio("MENU ĐIỀU HƯỚNG", (
    "🔍 Khám phá Khách sạn", 
    "💎 Gợi ý Cá nhân hóa", 
    "🏢 Trung tâm Đối tác", 
    "🎓 Giới thiệu Đồ án"
))

# Khôi phục thông tin Giảng viên và Nhóm trên Sidebar
st.sidebar.markdown("""
<div class="team-box">
    <b style="color: #FFD700; font-size: 13px;">👨‍💻 GV HƯỚNG DẪN</b><br>
    <div style="font-size: 13.5px; font-weight: 600; margin-top:5px;">Cô Khuất Thùy Phương</div>
</div>              
<div class="team-box">
    <b style="color: #FFD700; font-size: 13px;">👨‍💻 NHÓM THỰC HIỆN</b><br>
    <div style="font-size: 13.5px; font-weight: 600; margin-top:5px;">1. Phan Phúc Lộc<br>2. Nguyễn Nhật Trường</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <b>TRUNG TÂM TIN HỌC - ĐH KHOA HỌC TỰ NHIÊN TPHCM</b>
    <h1>Agoda Recommender System</h1>
    <span>Nền tảng Gợi ý & Phân tích Dữ liệu Khách sạn</span>
</div>
""", unsafe_allow_html=True)

if df_info.empty or df_comments.empty:
    st.error("Không tìm thấy dữ liệu. Vui lòng kiểm tra lại cấu trúc GitHub.")
    st.stop()

all_insights = models.get('hotel_insights')
insights_dict = all_insights.get('hotel_insights', {}) if all_insights else {}


# ==========================================
# MENU 1: KHÁM PHÁ KHÁCH SẠN (GUEST)
# ==========================================
if menu == "🔍 Khám phá Khách sạn":
    if st.session_state.search_step == 'search':
        st.markdown("""
        <div class="auth-card auth-card-guest">
            <div class="auth-icon">🍳</div>
            <div class="auth-title">Khám phá Khách sạn Toàn quốc</div>
            <div class="auth-desc">Tìm kiếm linh hoạt, thông minh với hàng ngàn ưu đãi dành cho khách vãng lai.</div>
        </div>
        """, unsafe_allow_html=True)
        
        ch1, ch2, ch3, ch4, ch5 = st.columns([1.5, 1.5, 1.8, 1.5, 3])
        def set_chip(q): st.session_state.chip_query = q
        with ch1: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("🌊 Gần biển", on_click=set_chip, args=("gần biển",)); st.markdown('</div>', unsafe_allow_html=True)
        with ch2: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("⭐ Khách sạn 5 sao", on_click=set_chip, args=("khách sạn 5 sao",)); st.markdown('</div>', unsafe_allow_html=True)
        with ch3: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("🍳 Có buffet sáng", on_click=set_chip, args=("buffet sáng",)); st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="search-bar-wrap">', unsafe_allow_html=True)
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 2.5, 1.5])
            with sc1:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Nhập nhu cầu tự do:</div>", unsafe_allow_html=True)
                search_query_free = st.text_input("Nhu cầu", value=st.session_state.chip_query, placeholder="VD: Panorama Nha Trang sang trọng...", label_visibility="collapsed")
                ai_tags = st.multiselect("Gợi ý AI", ["Gần trung tâm", "Yên tĩnh", "Sang trọng", "View đẹp", "Sạch sẽ", "Spa"], placeholder="💡 Chọn nhanh từ khóa...", label_visibility="collapsed")
                full_search_query = search_query_free + " " + " ".join(ai_tags)
                full_search_query = full_search_query.strip()
            with sc2:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Thời gian:</div>", unsafe_allow_html=True)
                dates = st.date_input("Thời gian", value=st.session_state.booking_dates, label_visibility="collapsed")
            with sc3:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Số lượng phòng & khách:</div>", unsafe_allow_html=True)
                popover_label = f"👥 {st.session_state.num_adults} NL, {st.session_state.num_children} TE — 🛏️ {st.session_state.num_rooms} Ph"
                with st.popover(popover_label, use_container_width=True):
                    st.session_state.num_rooms = st.number_input("Phòng", min_value=1, max_value=10, value=st.session_state.num_rooms, step=1)
                    st.session_state.num_adults = st.number_input("Người lớn", min_value=1, max_value=20, value=st.session_state.num_adults, step=1)
                    st.session_state.num_children = st.number_input("Trẻ em", min_value=0, max_value=10, value=st.session_state.num_children, step=1)
            with sc4: 
                st.markdown("<div style='margin-bottom:23px;'></div>", unsafe_allow_html=True)
                if st.button("TÌM KHÁCH SẠN"):
                    st.session_state.has_searched = True
                    st.session_state.display_limit = 5
                    if len(dates) == 2:
                        st.session_state.booking_dates = dates
                        st.session_state.num_nights = max(1, (dates[1] - dates[0]).days)
                    else: st.session_state.num_nights = 1
            st.markdown('</div></div><br>', unsafe_allow_html=True)

        col_filter, col_results = st.columns([1, 3])
        required_guests = st.session_state.num_adults + st.session_state.num_children
        required_rooms = st.session_state.num_rooms
        num_nights = st.session_state.num_nights
        checkin_date = st.session_state.booking_dates[0]
        
        with col_filter:
            available_cities = ["Tất cả"] + sorted(list(set(df_info['City_Region'].dropna().unique())))
            st.markdown("<div class='filter-header'>Bản đồ (Google Maps)</div>", unsafe_allow_html=True)
            loc_filter = st.selectbox("Khu vực / Tỉnh thành:", available_cities, label_visibility="collapsed")
            map_target = loc_filter if loc_filter != "Tất cả" else "Việt Nam"
            components.html(f"""<iframe width="100%" height="200" style="border:0; border-radius:8px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q={map_target}&hl=vi&z=11&output=embed"></iframe>""", height=200)
            
            st.markdown("<div class='filter-header'>Hạng Sao</div>", unsafe_allow_html=True)
            star_filter_ui = st.selectbox("Lọc hạng sao:", ["Tất cả", "5 sao", "4 sao", "3 sao", "Dưới 3 sao"], label_visibility="collapsed")
            st.markdown("<div class='filter-header'>Giá mỗi đêm</div>", unsafe_allow_html=True)
            price_range = st.slider("Giá", min_value=0, max_value=5000000, value=(0, 5000000), step=100000, label_visibility="collapsed")
            st.markdown("<div class='filter-header'>Tiện ích</div>", unsafe_allow_html=True)
            filter_cancel = st.checkbox("Có nhắc 'Hủy miễn phí'")
            filter_paylater = st.checkbox("Có nhắc 'Thanh toán tại chỗ'")
            filter_pool = st.checkbox("Có nhắc 'Hồ bơi'")
            st.markdown("<div class='filter-header'>Loại hình</div>", unsafe_allow_html=True)
            filter_hotel = st.checkbox("Khách sạn", value=True)
            filter_resort = st.checkbox("Resort / Khu nghỉ dưỡng", value=True)
            filter_apt = st.checkbox("Căn hộ / Studio", value=True)

        with col_results:
            if st.session_state.has_searched:
                if not full_search_query: st.warning("Vui lòng nhập bối cảnh tìm kiếm.")
                else:
                    with st.spinner("🤖 Đang quét phòng & trích xuất ý định..."):
                        star_intent = extract_intent(full_search_query)
                        top_indices = get_gensim_candidates(full_search_query, top_n=100, threshold=0.02)
                        
                        if not top_indices: st.error(f"⚠️ Không tìm thấy cơ sở lưu trú nào liên quan đến '{full_search_query}'.")
                        else:
                            df_res = df_info.iloc[top_indices].copy()
                            if star_intent:
                                df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: match_star(x, star_intent))]
                                st.success(f"🤖 Đã nhận diện ý định: Chỉ lọc Khách sạn **{star_intent} sao**.")
                            elif star_filter_ui != "Tất cả":
                                star_num = star_filter_ui.split(' ')[0]
                                if star_num.isdigit(): df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: match_star(x, star_num))]
                                else: df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: int(float(str(x).split(' ')[0])) < 3 if pd.notna(x) else False)]
                            
                            if loc_filter != "Tất cả": df_res = df_res[df_res['City_Region'] == loc_filter]
                            df_res = df_res[(df_res['Data_Price'] >= price_range[0]) & (df_res['Data_Price'] <= price_range[1])]
                            df_res = df_res[df_res['Max_Guests'] >= (required_guests / required_rooms)]
                            
                            if filter_cancel: df_res = df_res[df_res['Free_Cancel'] == True]
                            if filter_paylater: df_res = df_res[df_res['Pay_Later'] == True]
                            if filter_pool: df_res = df_res[df_res['Has_Pool'] == True]
                            
                            allowed_types = []
                            if filter_hotel: allowed_types.append("Khách sạn")
                            if filter_resort: allowed_types.append("Resort / Khu nghỉ dưỡng")
                            if filter_apt: allowed_types.append("Căn hộ / Studio")
                            df_res = df_res[df_res['Acc_Type'].isin(allowed_types)]
                            
                            total_found = len(df_res)
                            if total_found == 0: st.info("Không tìm thấy kết quả phù hợp.")
                            else:
                                st.markdown(f"<h5 style='color:#003580;'>Tìm thấy {total_found} cơ sở lưu trú phù hợp</h5>", unsafe_allow_html=True)
                                df_to_show = df_res.head(st.session_state.display_limit)
                                
                                for i, (_, hotel) in enumerate(df_to_show.iterrows()):
                                    with st.container(border=True):
                                        cc1, cc2, cc3 = st.columns([1.5, 2.5, 1.2])
                                        with cc1: st.image(f"https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80&sig={i}", use_container_width=True)
                                        with cc2:
                                            stars = get_stars_icon(hotel.get('Hotel_Rank', ''))
                                            st.markdown(f"<div style='font-size:18px; font-weight:800; color:#003580; margin-bottom:5px;'>{hotel['Hotel_Name']} {stars}</div>", unsafe_allow_html=True)
                                            st.markdown(f"<div style='font-size:13px; color:#0071C2;'>📍 {hotel.get('Hotel_Address', 'N/A')}</div>", unsafe_allow_html=True)
                                            with st.expander("📝 Xem mô tả"): st.write(str(hotel.get('Hotel_Description', 'Đang cập nhật...')))
                                        with cc3:
                                            score_str = str(hotel.get('Total_Score', 'N/A')).replace(',', '.')
                                            total_calculated_price, is_surge = get_dynamic_price(hotel['Data_Price'], checkin_date, num_nights, required_rooms)
                                            
                                            st.markdown(f"""
                                            <div style='text-align:right;'>
                                                <span style='font-weight:bold; color:#003580;'>{get_score_text(score_str)}</span> 
                                                <span style='background:#003580; color:white; padding:4px 8px; border-radius:6px; font-weight:bold;'>{score_str}</span>
                                            </div>
                                            <div style='text-align:right; margin-top:15px; margin-bottom:10px;'>
                                            """, unsafe_allow_html=True)
                                            if is_surge: st.markdown("<div style='font-size:11px; color:#E11D48; font-weight:bold; margin-bottom:2px;'>⚡ Tăng giá: Cuối tuần</div>", unsafe_allow_html=True)
                                            st.markdown(f"""
                                                <div style='font-size:12px; color:#666;'>Giá {required_rooms} phòng, {num_nights} đêm</div>
                                                <div style='font-size:22px; font-weight:800; color:#E11D48;'>{total_calculated_price:,} đ</div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            def go_detail(h_dict, price_calc):
                                                st.session_state.selected_hotel = h_dict
                                                st.session_state.calculated_price = price_calc
                                                st.session_state.search_step = 'detail'
                                            st.button("Xem chi tiết", key=f"view_{hotel['Hotel_ID']}", on_click=go_detail, args=(hotel.to_dict(), total_calculated_price))

                                if st.session_state.display_limit < total_found:
                                    st.markdown('<div class="btn-load-more">', unsafe_allow_html=True)
                                    if st.button("🔽 Xem thêm 5 cơ sở khác", use_container_width=True):
                                        st.session_state.display_limit += 5
                                        st.rerun()
                                    st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.search_step == 'detail':
        hotel = st.session_state.selected_hotel
        total_price = st.session_state.calculated_price
        
        st.button("← Quay lại Kết quả", on_click=lambda: st.session_state.update(search_step='search'))
        stars = get_stars_icon(hotel.get('Hotel_Rank', ''))
        st.markdown(f"<h2>{hotel['Hotel_Name']} {stars}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:15px; color:#555; margin-bottom:20px;'>📍 {hotel.get('Hotel_Address', '')}</div>", unsafe_allow_html=True)
        
        cd1, cd2 = st.columns([2, 1])
        with cd1:
            st.image("https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", use_container_width=True)
            st.markdown("### 📝 Giới thiệu Khách sạn")
            st.info(hotel.get('Hotel_Description', 'Đang cập nhật...'))
            st.markdown("### 💬 Đánh giá thực tế từ Khách hàng")
            hotel_reviews = df_comments[df_comments['Hotel ID'] == hotel['Hotel_ID']]
            if hotel_reviews.empty: st.warning("Chưa có đánh giá nào.")
            else:
                top_reviews = hotel_reviews.sort_values(by='Score', ascending=False).head(4)
                for _, rev in top_reviews.iterrows():
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border-left:4px solid #0071C2; padding:15px; margin-bottom:10px; border-radius:4px;">
                        <span style="background:#003580; color:white; padding:3px 8px; border-radius:6px; font-weight:bold; margin-right:10px;">{rev['Score']}</span>
                        <span style="font-weight:bold; color:#333;">{get_score_text(str(rev['Score']))}</span><br>
                        <div style="font-size:14px; color:#444; margin-top:8px;">"{rev.get('Body', '')}"</div>
                        <div style="font-size:12px; color:#888; margin-top:5px;">👤 {rev.get('Nationality', 'Ẩn danh')} • {rev.get('Group Name', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        with cd2:
            st.markdown(f"""
            <div class='checkout-box'>
                <div style='font-size:14px; color:#666;'>Giá cho {st.session_state.num_rooms} phòng, {st.session_state.num_nights} đêm</div>
                <div style='font-size:24px; font-weight:bold; color:#E11D48; margin-bottom:5px;'>{total_price:,} đ</div>
                <div style='color:#008009; font-size:14px; font-weight:bold; margin-bottom:15px;'>✓ Đã bao gồm thuế và phí</div>
            """, unsafe_allow_html=True)
            st.button("TIẾN HÀNH ĐẶT PHÒNG", use_container_width=True, on_click=lambda: st.session_state.update(search_step='checkout'))
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.search_step == 'checkout':
        hotel = st.session_state.selected_hotel
        total_price = st.session_state.calculated_price
        
        st.button("← Quay lại Trang Chi tiết", on_click=lambda: st.session_state.update(search_step='detail'))
        st.markdown(f"## Hoàn tất thủ tục đặt phòng")
        col_form, col_summary = st.columns([2, 1])
        with col_form:
            st.markdown("<div class='checkout-box'><div class='checkout-header'>Thông tin Khách chính</div>", unsafe_allow_html=True)
            f1, f2 = st.columns(2)
            f1.text_input("Tên *")
            f2.text_input("Họ *")
            f3, f4 = st.columns(2)
            f3.text_input("Email *")
            f4.text_input("Số điện thoại *")
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("CHỐT ĐẶT PHÒNG", use_container_width=True):
                st.balloons(); st.success("🎉 Đặt phòng vãng lai thành công!")

        with col_summary:
            booking_dates = st.session_state.booking_dates
            checkin_str = booking_dates[0].strftime("%d/%m/%Y")
            checkout_str = booking_dates[1].strftime("%d/%m/%Y") if len(booking_dates) > 1 else (booking_dates[0] + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
            st.markdown(f"""
            <div class='checkout-box'>
                <img src='https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80' style='width:100%; border-radius:8px; margin-bottom:15px;'>
                <div style='font-size:18px; font-weight:800; color:#003580; margin-bottom:10px;'>{hotel['Hotel_Name']}</div>
                <div style='background:#E0F2FE; color:#0369A1; padding:10px; border-radius:6px; font-size:13px; margin-bottom:15px;'><b>Nhận phòng:</b> 14:00 - {checkin_str}<br><b>Trả phòng:</b> 12:00 - {checkout_str}<br></div>
                <div class='checkout-header' style='font-size:16px;'>Chi tiết giá ({st.session_state.num_rooms} phòng x {st.session_state.num_nights} đêm)</div>
                <div style='display:flex; justify-content:space-between; margin-bottom: 8px; color: #475569; font-size: 14px;'><span>Tiền phòng</span> <span>{int(total_price):,} đ</span></div>
                <div style='display:flex; justify-content:space-between; margin-bottom: 8px; color: #475569; font-size: 14px;'><span>Thuế và phí (10%)</span> <span>{int(total_price * 0.1):,} đ</span></div>
                <div style='display:flex; justify-content:space-between; margin-top:15px; border-top:1px dashed #ccc; padding-top:10px; font-size:20px; font-weight:bold; color:#E11D48;'><span>TỔNG CỘNG</span> <span>{int(total_price * 1.1):,} đ</span></div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# MENU 2: ĐẶC QUYỀN THÀNH VIÊN (AI)
# ==========================================
elif menu == "💎 Gợi ý Cá nhân hóa":
    if st.session_state.ai_step == 'search':
        st.markdown("""
        <div class="auth-card auth-card-member">
            <div class="auth-icon">💎</div>
            <div class="auth-title">Gợi ý cá nhân hóa Nhóm thành viên</div>
            <div class="auth-desc">Hệ thống AI sẽ cá nhân hóa đề xuất (CF+CB) và cung cấp các báo cáo Insight dựa trên phân tích cộng đồng có cùng "gu" du lịch với bạn.</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_gap1, c_input, c_gap2 = st.columns([1, 2, 1])
        with c_input:
            hybrid_user = st.text_input("Mã Thành viên (Reviewer ID):", placeholder="ID: 341_12, 1142_11...", value="341_12", label_visibility="collapsed")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        ch1, ch2, ch3, ch4, ch5 = st.columns([1.5, 1.5, 1.8, 1.5, 3])
        def set_ai_chip(q): st.session_state.ai_chip_query = q
        with ch1: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("🌊 Gần biển", key="ai_c1", on_click=set_ai_chip, args=("gần biển",)); st.markdown('</div>', unsafe_allow_html=True)
        with ch2: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("⭐ Khách sạn 5 sao", key="ai_c2", on_click=set_ai_chip, args=("khách sạn 5 sao",)); st.markdown('</div>', unsafe_allow_html=True)
        with ch3: st.markdown('<div class="chip-btn">', unsafe_allow_html=True); st.button("🍳 Có buffet sáng", key="ai_c3", on_click=set_ai_chip, args=("buffet sáng",)); st.markdown('</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="search-bar-wrap">', unsafe_allow_html=True)
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 2.5, 1.5])
            with sc1:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Nhập nhu cầu hiện tại (Tuỳ chọn):</div>", unsafe_allow_html=True)
                search_query_free = st.text_input("Nhu cầu", value=st.session_state.ai_chip_query, placeholder="VD: Panorama Nha Trang sang trọng...", label_visibility="collapsed")
                ai_tags = st.multiselect("Gợi ý AI", ["Trung tâm", "Yên tĩnh", "Sang trọng", "View đẹp", "Sạch sẽ"], placeholder="💡 Chọn nhanh từ khóa...", label_visibility="collapsed")
                full_search_query = search_query_free + " " + " ".join(ai_tags)
                full_search_query = full_search_query.strip()
            with sc2:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Thời gian:</div>", unsafe_allow_html=True)
                dates = st.date_input("Thời gian (AI)", value=st.session_state.ai_booking_dates, label_visibility="collapsed")
            with sc3:
                st.markdown("<div style='font-size:12px; color:#555; font-weight:bold; margin-bottom:5px;'>Số lượng phòng & khách:</div>", unsafe_allow_html=True)
                popover_label = f"👥 {st.session_state.ai_num_adults} NL, {st.session_state.ai_num_children} TE — 🛏️ {st.session_state.ai_num_rooms} Ph"
                with st.popover(popover_label, use_container_width=True):
                    st.session_state.ai_num_rooms = st.number_input("Phòng (AI)", min_value=1, max_value=10, value=st.session_state.ai_num_rooms, step=1)
                    st.session_state.ai_num_adults = st.number_input("Người lớn (AI)", min_value=1, max_value=20, value=st.session_state.ai_num_adults, step=1)
                    st.session_state.ai_num_children = st.number_input("Trẻ em (AI)", min_value=0, max_value=10, value=st.session_state.ai_num_children, step=1)
            with sc4: 
                st.markdown("<div style='margin-bottom:23px;'></div>", unsafe_allow_html=True)
                if st.button("ĐỀ XUẤT (AI)", key="ai_search_btn"):
                    st.session_state.ai_has_searched = True
                    st.session_state.ai_display_limit = 5
                    if len(dates) == 2:
                        st.session_state.ai_booking_dates = dates
                        st.session_state.ai_num_nights = max(1, (dates[1] - dates[0]).days)
                    else: st.session_state.ai_num_nights = 1
            st.markdown('</div></div><br>', unsafe_allow_html=True)

        col_filter, col_results = st.columns([1, 3])
        required_guests = st.session_state.ai_num_adults + st.session_state.ai_num_children
        required_rooms = st.session_state.ai_num_rooms
        num_nights = st.session_state.ai_num_nights
        checkin_date = st.session_state.ai_booking_dates[0]
        
        with col_filter:
            available_cities = ["Tất cả"] + sorted(list(set(df_info['City_Region'].dropna().unique())))
            st.markdown("<div class='filter-header'>Bản đồ (Google Maps)</div>", unsafe_allow_html=True)
            loc_filter = st.selectbox("Khu vực / Tỉnh thành:", available_cities, label_visibility="collapsed", key="ai_loc")
            map_target = loc_filter if loc_filter != "Tất cả" else "Việt Nam"
            components.html(f"""<iframe width="100%" height="200" style="border:0; border-radius:8px;" loading="lazy" allowfullscreen src="https://maps.google.com/maps?q={map_target}&hl=vi&z=11&output=embed"></iframe>""", height=200)
            st.markdown("<div class='filter-header'>Hạng Sao</div>", unsafe_allow_html=True)
            star_filter_ui = st.selectbox("Lọc hạng sao:", ["Tất cả", "5 sao", "4 sao", "3 sao", "Dưới 3 sao"], label_visibility="collapsed", key="ai_star_ui")
            st.markdown("<div class='filter-header'>Giá mỗi đêm</div>", unsafe_allow_html=True)
            price_range = st.slider("Giá", min_value=0, max_value=5000000, value=(0, 5000000), step=100000, label_visibility="collapsed", key="ai_price")
            st.markdown("<div class='filter-header'>Trích xuất NLP</div>", unsafe_allow_html=True)
            filter_cancel = st.checkbox("Có nhắc 'Hủy miễn phí'", key="ai_cancel")
            filter_pool = st.checkbox("Có nhắc 'Hồ bơi'", key="ai_pool")

        with col_results:
            if st.session_state.ai_has_searched:
                with st.spinner("🤖 AI đang chạy thuật toán Hybrid (SVD + NLP)..."):
                    df_res = df_info.copy()
                    
                    if full_search_query:
                        star_intent = extract_intent(full_search_query)
                        top_indices = get_gensim_candidates(full_search_query, top_n=200, threshold=0.01)
                        if not top_indices: st.error(f"⚠️ NLP không tìm thấy cơ sở lưu trú nào liên quan đến '{full_search_query}'.")
                        else: df_res = df_res.iloc[top_indices].copy()
                        if star_intent: df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: match_star(x, star_intent))]
                    elif star_filter_ui != "Tất cả":
                        star_num = star_filter_ui.split(' ')[0]
                        if star_num.isdigit(): df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: match_star(x, star_num))]
                        else: df_res = df_res[df_res['Hotel_Rank'].apply(lambda x: int(float(str(x).split(' ')[0])) < 3 if pd.notna(x) else False)]
                    
                    if loc_filter != "Tất cả": df_res = df_res[df_res['City_Region'] == loc_filter]
                    df_res = df_res[(df_res['Data_Price'] >= price_range[0]) & (df_res['Data_Price'] <= price_range[1])]
                    df_res = df_res[df_res['Max_Guests'] >= (required_guests / required_rooms)]
                    if filter_cancel: df_res = df_res[df_res['Free_Cancel'] == True]
                    if filter_pool: df_res = df_res[df_res['Has_Pool'] == True]
                    
                    svd_model = models.get('surprise_svd')
                    is_warm_start = False
                    
                    if hybrid_user and check_user_exists(svd_model, hybrid_user):
                        is_warm_start = True
                        candidate_ids = df_res['Hotel_ID'].tolist()
                        df_res['Est_Score'] = [svd_model.predict(uid=hybrid_user, iid=hid).est for hid in candidate_ids]
                        df_res = df_res.sort_values(by='Est_Score', ascending=False)
                    else:
                        if hybrid_user: st.warning(f"⚠️ Thành viên '{hybrid_user}' chưa có dữ liệu lịch sử. Chuyển sang Gợi ý Trending.")
                        df_res['Total_Score_Num'] = pd.to_numeric(df_res.get('Total_Score', 0), errors='coerce').fillna(0)
                        df_res = df_res.sort_values(by='Total_Score_Num', ascending=False)

                    total_found = len(df_res)
                    if total_found == 0: st.info("Không tìm thấy kết quả phù hợp.")
                    else:
                        st.markdown(f"<h5 style='color:#E11D48;'>Đã tìm thấy & xếp hạng {total_found} đề xuất tốt nhất</h5>", unsafe_allow_html=True)
                        df_to_show = df_res.head(st.session_state.ai_display_limit)
                        
                        for i, (_, hotel) in enumerate(df_to_show.iterrows()):
                            with st.container(border=True):
                                cc1, cc2, cc3 = st.columns([1.5, 2.5, 1.2])
                                with cc1: st.image(f"https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80&sig={i+20}", use_container_width=True)
                                with cc2:
                                    stars = get_stars_icon(hotel.get('Hotel_Rank', ''))
                                    st.markdown(f"<div style='font-size:18px; font-weight:800; color:#003580; margin-bottom:5px;'>{hotel['Hotel_Name']} {stars}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div style='font-size:13px; color:#0071C2;'>📍 {hotel.get('Hotel_Address', 'N/A')}</div>", unsafe_allow_html=True)
                                    
                                    h_id = hotel['Hotel_ID']
                                    h_in = insights_dict.get(h_id, {})
                                    if is_warm_start:
                                        est = hotel['Est_Score']
                                        match_pct = min(int((est / 10.0) * 100 + np.random.randint(-5, 5)), 99) 
                                        pos_kws = list(h_in.get('pos_keywords', {}).keys())[:3]
                                        feature_str = f"đặc biệt là <b>{', '.join(pos_kws)}</b>" if pos_kws else "chất lượng dịch vụ tại đây"
                                        st.markdown(f"""
                                        <div class="member-insight-box">
                                            <div class="member-insight-title">👑 Đặc quyền Insight Thành viên</div>
                                            <div class="member-insight-text">Có <b>{match_pct}%</b> cộng đồng người dùng (cùng gu du lịch với bạn) đã đánh giá rất cao {feature_str}.</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        st.markdown("<div style='margin-top: 10px; font-size: 13px; color: #475569; font-weight: bold;'>Tóm tắt AI (Dành riêng cho thành viên):</div>", unsafe_allow_html=True)
                                        col_tags = ""
                                        
                                        grp_data = h_in.get('group_dist', {})
                                        if grp_data:
                                            top_group = max(grp_data, key=grp_data.get)
                                            col_tags += f"<span style='background: #DBEAFE; color: #1D4ED8; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px; display: inline-block; margin-bottom: 4px;'>👨‍👩‍👧‍👦 Top lựa chọn của {top_group}</span>"
                                            
                                        if pos_kws:
                                            col_tags += f"<span style='background: #D1FAE5; color: #047857; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px; display: inline-block; margin-bottom: 4px;'>✅ Khen nhiều: {', '.join(pos_kws[:2])}</span>"
                                            
                                        neg_kw = h_in.get('neg_keywords', {})
                                        if neg_kw:
                                            top_neg = list(neg_kw.keys())[0]
                                            col_tags += f"<span style='background: #FEE2E2; color: #B91C1C; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px; display: inline-block; margin-bottom: 4px;'>⚠️ Cần lưu ý: {top_neg}</span>"
                                            
                                        st.markdown(f"<div style='margin-top: 5px; margin-bottom: 10px;'>{col_tags}</div>", unsafe_allow_html=True)
                                    
                                    with st.expander("📝 Xem mô tả"): st.write(str(hotel.get('Hotel_Description', 'Đang cập nhật...')))
                                        
                                with cc3:
                                    score_str = str(hotel.get('Total_Score', 'N/A')).replace(',', '.')
                                    total_calculated_price, is_surge = get_dynamic_price(hotel['Data_Price'], checkin_date, num_nights, required_rooms)
                                    
                                    st.markdown(f"""
                                    <div style='text-align:right;'>
                                        <span style='font-weight:bold; color:#003580;'>{get_score_text(score_str)}</span> 
                                        <span style='background:#003580; color:white; padding:4px 8px; border-radius:6px; font-weight:bold;'>{score_str}</span>
                                    </div>
                                    <div style='text-align:right; margin-top:15px; margin-bottom:10px;'>
                                    """, unsafe_allow_html=True)
                                    if is_surge: st.markdown("<div style='font-size:11px; color:#E11D48; font-weight:bold; margin-bottom:2px;'>⚡ Tăng giá: Cuối tuần</div>", unsafe_allow_html=True)
                                    st.markdown(f"""
                                        <div style='font-size:12px; color:#666;'>Giá {required_rooms} phòng, {num_nights} đêm</div>
                                        <div style='font-size:22px; font-weight:800; color:#E11D48;'>{total_calculated_price:,} đ</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    def go_detail_ai(h_dict, price_calc):
                                        st.session_state.ai_selected_hotel = h_dict
                                        st.session_state.ai_calculated_price = price_calc
                                        st.session_state.ai_step = 'detail'
                                    st.button("Xem chi tiết", key=f"ai_view_{hotel['Hotel_ID']}", on_click=go_detail_ai, args=(hotel.to_dict(), total_calculated_price))

                        if st.session_state.ai_display_limit < total_found:
                            st.markdown('<div class="btn-load-more">', unsafe_allow_html=True)
                            if st.button("🔽 Xem thêm 5 cơ sở khác", key="ai_load_more", use_container_width=True):
                                st.session_state.ai_display_limit += 5
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                            
        st.markdown("---")
        st.markdown("""
        <div class="auth-card" style="margin-top: 30px;">
            <div class="auth-icon">♻️</div>
            <div class="auth-title">Đóng góp Trải nghiệm của Bạn (Data Flywheel)</div>
            <div class="auth-desc">Hãy gửi đánh giá thực tế của bạn để giúp hệ thống AI thấu hiểu "gu" của bạn tốt hơn trong những lần đề xuất tới.</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_gap1, c_form, c_gap2 = st.columns([1, 2, 1])
        with c_form:
            with st.form("review_form_member"):
                st.markdown("<b>👤 Tài khoản đang đăng nhập:</b>", unsafe_allow_html=True)
                rev_user = st.text_input("Tài khoản", value=hybrid_user, disabled=True, label_visibility="collapsed")
                
                hotel_names_list = df_info['Hotel_Name'].tolist()
                rev_hotel = st.selectbox("Chọn Khách sạn bạn đã ở:", hotel_names_list)
                st.markdown("<b>Đánh giá chất lượng:</b>", unsafe_allow_html=True)
                rev_score = st.slider("Điểm tổng quan (1 - 10):", min_value=1.0, max_value=10.0, value=8.0, step=0.1)
                rev_body = st.text_area("Nhận xét chuyến đi:", placeholder="Nhập cảm nhận của bạn về phòng ốc, dịch vụ, nhân viên...")
                submitted = st.form_submit_button("GỬI ĐÁNH GIÁ LÊN HỆ THỐNG", use_container_width=True)
                
                if submitted:
                    if not rev_user or not rev_body: st.error("⚠️ Vui lòng nhập Mã thành viên và Nhận xét.")
                    else:
                        h_id_selected = df_info[df_info['Hotel_Name'] == rev_hotel]['Hotel_ID'].values[0]
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                        new_reviews_path = os.path.join(BASE_DIR, 'data', 'new_reviews.csv')
                        
                        new_data = pd.DataFrame([{
                            "Reviewer ID": rev_user, "Hotel ID": h_id_selected, 
                            "Score": rev_score, "Body": rev_body, "Status": "Pending Batch Training"
                        }])
                        
                        if os.path.exists(new_reviews_path): new_data.to_csv(new_reviews_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                        else: new_data.to_csv(new_reviews_path, index=False, encoding='utf-8-sig')
                        st.success("✅ Cảm ơn bạn! Đánh giá đã được lưu vào Hồ sơ thành viên và Data Lake.")

    elif st.session_state.ai_step == 'detail':
        hotel = st.session_state.ai_selected_hotel
        total_price = st.session_state.ai_calculated_price
        
        st.button("← Quay lại Kết quả Đề xuất", on_click=lambda: st.session_state.update(ai_step='search'))
        stars = get_stars_icon(hotel.get('Hotel_Rank', ''))
        st.markdown(f"<h2>{hotel['Hotel_Name']} {stars}</h2>", unsafe_allow_html=True)
        
        cd1, cd2 = st.columns([2, 1])
        with cd1:
            st.image("https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", use_container_width=True)
            st.markdown("### 📝 Giới thiệu Khách sạn")
            st.info(hotel.get('Hotel_Description', 'Đang cập nhật...'))
            st.markdown("### 💬 Đánh giá thực tế từ Khách hàng")
            hotel_reviews = df_comments[df_comments['Hotel ID'] == hotel['Hotel_ID']]
            if hotel_reviews.empty: st.warning("Chưa có đánh giá nào.")
            else:
                top_reviews = hotel_reviews.sort_values(by='Score', ascending=False).head(4)
                for _, rev in top_reviews.iterrows():
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border-left:4px solid #E11D48; padding:15px; margin-bottom:10px; border-radius:4px;">
                        <span style="background:#003580; color:white; padding:3px 8px; border-radius:6px; font-weight:bold; margin-right:10px;">{rev['Score']}</span>
                        <span style="font-weight:bold; color:#333;">{get_score_text(str(rev['Score']))}</span><br>
                        <div style="font-size:14px; color:#444; margin-top:8px;">"{rev.get('Body', '')}"</div>
                    </div>
                    """, unsafe_allow_html=True)
        with cd2:
            st.markdown(f"""
            <div class='checkout-box'>
                <div style='font-size:14px; color:#666;'>Giá cho {st.session_state.ai_num_rooms} phòng, {st.session_state.ai_num_nights} đêm</div>
                <div style='font-size:24px; font-weight:bold; color:#E11D48; margin-bottom:5px;'>{total_price:,} đ</div>
                <div style='color:#008009; font-size:14px; font-weight:bold; margin-bottom:15px;'>✓ Đã bao gồm thuế và phí</div>
            """, unsafe_allow_html=True)
            st.button("TIẾN HÀNH ĐẶT PHÒNG", key="ai_go_checkout", use_container_width=True, on_click=lambda: st.session_state.update(ai_step='checkout'))
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.ai_step == 'checkout':
        hotel = st.session_state.ai_selected_hotel
        total_price = st.session_state.ai_calculated_price
        
        st.button("← Quay lại Trang Chi tiết", on_click=lambda: st.session_state.update(ai_step='detail'))
        st.markdown(f"## Hoàn tất thủ tục đặt phòng (Thành viên)")
        col_form, col_summary = st.columns([2, 1])
        with col_form:
            st.markdown("<div class='checkout-box'><div class='checkout-header'>Xác nhận Thông tin</div>", unsafe_allow_html=True)
            f1, f2 = st.columns(2)
            f1.text_input("Tên *", key="ai_fn")
            f2.text_input("Họ *", key="ai_ln")
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("XÁC NHẬN ĐẶT PHÒNG", key="ai_final_checkout", use_container_width=True):
                st.balloons(); st.success("🎉 Đặt phòng thành công! Dữ liệu đã lưu vào Lịch sử.")

        with col_summary:
            booking_dates = st.session_state.ai_booking_dates
            checkin_str = booking_dates[0].strftime("%d/%m/%Y")
            checkout_str = booking_dates[1].strftime("%d/%m/%Y") if len(booking_dates) > 1 else (booking_dates[0] + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
            st.markdown(f"""
            <div class='checkout-box'>
                <img src='https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80' style='width:100%; border-radius:8px; margin-bottom:15px;'>
                <div style='font-size:18px; font-weight:800; color:#003580; margin-bottom:10px;'>{hotel['Hotel_Name']}</div>
                <div style='background:#E0F2FE; color:#0369A1; padding:10px; border-radius:6px; font-size:13px; margin-bottom:15px;'><b>Nhận phòng:</b> 14:00 - {checkin_str}<br><b>Trả phòng:</b> 12:00 - {checkout_str}<br></div>
                <div class='checkout-header' style='font-size:16px;'>Chi tiết giá ({st.session_state.ai_num_rooms} phòng x {st.session_state.ai_num_nights} đêm)</div>
                <div style='display:flex; justify-content:space-between; margin-bottom: 8px; color: #475569; font-size: 14px;'><span>Tiền phòng</span> <span>{int(total_price):,} đ</span></div>
                <div style='display:flex; justify-content:space-between; margin-bottom: 8px; color: #475569; font-size: 14px;'><span>Thuế và phí (10%)</span> <span>{int(total_price * 0.1):,} đ</span></div>
                <div style='display:flex; justify-content:space-between; margin-top:15px; border-top:1px dashed #ccc; padding-top:10px; font-size:20px; font-weight:bold; color:#E11D48;'><span>TỔNG CỘNG</span> <span>{int(total_price * 1.1):,} đ</span></div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# MENU 3: TRUNG TÂM ĐỐI TÁC (ADMIN)
# ==========================================
elif menu == "🏢 Trung tâm Đối tác":
    
    if not st.session_state.admin_auth:
        st.markdown("""
        <div class="auth-card auth-card-admin">
            <div class="auth-icon">🏢</div>
            <div class="auth-title">Cổng Đăng nhập Đối tác Khách sạn</div>
            <div class="auth-desc">Quản lý doanh thu, theo dõi khách hàng và phân tích AI Insights toàn diện.</div>
        </div>
        """, unsafe_allow_html=True)
        
        c_gap1, c_hotel, c_pwd, c_btn, c_gap2 = st.columns([1, 3, 2, 1, 1])
        with c_hotel: admin_hotel_sel = st.selectbox("Khách sạn của bạn:", df_info['Hotel_Name'].tolist(), label_visibility="collapsed")
        with c_pwd: pwd = st.text_input("Mật khẩu:", type="password", label_visibility="collapsed", placeholder="agoda2026")
        with c_btn:
            if st.button("Đăng nhập", use_container_width=True):
                if pwd == "agoda2026":
                    st.session_state.admin_auth = True
                    st.session_state.admin_owned_hotel = admin_hotel_sel
                    st.rerun()
                else: st.error("Sai mật khẩu!")
    else:
        owned_hotel_name = st.session_state.admin_owned_hotel
        owned_id = df_info[df_info['Hotel_Name'] == owned_hotel_name]['Hotel_ID'].values[0]
        h_insight = insights_dict.get(owned_id, {})
        
        col_title, col_logout = st.columns([8, 2])
        with col_title: st.markdown(f"<h3 style='color:#003580;'>Xin chào, Quản lý {owned_hotel_name}!</h3>", unsafe_allow_html=True)
        with col_logout:
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
                
        hotel_reviews = prepare_admin_reviews(owned_id, df_comments)
        
        tab_exec, tab_nlp, tab_data_comp = st.tabs(["📊 Executive Dashboard", "☁️ Phân tích NLP (Trải nghiệm)", "📅 Dữ liệu Vận hành & Đối thủ"])
        
        # === TAB 1: EXECUTIVE DASHBOARD ===
        with tab_exec:
            if not hotel_reviews.empty:
                st.markdown("<div class='admin-card-title'>📅 Bộ lọc Phân tích Thời gian</div>", unsafe_allow_html=True)
                date_filter = st.date_input("Chọn khung thời gian xem báo cáo:", value=(datetime.date(2026, 1, 1), datetime.date(2026, 8, 30)))
                if len(date_filter) == 2:
                    mask = (hotel_reviews['Ngày Checkout'].dt.date >= date_filter[0]) & (hotel_reviews['Ngày Checkout'].dt.date <= date_filter[1])
                    filtered_reviews = hotel_reviews.loc[mask]
                else: filtered_reviews = hotel_reviews
                
                total_rev = filtered_reviews[filtered_reviews['Trạng thái'] == 'Đã hoàn tất']['Doanh Thu'].sum()
                adr = filtered_reviews[filtered_reviews['Trạng thái'] == 'Đã hoàn tất']['Doanh Thu'].mean()
                total_rooms_hotel = df_info[df_info['Hotel_ID'] == owned_id]['Total_Rooms'].values[0]
                
                seed_val_admin = sum(ord(c) for c in str(owned_id))
                np.random.seed(42 + seed_val_admin)
                
                base_occ = np.random.uniform(65, 85)
                avg_score_curr = filtered_reviews['Score'].mean()
                occupancy_rate = min(100, base_occ + (avg_score_curr - 8)*5)
                
                pos_kw = h_insight.get('pos_keywords', {})
                neg_kw = h_insight.get('neg_keywords', {})
                top_weakness = list(neg_kw.keys())[0] if neg_kw else None
                top_strength = list(pos_kw.keys())[0] if pos_kw else None
                
                st.markdown("<div class='admin-card-title'>📄 Executive Summary & AI Alerts</div>", unsafe_allow_html=True)
                st.info(f"💡 **Tóm tắt Kinh doanh:** Trong kỳ, khách sạn đạt tổng doanh thu **{total_rev/1000000:,.1f} Triệu VNĐ** với tỷ lệ lấp đầy ước tính **{occupancy_rate:.1f}%**. Khách hàng đặc biệt đánh giá cao về **'{top_strength}'**, duy trì mức điểm trung bình **{avg_score_curr:.1f}/10**.")
                
                c_alert1, c_alert2 = st.columns(2)
                with c_alert1:
                    if top_weakness: st.markdown(f"<div class='alert-box'>🚨 <b>Rủi ro Trải nghiệm:</b> Ghi nhận tỷ lệ phàn nàn cao về <b>'{top_weakness}'</b>. Cần rà soát ngay lập tức!</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='rec-box'>✅ Không phát hiện rủi ro tiêu cực nghiêm trọng.</div>", unsafe_allow_html=True)
                with c_alert2:
                    if top_weakness == 'phòng': st.markdown("<div class='rec-box'>🤖 <b>AI Đề xuất:</b> Lên kế hoạch bảo trì, kiểm tra lại thiết bị trong phòng và quy trình Housekeeping.</div>", unsafe_allow_html=True)
                    elif top_weakness == 'bữa sáng': st.markdown("<div class='rec-box'>🤖 <b>AI Đề xuất:</b> Làm việc lại với bộ phận F&B để cải thiện thực đơn buffet sáng.</div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='rec-box'>🤖 <b>AI Đề xuất:</b> Tiếp tục phát huy thế mạnh hiện tại để duy trì điểm số.</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='admin-card-title'>📊 Sức khỏe Kinh doanh & Đánh giá (Hotel Health)</div>", unsafe_allow_html=True)
                kpi_f1, kpi_f2, kpi_f3, kpi_f4 = st.columns(4)
                kpi_f1.metric("Tổng Doanh Thu", f"{total_rev/1000000:,.1f} Tr VNĐ")
                kpi_f2.metric("ADR (Giá bán TB)", f"{adr:,.0f} đ" if pd.notna(adr) else "0 đ")
                kpi_f3.metric("Tỷ lệ lấp đầy (Occ)", f"{occupancy_rate:.1f}%")
                kpi_f4.metric("Tổng lượt lưu trú", f"{len(filtered_reviews)} lượt")
                
                c_radar, c_dist = st.columns([1, 1])
                with c_radar:
                    cats = ['Location', 'Cleanliness', 'Service', 'Facilities', 'Value_for_money']
                    try:
                        h_vals = [pd.to_numeric(df_info[df_info['Hotel_ID']==owned_id][c].values[0], errors='coerce') for c in cats]
                        fig_radar = go.Figure()
                        fig_radar.add_trace(go.Scatterpolar(
                            r=h_vals,
                            theta=['Vị trí', 'Sạch sẽ', 'Dịch vụ', 'Tiện nghi', 'Giá trị'],
                            fill='toself',
                            name='Cơ sở của bạn',
                            line_color='#003580'
                        ))
                        fig_radar.update_layout(title="🎯 Đánh giá 5 Tiêu chí Dịch vụ", polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
                        st.plotly_chart(fig_radar, use_container_width=True)
                    except: st.warning("Chưa có dữ liệu 5 tiêu chí.")
                with c_dist:
                    dist_df = filtered_reviews['Phân khúc điểm'].value_counts().reset_index()
                    dist_df.columns = ['Phân khúc', 'Số lượng']
                    fig_dist = px.bar(dist_df, x='Số lượng', y='Phân khúc', orientation='h', title="⭐ Phân bổ Đánh giá (Rating Analysis)", color_discrete_sequence=['#10B981'])
                    fig_dist.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                st.markdown("<div class='admin-card-title'>📍 Phân tích Nguồn khách (Geographic Demographics)</div>", unsafe_allow_html=True)
                col_geo1, col_geo2 = st.columns(2)
                with col_geo1:
                    nat_counts = filtered_reviews['Nationality'].value_counts().reset_index()
                    nat_counts.columns = ['Quốc gia', 'Số lượng']
                    fig_nat_pie = px.pie(nat_counts.head(5), values='Số lượng', names='Quốc gia', title="🌍 Thị phần Nguồn khách Quốc gia", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_nat_pie, use_container_width=True)
                with col_geo2:
                    city_counts = filtered_reviews[filtered_reviews['Guest_City'] != 'Quốc tế']['Guest_City'].value_counts().reset_index()
                    city_counts.columns = ['Tỉnh/Thành', 'Số lượng']
                    fig_city_pie = px.pie(city_counts, values='Số lượng', names='Tỉnh/Thành', title="🇻🇳 Thị phần Khách Nội địa (Theo Tỉnh/Thành)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                    st.plotly_chart(fig_city_pie, use_container_width=True)

                st.markdown("<div class='admin-card-title'>📈 Xu hướng Kinh doanh & Nhân khẩu học</div>", unsafe_allow_html=True)
                c_chart1, c_chart2 = st.columns(2)
                with c_chart1:
                    trend_df = filtered_reviews.groupby(filtered_reviews['Ngày Checkout'].dt.to_period('M')).size().reset_index(name='Lượt đánh giá')
                    trend_df['Sort_Date'] = trend_df['Ngày Checkout'].dt.to_timestamp()
                    trend_df = trend_df.sort_values('Sort_Date')
                    trend_df['Tháng'] = trend_df['Sort_Date'].dt.strftime('%m/%Y')
                    fig_trend = px.line(trend_df, x='Tháng', y='Lượt đánh giá', title="Xu hướng Lượng khách lưu trú (Theo tháng)", markers=True, color_discrete_sequence=['#0071C2'])
                    fig_trend.update_xaxes(type='category', categoryorder='array', categoryarray=trend_df['Tháng'].unique())
                    st.plotly_chart(fig_trend, use_container_width=True)
                with c_chart2:
                    trend_geo = filtered_reviews.groupby([filtered_reviews['Ngày Checkout'].dt.to_period('M'), 'Nationality']).size().reset_index(name='Lượt khách')
                    trend_geo['Sort_Date'] = trend_geo['Ngày Checkout'].dt.to_timestamp()
                    trend_geo = trend_geo.sort_values('Sort_Date')
                    trend_geo['Tháng'] = trend_geo['Sort_Date'].dt.strftime('%m/%Y')
                    top_nats = filtered_reviews['Nationality'].value_counts().head(3).index.tolist()
                    trend_geo = trend_geo[trend_geo['Nationality'].isin(top_nats)]
                    fig_trend_geo = px.line(trend_geo, x='Tháng', y='Lượt khách', color='Nationality', title="Xu hướng Top 3 Quốc tịch qua các tháng", markers=True)
                    fig_trend_geo.update_xaxes(type='category', categoryorder='array', categoryarray=trend_geo['Tháng'].unique())
                    st.plotly_chart(fig_trend_geo, use_container_width=True)
            else: st.warning("Chưa có dữ liệu để phân tích.")

        # === TAB 2: NLP INSIGHTS ===
        with tab_nlp:
            if not hotel_reviews.empty:
                st.markdown("<div class='admin-card-title'>😊 Phân tích Trải nghiệm Chuyên sâu (Aspect-Based Sentiment)</div>", unsafe_allow_html=True)
                
                c_pos_wc, c_pos_stat = st.columns(2)
                with c_pos_wc:
                    st.markdown("**💪 Điểm Sáng Cốt Lõi (Top Strength)**")
                    if pos_kw:
                        fig_wc_pos, ax = plt.subplots(figsize=(6, 4))
                        ax.imshow(WordCloud(width=600, height=400, background_color='white', colormap='viridis').generate_from_frequencies(pos_kw), interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig_wc_pos)
                with c_pos_stat:
                    st.markdown("**Định lượng Điểm Sáng (%)**")
                    st.markdown(render_text_stats(pos_kw, "#10B981"), unsafe_allow_html=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                
                c_neg_wc, c_neg_stat = st.columns(2)
                with c_neg_wc:
                    st.markdown("**⚠ Điểm Yếu Cốt Lõi (Top Weakness)**")
                    if neg_kw:
                        fig_wc_neg, ax = plt.subplots(figsize=(6, 4))
                        ax.imshow(WordCloud(width=600, height=400, background_color='white', colormap='magma').generate_from_frequencies(neg_kw), interpolation='bilinear')
                        ax.axis("off")
                        st.pyplot(fig_wc_neg)
                    else: st.success("Không có phàn nàn nổi bật.")
                with c_neg_stat:
                    st.markdown("**Định lượng Điểm Yếu (%)**")
                    st.markdown(render_text_stats(neg_kw, "#EF4444"), unsafe_allow_html=True)
            else: st.warning("Chưa có dữ liệu NLP.")

        # === TAB 3: DỮ LIỆU & ĐỐI THỦ ===
        with tab_data_comp:
            st.markdown("<div class='admin-card-title'>📅 Quản lý Dữ liệu Lưu trú</div>", unsafe_allow_html=True)
            if not hotel_reviews.empty:
                display_df = filtered_reviews[['Reviewer ID', 'Nationality', 'Guest_City', 'Group Name', 'Ngày Nhận Phòng', 'Ngày Checkout', 'Trạng thái', 'Doanh Thu', 'Score']].sort_values('Ngày Checkout', ascending=False)
                display_df['Ngày Nhận Phòng'] = display_df['Ngày Nhận Phòng'].dt.strftime('%d/%m/%Y')
                display_df['Ngày Checkout'] = display_df['Ngày Checkout'].dt.strftime('%d/%m/%Y')
                display_df['Doanh Thu'] = display_df['Doanh Thu'].apply(lambda x: f"{int(x):,} đ")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else: st.warning("Trống.")
            
            st.markdown("<br><div class='admin-card-title'>📉 Compare With Market (So sánh Đối thủ Cạnh tranh)</div>", unsafe_allow_html=True)
            competitor_name = st.selectbox("Chọn Khách sạn Đối thủ để phân tích:", df_info[df_info['Hotel_Name'] != owned_hotel_name]['Hotel_Name'].tolist())
            comp_id = df_info[df_info['Hotel_Name'] == competitor_name]['Hotel_ID'].values[0]
            comp_insight = insights_dict.get(comp_id, {})
            
            comp_reviews = prepare_admin_reviews(comp_id, df_comments)
            
            st.warning("🔒 Tuân thủ Quyền Riêng Tư (Data Privacy), dữ liệu danh sách khách hàng chi tiết và doanh thu của Đối thủ bị ẩn. Chỉ hiển thị biểu đồ phân tích thị phần và chỉ số trải nghiệm công khai.")
            
            if not comp_reviews.empty:
                st.markdown("#### 🌍 Phân tích Nguồn khách Đối thủ (Thị phần)")
                c_comp_geo1, c_comp_geo2 = st.columns(2)
                with c_comp_geo1:
                    comp_nat_counts = comp_reviews['Nationality'].value_counts().reset_index()
                    comp_nat_counts.columns = ['Quốc gia', 'Số lượng']
                    fig_comp_nat = px.pie(comp_nat_counts.head(5), values='Số lượng', names='Quốc gia', title="Thị phần Quốc gia của Đối thủ", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_comp_nat, use_container_width=True)
                with c_comp_geo2:
                    comp_trend_geo = comp_reviews.groupby([comp_reviews['Ngày Checkout'].dt.to_period('M'), 'Nationality']).size().reset_index(name='Lượt khách')
                    comp_trend_geo['Sort_Date'] = comp_trend_geo['Ngày Checkout'].dt.to_timestamp()
                    comp_trend_geo = comp_trend_geo.sort_values('Sort_Date')
                    comp_trend_geo['Tháng'] = comp_trend_geo['Sort_Date'].dt.strftime('%m/%Y')
                    comp_top_nats = comp_reviews['Nationality'].value_counts().head(3).index.tolist()
                    comp_trend_geo = comp_trend_geo[comp_trend_geo['Nationality'].isin(comp_top_nats)]
                    fig_comp_trend = px.line(comp_trend_geo, x='Tháng', y='Lượt khách', color='Nationality', title="Xu hướng Khách Đối thủ", markers=True)
                    fig_comp_trend.update_xaxes(type='category', categoryorder='array', categoryarray=comp_trend_geo['Tháng'].unique())
                    st.plotly_chart(fig_comp_trend, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🗣️ Phân tích Cảm xúc & Từ khóa (Sentiment & NLP)")
            
            c_comp_pie, c_comp_words = st.columns([1, 1.5])
            with c_comp_pie:
                pcts = comp_insight.get('sentiment_pct', {})
                if pcts:
                    fig_pie = px.pie(values=list(pcts.values()), names=list(pcts.keys()), title="Tỉ lệ Cảm xúc Chung", color_discrete_sequence=['#2ecc71', '#f1c40f', '#e74c3c'], hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else: st.write("Không có dữ liệu.")
            
            with c_comp_words:
                c_w_pos, c_w_neg = st.columns(2)
                with c_w_pos:
                    st.markdown("**🟩 Top từ khóa tạo nên Tích cực**")
                    pos_kw_c = comp_insight.get('pos_keywords', {})
                    st.markdown(render_text_stats(pos_kw_c, "#10B981"), unsafe_allow_html=True)
                with c_w_neg:
                    st.markdown("**🟥 Top từ khóa tạo nên Tiêu cực**")
                    neg_kw_c = comp_insight.get('neg_keywords', {})
                    st.markdown(render_text_stats(neg_kw_c, "#EF4444"), unsafe_allow_html=True)

            st.markdown("---")
            cats = ['Location', 'Cleanliness', 'Service', 'Facilities', 'Value_for_money']
            try:
                h_vals = [pd.to_numeric(df_info[df_info['Hotel_ID']==owned_id][c].values[0], errors='coerce') for c in cats]
                c_vals = [pd.to_numeric(df_info[df_info['Hotel_ID']==comp_id][c].values[0], errors='coerce') for c in cats]
                fig_bar = go.Figure(data=[
                    go.Bar(name='Cơ sở của Bạn', x=cats, y=h_vals, marker_color='#003580'),
                    go.Bar(name='Đối thủ', x=cats, y=c_vals, marker_color='#E11D48')
                ])
                fig_bar.update_layout(title="Benchmark Trực tiếp 5 Tiêu chí Dịch vụ", barmode='group')
                st.plotly_chart(fig_bar, use_container_width=True)
            except Exception: st.warning("Thiếu dữ liệu chi tiết so sánh.")


# ==========================================
# MENU 4: TỔNG QUAN ĐỒ ÁN (FOR COMMITTEE)
# ==========================================
elif menu == "🎓 Giới thiệu Đồ án":
    tab_stats, tab_story, tab_model, tab_team = st.tabs(["📊 Thống kê Nền tảng", "📖 Câu chuyện Dữ liệu", "⚙️ Mô hình & Đánh giá", "👨‍💻 Phân công & Nhóm"])
    
    with tab_stats:
        st.markdown("### 📊 Thống kê Nền tảng (Global Insights)")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Tổng số Khách sạn", f"{len(df_info):,}")
        kpi2.metric("Tổng lượt Đánh giá", f"{len(df_comments):,}")
        
        try:
            valid_scores = pd.to_numeric(df_info['Total_Score'].astype(str).str.replace(',', '.'), errors='coerce').dropna()
            avg_score = valid_scores.mean() if not valid_scores.empty else 8.2
        except:
            avg_score = 8.2
            
        kpi3.metric("Điểm trung bình", f"{avg_score:.1f}/10")
        kpi4.metric("Engine Recommender", "Hybrid CF + CB")
        st.markdown("---")
        
        sentiment_counts = df_comments['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sắc thái', 'Số lượng']
        fig_pie = px.pie(sentiment_counts, values='Số lượng', names='Sắc thái', color='Sắc thái',
                         color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#f1c40f', 'Negative':'#e74c3c'}, hole=0.4, title="Phân bổ Sắc thái Đánh giá toàn hệ thống")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab_story:
        st.markdown("""
        ### 📖 Câu chuyện Dữ liệu (Data Story)
        
        Trong thời đại bùng nổ thông tin, khách hàng phải đối mặt với hàng ngàn lựa chọn khách sạn khi đi du lịch. Điều này dẫn đến hiệu ứng **"Nghịch lý của sự lựa chọn" (Paradox of Choice)**, khiến họ mất nhiều thời gian để ra quyết định và dễ bị choáng ngợp.
        
        Đồ án này được sinh ra để giải quyết bài toán đó bằng cách ứng dụng **Khoa học dữ liệu (Data Science)** và **Học máy (Machine Learning)**:
        
        *   **Nguồn dữ liệu:** Khai thác tập dữ liệu thực tế gồm thông tin hàng ngàn khách sạn tại Việt Nam và hàng chục ngàn bình luận (reviews) từ người dùng.
        *   **Khía cạnh NLP (Xử lý ngôn ngữ tự nhiên):** Phân tích cảm xúc (Sentiment Analysis) để bóc tách xem khách hàng đang khen hay chê điều gì, từ đó giúp Quản lý khách sạn (Admin) nhìn ra điểm sáng và điểm mù của doanh nghiệp.
        *   **Khía cạnh Recommender System (Hệ thống gợi ý):** Xây dựng một luồng kiến trúc thông minh giúp tự động "đọc vị" gu của khách hàng để đưa ra các đề xuất khách sạn cá nhân hóa nhất.
        """)
        
    with tab_model:
        st.markdown("### ⚙️ Đánh giá Mô hình & Thuật toán")
        st.markdown("Hệ thống đề xuất sử dụng kiến trúc lai phân tầng **Cascade Hybrid (CF + CB)** nhằm giải quyết đồng thời bài toán cá nhân hóa và nhu cầu bối cảnh nhất thời.")
        st.markdown("Trong bài toán Lọc cộng tác (Collaborative Filtering) có độ thưa thớt (sparsity) cao, hệ thống sử dụng **RMSE** làm thang đo chính. Mô hình **Surprise SVD** được chọn làm Engine cốt lõi nhờ sai số thấp và tốc độ suy luận nhanh.")
        
        col_e1, col_e2, col_e3 = st.columns(3)
        col_e1.metric(label="Surprise SVD (Python)", value="0.9213 RMSE", delta="Engine Chính", delta_color="normal")
        col_e2.metric(label="PySpark ALS (Big Data)", value="0.9407 RMSE", delta="Dự phòng", delta_color="off")
                        
    with tab_team:
        st.markdown("### 👨‍💻 Thông tin Nhóm thực hiện Đồ án")
        st.markdown("Đồ án thuộc **Trung tâm Tin học - Đại học Khoa học Tự nhiên TP.HCM**.")
        st.markdown("---")
        
        st.markdown("#### 👩‍🏫 Giảng viên Hướng dẫn:")
        st.info("**Cô Khuất Thùy Phương**")
        
        st.markdown("#### 👨‍🎓 Nhóm thực hiện:")
        t1, t2 = st.columns(2)
        with t1:
            st.success("""
            **1. Phan Phúc Lộc**
            * Email: pplocddt@gmail.com
            - Tiền xử lý dữ liệu & Phân tích khám phá (EDA)
            - Phân tích phản hồi khách hàng & Cung cấp Business Insights
            - Hướng phát triển

           
            """)
        with t2:
            st.success("""
            **2. Nguyễn Nhật Trường**
            * Email: fmnntruong@gmail.com
            - Triển khai Content-Based Filtering
            - Triển khai Collaborative Filtering
            - Xây dựng GUI Web App bằng Streamlit và deploy ứng dụng Recommender System lên Streamlit Cloud thông qua GitHub.
            - Lập nội dung báo cáo trên Slide
            - Lập file hướng dẫn readme

            """)

# --- FOOTER ---
st.markdown("""
<div class='footer-container'>
    Agoda Recommender System
</div>
""", unsafe_allow_html=True)
