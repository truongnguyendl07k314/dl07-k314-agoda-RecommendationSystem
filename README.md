# Agoda Hotel Recommender System & Business Insights Portal

Hệ thống Đề xuất Khách sạn Thông minh & Bảng phân tích Phản hồi Khách hàng Đa chiều cho nền tảng Agoda tại Nha Trang. Dự án kết hợp các mô hình Machine Learning tiên tiến (Content-Based, Collaborative Filtering) và Dashboard phân tích dữ liệu kinh doanh trực quan dành cho chủ khách sạn.

---
## Cấu trúc thư mục

```
DL07_k314_27_phanphucloc_nguyennhattruong_ProjectAgoda
├── data/
│   ├── hotel_info_cleaned.csv
│   ├── hotel_comments_cleaned.csv
│   ├── hotel_comments.csv
│   └── hotel_info.csv
|
├── files/
│   ├── emojicon.txt
│   ├── english-vnmese.txt
│   ├── teencode.txt
│   ├── vietnamese-stopwords.txt
│   └── wrong-word.txt
│
├── models/
│   ├── als_item_factors.pkl
│   ├── als_user_factors.pkl
│   ├── cf_mappings.pkl
│   ├── cosine_sim.pkl
│   ├── gensim_dictionary.pkl
│   ├── gensim_index.pkl
│   ├── gensim_tfidf.pkl
│   ├── hotel_insights.pkl
│   ├── surprise_svd.pkl
│   ├── tfidf_vectorizer.pkl
│
├── notebook.ipynb
├── app.py
├── README.md
├── Agoda_Recommender_System_Slide.pptx
└── Ban phan cong cong viec.xlsx
```

---

## Hướng dẫn Cài đặt & Chạy Chương trình

### 1. Cài đặt Thư viện
Đảm bảo máy của bạn đã cài đặt Python (khuyến nghị >= 3.8). Cài đặt các thư viện cần thiết bằng lệnh:
```bash
pip install streamlit pandas numpy scikit-learn gensim scikit-surprise pyspark pyvi matplotlib wordcloud python-pptx
```
*(Lưu ý: Để sử dụng PySpark ALS, bạn cần cài đặt sẵn Java JDK 8/11 và cấu hình biến môi trường `JAVA_HOME`).*

### 2. Huấn luyện Mô hình bằng Jupyter Notebook
Trước khi chạy ứng dụng Streamlit, bạn cần chạy toàn bộ các cell trong Jupyter Notebook để làm sạch dữ liệu, huấn luyện mô hình và lưu trữ các tệp cấu hình, tệp trọng số (pickle) cần thiết:

1. Mở file notebook.ipynb bằng VS Code (hoặc Jupyter Notebook/Google Colab).
2. Chọn môi trường kernel Python thích hợp.
3. Chọn **Run All**

Pipeline này sẽ thực hiện:
*   Làm sạch văn bản tiếng Việt và chạy bộ tách từ `PyVi`.
*   Huấn luyện TF-IDF & Cosine Similarity cho Content-Based Filtering.
*   Huấn luyện Surprise SVD và PySpark ALS cho Collaborative Filtering.
*   Tổng hợp và lưu trữ dữ liệu insights kinh doanh của từng khách sạn vào thư mục `models/`.


### 3. Khởi chạy Ứng dụng Streamlit App
Sau khi pipeline hoàn tất thành công, khởi chạy Dashboard trực quan:
```bash
streamlit run app.py
```
Truy cập ứng dụng tại URL mặc định: `http://localhost:8501`.

---

## Chi tiết các Phân hệ Giao diện

Ứng dụng cung cấp 3 phân hệ chức năng chính được chuyển đổi qua thanh Sidebar:

1.  **Gợi ý & Tìm kiếm Khách sạn**:
    *   **Tìm kiếm tự do (Gensim TF-IDF)**: Cho phép người dùng nhập câu lệnh ngôn ngữ tự nhiên tự do (ví dụ: *"khách sạn trung tâm có hồ bơi sát biển giá rẻ"*). Hệ thống tính độ tương đồng ngữ nghĩa và trả về Top khách sạn phù hợp nhất.
    *   **Gợi ý khách sạn tương tự (Cosine Similarity)**: Chọn một khách sạn cụ thể và nhận ngay danh sách các khách sạn có đặc điểm mô tả và tiện ích tương đồng nhất.
2.  **Báo cáo Insights & Phản hồi**:
    *   Dành cho chủ doanh nghiệp/chủ khách sạn để theo dõi "sức khỏe" dịch vụ của mình qua:
        *   Tỷ lệ đánh giá tích cực/tiêu cực/trung lập.
        *   Phân bố khách du lịch theo Quốc tịch và Nhóm khách đi cùng.
        *   Biểu đồ xu hướng số lượng đánh giá qua 12 tháng gần nhất.
        *   **Word Cloud tích cực & tiêu cực**: Trực quan hóa từ khóa nổi bật trong review sau khi đã được lọc nhiễu đa ngôn ngữ.
        *   **Benchmark 6 tiêu chí**: So sánh điểm số của khách sạn với điểm trung bình toàn hệ thống (Vị trí, Sạch sẽ, Dịch vụ, Tiện nghi, Giá trị tiền tệ, Độ thoải mái). Tự động cảnh báo điểm mạnh/điểm yếu nổi trội (chênh lệch > 0.3 điểm).
3.  **Đề xuất Collaborative Filtering (CF Test)**:
    *   Phân hệ thử nghiệm đề xuất cá nhân hóa. Chủ trang web chọn một hồ sơ khách hàng mẫu (dạng `Tên_Quốc tịch_Nhóm khách`) để xem danh sách gợi ý khách sạn riêng biệt được tạo ra bởi hai thuật toán **Surprise SVD** và **PySpark ALS**.

---

## Các Cải tiến & Khắc phục Lỗi dữ liệu

Trong quá trình xây dựng hệ thống, nhóm đã phát hiện và sửa đổi các vấn đề dữ liệu thực tế quan trọng:
*   **Sửa lỗi phân tích cảm xúc (Sentiment 0%):** Do toàn bộ điểm số đánh giá của Agoda trong tập dữ liệu đều $\ge 6.3$ điểm (không có review tệ thực tế), việc dùng ngưỡng `Score < 6.0` để gán nhãn Negative khiến tỷ lệ tiêu cực luôn bằng 0%. Dự án đã chuyển sang phân loại dựa trên cột `Score Level` có sẵn của Agoda (`Hài lòng` $\rightarrow$ Negative, `Rất tốt` $\rightarrow$ Neutral, `Tuyệt vời/Trên cả tuyệt vời` $\rightarrow$ Positive).
*   **Lọc từ khóa nhiễu đa ngôn ngữ:** Các bình luận chứa cả tiếng Anh, tiếng Pháp, tiếng Đức làm nhiễu Word Cloud. Hệ thống đã tích hợp thêm bộ Stopwords đa ngôn ngữ mở rộng và áp dụng bộ lọc Regex chỉ giữ lại các ký tự thuộc bảng chữ cái Latin và tiếng Việt chuẩn (loại bỏ hoàn toàn các ký tự Nga, CJK, ký tự đặc biệt).
*   **Mở rộng bộ Emoji cảm xúc:** Bổ sung thêm 29 emoji phổ biến xuất hiện trong dữ liệu thực tế vào tệp emojicon.txt để tăng khả năng nhận diện sắc thái cảm xúc.
