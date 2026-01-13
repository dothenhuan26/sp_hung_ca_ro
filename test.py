import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ Thống Báo Cáo Nội Bộ", layout="wide", page_icon="📈")


# --- XỬ LÝ DATABASE (SQLite) ---
# Hàm này tự động tạo file database nếu chưa có
def init_db():
    conn = sqlite3.connect('data_baocao.db')
    c = conn.cursor()
    # Tạo bảng lưu dữ liệu báo cáo
    c.execute('''
              CREATE TABLE IF NOT EXISTS reports
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  report_date
                  TEXT,
                  channel
                  TEXT,
                  team
                  TEXT,
                  gmv
                  REAL,
                  cost
                  REAL,
                  orders
                  INTEGER,
                  best_performer
                  TEXT,
                  extra_metric_1
                  REAL,
                  extra_metric_2
                  REAL,
                  note
                  TEXT,
                  created_at
                  TIMESTAMP
                  DEFAULT
                  CURRENT_TIMESTAMP
              )
              ''')
    conn.commit()
    conn.close()


# Gọi hàm khởi tạo DB ngay khi chạy app
init_db()


# Hàm gửi dữ liệu vào DB
def submit_data(date, channel, team, gmv, cost, orders, best, ex1, ex2, note):
    conn = sqlite3.connect('data_baocao.db')
    c = conn.cursor()
    c.execute('''
              INSERT INTO reports (report_date, channel, team, gmv, cost, orders, best_performer, extra_metric_1,
                                   extra_metric_2, note)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              ''', (date, channel, team, gmv, cost, orders, best, ex1, ex2, note))
    conn.commit()
    conn.close()
    st.success(f"Đã lưu báo cáo cho team {team} - Kênh {channel}!")


# Hàm lấy dữ liệu ra để vẽ biểu đồ
def load_data():
    conn = sqlite3.connect('data_baocao.db')
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return df


# --- GIAO DIỆN CHÍNH ---
st.title("🔥 HỆ THỐNG QUẢN TRỊ & BÁO CÁO (MANUAL INPUT)")

# Sidebar: Chọn chế độ (Nhập liệu hay Xem báo cáo)
menu = st.sidebar.radio("Chọn Chức Năng", ["📝 NHẬP LIỆU (Cho Nhân Viên)", "📊 DASHBOARD (Cho Sếp)"])

# ==============================================================================
# PHẦN 1: GIAO DIỆN NHẬP LIỆU (DÀNH CHO NHÂN VIÊN)
# ==============================================================================
if menu == "📝 NHẬP LIỆU (Cho Nhân Viên)":
    st.header("Cập Nhật Số Liệu Hàng Ngày")
    st.markdown("Lưu ý: Nhập đúng số tiền (VNĐ). Sai số liệu sẽ ảnh hưởng đến lương thưởng.")

    with st.form("input_form"):
        col_date, col_channel = st.columns(2)
        input_date = col_date.date_input("Ngày báo cáo", datetime.now())
        input_channel = col_channel.selectbox("Kênh bán hàng", ["TikTok Shop", "Shopee", "Facebook"])

        # Logic hiển thị form nhập theo từng kênh
        input_team = "General"
        val_gmv = 0.0
        val_cost = 0.0
        val_orders = 0
        val_best = ""
        val_ex1 = 0.0
        val_ex2 = 0.0
        val_note = ""

        st.divider()

        if input_channel == "TikTok Shop":
            input_team = st.selectbox("Chọn Team", ["Team Ads", "Team Livestream", "Team Booking"])

            if input_team == "Team Ads":
                c1, c2, c3 = st.columns(3)
                val_gmv = c1.number_input("Doanh số từ Ads", min_value=0.0, step=100000.0)
                val_cost = c2.number_input("Chi phí Ads (Spend)", min_value=0.0, step=100000.0)
                val_ex1 = c3.number_input("Số lượng Video lên hàng ngày", min_value=0)
                val_best = st.text_input("Video tốt nhất (Mã Video/Link)")

            elif input_team == "Team Livestream":
                c1, c2, c3 = st.columns(3)
                val_gmv = c1.number_input("Doanh số Livestream", min_value=0.0)
                val_cost = c2.number_input("Chi phí vận hành Live (Voucher/Ads Live)", min_value=0.0)
                val_orders = c3.number_input("Số đơn hàng", min_value=0)
                val_best = st.text_input("Ca Live tốt nhất / Host Live tốt nhất")

            elif input_team == "Team Booking":
                c1, c2 = st.columns(2)
                val_cost = c1.number_input("Chi phí Booking (Tiền booking + Sản phẩm)", min_value=0.0)
                val_gmv = c2.number_input("Doanh số từ KOC/Affiliate", min_value=0.0)  # Có thể ước lượng
                val_best = st.text_input("KOC hiệu quả nhất")

        elif input_channel == "Shopee":
            input_team = st.selectbox("Chọn Team", ["Ads Shopee", "Livestream Shopee", "Affiliate Shopee"])

            if input_team == "Ads Shopee":
                c1, c2, c3 = st.columns(3)
                val_gmv = c1.number_input("Doanh số Ads", min_value=0.0)
                val_cost = c2.number_input("Chi phí Ads", min_value=0.0)
                val_ex1 = c3.number_input("ROAS (Tự nhập hoặc tính sau)", min_value=0.0)

            elif input_team == "Livestream Shopee":
                c1, c2 = st.columns(2)
                val_gmv = c1.number_input("Doanh số Live", min_value=0.0)
                val_cost = c2.number_input("Chi phí Live", min_value=0.0)
                val_best = st.text_input("Ca Live tốt nhất")

            elif input_team == "Affiliate Shopee":
                c1, c2 = st.columns(2)
                val_gmv = c1.number_input("Doanh số Affiliate", min_value=0.0)
                val_cost = c2.number_input("Chi phí hoa hồng phải trả", min_value=0.0)

        elif input_channel == "Facebook":
            input_team = st.selectbox("Chọn Team", ["FB Ads/Sale", "Content Team"])
            if input_team == "FB Ads/Sale":
                c1, c2, c3 = st.columns(3)
                val_cost = c1.number_input("Chi phí Ads (Spend)", min_value=0.0)
                val_orders = c2.number_input("Số lượng Mess/Lead", min_value=0)
                val_gmv = c3.number_input("Doanh số chốt đơn (Thực thu)", min_value=0.0)
                val_best = st.text_input("Nhân sự Sale xuất sắc nhất")

            elif input_team == "Content Team":
                val_ex1 = st.number_input("Số lượng Video sản xuất", min_value=0)
                val_best = st.text_input("Video tốt nhất team")

        val_note = st.text_area("Ghi chú thêm (Nếu có)")

        # Nút Submit
        submitted = st.form_submit_button("Lưu Báo Cáo")
        if submitted:
            # Chuyển đổi date sang string để lưu DB
            str_date = input_date.strftime("%Y-%m-%d")
            submit_data(str_date, input_channel, input_team, val_gmv, val_cost, val_orders, val_best, val_ex1, val_ex2,
                        val_note)

# ==============================================================================
# PHẦN 2: DASHBOARD (DÀNH CHO SẾP)
# ==============================================================================
elif menu == "📊 DASHBOARD (Cho Sếp)":
    # Load dữ liệu
    df = load_data()

    if df.empty:
        st.warning("Chưa có dữ liệu nào được nhập! Hãy sang tab 'Nhập Liệu' để nhập số.")
    else:
        # Xử lý dữ liệu
        df['report_date'] = pd.to_datetime(df['report_date'])

        # --- BỘ LỌC THỜI GIAN ---
        st.sidebar.markdown("---")
        st.sidebar.header("Bộ Lọc Dashboard")
        date_range = st.sidebar.date_input("Chọn khoảng thời gian",
                                           [datetime.now() - timedelta(days=7), datetime.now()])

        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask = (df['report_date'] >= start_date) & (df['report_date'] <= end_date)
            df_filtered = df.loc[mask]
        else:
            df_filtered = df

        # --- KPI TỔNG QUAN ---
        total_gmv = df_filtered['gmv'].sum()
        total_cost = df_filtered['cost'].sum()
        cir = (total_cost / total_gmv * 100) if total_gmv > 0 else 0
        profit_est = total_gmv * 0.4 - total_cost  # Giả định biên lãi gộp 40%

        st.markdown(
            f"### Kết quả kinh doanh từ {date_range[0].strftime('%d/%m')} đến {date_range[1].strftime('%d/%m') if len(date_range) > 1 else '...'}")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Tổng Doanh Số", f"{total_gmv:,.0f} đ")
        k2.metric("💸 Tổng Chi Phí Thúc Đẩy", f"{total_cost:,.0f} đ")
        k3.metric("📉 % Chi Phí (CIR)", f"{cir:.1f}%", delta_color="inverse")  # Càng thấp càng tốt
        k4.metric("💎 Lợi Nhuận (Ước tính)", f"{profit_est:,.0f} đ")

        st.divider()

        # --- BIỂU ĐỒ PHÂN TÍCH ---
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Doanh số theo Kênh")
            # Group by Channel
            df_channel = df_filtered.groupby('channel')['gmv'].sum().reset_index()
            fig_pie = px.pie(df_channel, values='gmv', names='channel', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader("Xu hướng Doanh số & Chi phí (Theo ngày)")
            df_daily = df_filtered.groupby('report_date')[['gmv', 'cost']].sum().reset_index()
            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(x=df_daily['report_date'], y=df_daily['gmv'], name='Doanh số', marker_color='#4CAF50'))
            fig_bar.add_trace(
                go.Bar(x=df_daily['report_date'], y=df_daily['cost'], name='Chi phí', marker_color='#FF5252'))
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- CHI TIẾT THEO TEAM (DRILL DOWN) ---
        st.subheader("📋 Chi tiết hiệu quả từng Team")

        tab_tiktok, tab_shopee, tab_fb = st.tabs(["🎵 TikTok Shop", "🛍️ Shopee", "📘 Facebook"])

        with tab_tiktok:
            df_tt = df_filtered[df_filtered['channel'] == "TikTok Shop"]
            if not df_tt.empty:
                # Group theo team
                st.dataframe(df_tt[['report_date', 'team', 'gmv', 'cost', 'best_performer', 'note']],
                             use_container_width=True)

                # Metric đặc thù
                total_ads_tt = df_tt[df_tt['team'] == 'Team Ads']['cost'].sum()
                total_gmv_ads_tt = df_tt[df_tt['team'] == 'Team Ads']['gmv'].sum()
                roas_tt = total_gmv_ads_tt / total_ads_tt if total_ads_tt > 0 else 0
                st.info(f"Team Ads TikTok: Tổng chi tiêu {total_ads_tt:,.0f} - ROAS trung bình: {roas_tt:.2f}")
            else:
                st.write("Chưa có dữ liệu TikTok trong khoảng thời gian này.")

        with tab_shopee:
            df_sp = df_filtered[df_filtered['channel'] == "Shopee"]
            if not df_sp.empty:
                st.dataframe(df_sp[['report_date', 'team', 'gmv', 'cost', 'best_performer']], use_container_width=True)
            else:
                st.write("Chưa có dữ liệu Shopee.")

        with tab_fb:
            df_fb = df_filtered[df_filtered['channel'] == "Facebook"]
            if not df_fb.empty:
                st.dataframe(df_fb[['report_date', 'team', 'gmv', 'cost', 'orders', 'best_performer']],
                             use_container_width=True)
            else:
                st.write("Chưa có dữ liệu Facebook.")

        # --- NÚT XUẤT EXCEL ---
        st.download_button(
            label="📥 Tải Báo Cáo Excel",
            data=df_filtered.to_csv(index=False).encode('utf-8'),
            file_name='bao_cao_kinh_doanh.csv',
            mime='text/csv',
        )