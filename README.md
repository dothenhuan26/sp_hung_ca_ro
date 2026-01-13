# Hướng dẫn chạy project Streamlit

Tệp này hướng dẫn cách thiết lập và chạy nhanh project Streamlit có trong thư mục này (`test.py`). Các lệnh dành cho shell zsh (Linux).

## Yêu cầu
- Python 3.8+ (khuyến nghị 3.9–3.11)
- pip (đi kèm Python)
- Trình duyệt (Chrome / Firefox)

## 1. Mở terminal và chuyển vào thư mục project
```bash
cd /home/nhuandt3/PyCharmMiscProject
pwd
ls -la
```

## 2. Tạo virtual environment và kích hoạt
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Cập nhật pip và cài dependencies
Tệp `requirements.txt` đã có sẵn trong repo và chứa:
```
streamlit
pandas
plotly
```
Cài bằng:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Hoặc cài từng gói nếu không dùng `requirements.txt`:
```bash
pip install streamlit pandas plotly
```

## 4. Chạy ứng dụng Streamlit (foreground)
Lệnh này sẽ chạy app ở cổng 8501 và hiển thị log trực tiếp trên terminal:
```bash
streamlit run test.py --server.port 8501
```
Mở trình duyệt tới: http://localhost:8501

## 5. Chạy ở background (daemon) và ghi log
Nếu muốn chạy dưới nền, dùng `nohup` và lưu PID + log:
```bash
nohup streamlit run test.py --server.port 8501 --server.headless true > streamlit.log 2>&1 & echo $! > streamlit.pid
```
Kiểm tra PID và log:
```bash
cat streamlit.pid
tail -n 200 streamlit.log
```
Dừng server:
```bash
kill $(cat streamlit.pid) || true
rm -f streamlit.pid
```

## 6. Kiểm tra cổng và tiến trình
```bash
# tìm tiến trình đang lắng nghe cổng 8501
lsof -i :8501
# hoặc kiểm tra tiến trình theo PID
ps -p $(cat streamlit.pid) -o pid,cmd
# kiểm tra HTTP
curl -I http://localhost:8501
```

## 7. Vấn đề thường gặp & cách xử lý
- Thiếu module (ModuleNotFoundError):
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

- Cổng 8501 đã bị chiếm:
```bash
lsof -i :8501
kill -9 <PID>
# hoặc chạy trên cổng khác
streamlit run test.py --server.port 8502
```

- Lỗi truy cập file DB `data_baocao.db` (quyền/owner):
```bash
ls -l data_baocao.db
sudo chown $(whoami):$(whoami) data_baocao.db
chmod 664 data_baocao.db
```
Ghi chú: nếu file DB chưa tồn tại, `test.py` có thể tự tạo khi chạy (tùy implement).

- Lỗi mã hóa CSV (ký tự lạ): đặt locale UTF-8
```bash
export LANG=en_US.UTF-8
```

- Nếu Streamlit không mở trình duyệt tự động (máy chủ headless): mở thủ công hoặc dùng SSH port-forward.

## 8. Tối ưu & gợi ý
- Thêm `.venv/` vào `.gitignore` (đã có sẵn trong repo nếu bạn dùng file tôi tạo).
- Nếu muốn ghi phiên bản chính xác của các gói:
```bash
pip freeze > requirements.txt
```
- Muốn deploy trên server, cân nhắc Docker hoặc reverse-proxy (nginx) để phục vụ ở cổng 80/443.

---
Nếu bạn muốn, tôi có thể:
- Chạy hộ các lệnh trên trong workspace và gửi log/kết quả (PID, log). Trả lời “Chạy hộ” để tôi thực hiện.
- Hoặc cập nhật README thêm phần Dockerfile / hướng dẫn deploy.

