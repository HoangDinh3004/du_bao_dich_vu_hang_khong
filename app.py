import streamlit as st
import pandas as pd
import joblib
import os


# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Dự báo Hài lòng Hàng không", page_icon="✈️", layout="wide")

st.title("✈️ Dự báo Mức độ Hài lòng Khách hàng")
st.write("Nhập thông tin chuyến bay ở cột bên trái để xem AI dự đoán.")

# --- 2. LOAD MÔ HÌNH (Đã sửa lỗi đường dẫn và gọi hàm) ---
@st.cache_resource
def load_data():
    # Chỉ cần gọi tên file, vì lát nữa ta sẽ để file này nằm ngay cạnh app.py trên GitHub
    file_path = "final_lightgbm_model.pkl" 
    
    loaded_model = joblib.load(file_path)
    return loaded_model

# --- QUAN TRỌNG: GỌI HÀM ĐỂ LẤY MÔ HÌNH ---
model = load_data()

# Kiểm tra nếu chưa có mô hình thì báo lỗi ngay
if model is None:
    st.error("❌ Lỗi: Không tìm thấy file 'final_lightgbm_model.pkl'. Hãy đảm bảo file này nằm cùng thư mục với app.py")
    st.stop()
else:
    st.success("✅ Đã kết nối với bộ não AI thành công!")

# --- 3. GIAO DIỆN NHẬP LIỆU (SIDEBAR MỚI) ---
st.sidebar.header("📝 Nhập thông tin")

def user_input_features():
    # --- NHÓM 1: THÔNG TIN CÁ NHÂN ---
    with st.sidebar.expander("👤 1. Thông tin Cá nhân", expanded=True):
        gender = st.selectbox("Giới tính", ["Nam", "Nữ"])
        gender_val = 1 if gender == "Nam" else 0
        
        age = st.slider("Tuổi", 7, 85, 30)
        
        cust_type = st.selectbox("Loại khách hàng", ["Thân thiết", "Vãng lai"])
        cust_type_val = 0 if cust_type == "Thân thiết" else 1

    # --- NHÓM 2: THÔNG TIN CHUYẾN BAY ---
    with st.sidebar.expander("✈️ 2. Chi tiết Chuyến bay", expanded=True):
        travel_type = st.selectbox("Mục đích chuyến đi", ["Công tác", "Cá nhân"])
        travel_type_val = 0 if travel_type == "Công tác" else 1
        
        flight_class = st.selectbox("Hạng vé", ["Thương gia", "Phổ thông", "Phổ thông đặc biệt"])
        if flight_class == "Thương gia": class_val = 2
        elif flight_class == "Phổ thông": class_val = 0
        else: class_val = 1
        
        flight_distance = st.number_input("Khoảng cách bay (km)", min_value=0, value=1000)
        
        st.markdown("---")
        st.write("⏱️ **Thông tin trễ chuyến (phút):**")
        dep_delay = st.number_input("Trễ khởi hành (Departure Delay)", min_value=0, value=0)
        arr_delay = st.number_input("Trễ đến nơi (Arrival Delay)", min_value=0, value=0)

    # --- NHÓM 3: ĐÁNH GIÁ DỊCH VỤ ---
    with st.sidebar.expander("⭐ 3. Đánh giá Dịch vụ (1-5 sao)", expanded=False):
        st.info("Kéo thanh trượt để chấm điểm")
        
        wifi = st.slider("Wifi trực tuyến", 0, 5, 3)
        online_boarding = st.slider("Thủ tục trực tuyến", 0, 5, 3)
        seat_comfort = st.slider("Sự thoải mái ghế ngồi", 0, 5, 3)
        entertainment = st.slider("Giải trí", 0, 5, 3)
        
        on_board_service = st.slider("Phục vụ trên tàu bay", 0, 5, 3)
        leg_room = st.slider("Chỗ để chân", 0, 5, 3)
        baggage = st.slider("Vận chuyển hành lý", 0, 5, 3)
        checkin = st.slider("Dịch vụ Check-in", 0, 5, 3)
        food = st.slider("Đồ ăn uống", 0, 5, 3)
        cleanliness = st.slider("Sự sạch sẽ", 0, 5, 3)
        gate_location = st.slider("Vị trí cổng", 0, 5, 3)
        ease_booking = st.slider("Đặt vé trực tuyến", 0, 5, 3)
        time_convenient = st.slider("Giờ bay thuận tiện", 0, 5, 3)

    # --- TỔNG HỢP DỮ LIỆU ---
    data = {
        'Gender': gender_val,
        'Customer Type': cust_type_val,
        'Age': age,
        'Type of Travel': travel_type_val,
        'Class': class_val,
        'Flight Distance': flight_distance,
        'In-flight wifi service': wifi,
        'Online boarding': online_boarding,
        'Seat comfort': seat_comfort,
        'In-flight entertainment': entertainment,
        'On-board service': on_board_service,
        'Leg room service': leg_room,
        'Baggage handling': baggage,
        'Checkin service': checkin,
        'Food and drink': food,
        'Cleanliness': cleanliness,
        'Departure Delay in Minutes': dep_delay,
        'Arrival Delay in Minutes': arr_delay,
        'Ease of Online booking': ease_booking,
        'Gate location': gate_location,
        'Departure/Arrival time convenient': time_convenient
    }
    features = pd.DataFrame(data, index=[0])
    return features

# --- 4. HIỂN THỊ VÀ DỰ BÁO ---
input_df = user_input_features()

st.subheader("📋 Thông tin bạn vừa nhập:")
st.dataframe(input_df)

if st.button("🚀 DỰ BÁO NGAY", type="primary"):
    # Dự báo
    prediction = model.predict(input_df)
    probability = model.predict_proba(input_df)

    st.markdown("---")
    st.subheader("🎯 Kết quả dự báo:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if prediction[0] == 1:
            st.success("🎉 KHÁCH HÀNG: HÀI LÒNG")
            st.metric("Độ tin cậy", f"{probability[0][1]*100:.2f}%")
        else:
            st.error("😡 KHÁCH HÀNG: KHÔNG HÀI LÒNG")
            st.metric("Độ tin cậy", f"{probability[0][0]*100:.2f}%")
    
    with col2:
        if prediction[0] == 0:
            st.warning("⚠️ **Khuyến nghị hành động:**")
            st.write("- Kiểm tra lại kết nối Wifi.")
            st.write("- Gửi email xin lỗi và tặng voucher giảm giá vé lần sau.")
            st.write("- Cải thiện quy trình Check-in online.")