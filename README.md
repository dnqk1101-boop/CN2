# AsynapRous Framework 

AsynapRous là một framework định tuyến web và RESTful gọn nhẹ có thể tùy biến, được xây dựng hoàn toàn bằng Python.

##  Cấu trúc dự án

```text
CO3094-asynaprous/
├── apps/
│   └── sampleapp.py       # Ứng dụng mẫu P2P nhắn tin REST sử dụng AsynapRous
├── daemon/
│   ├── asynaprous.py      # Framework định tuyến lõi (@app.route)
│   ├── backend.py         # Máy chủ TCP tự tạo xử lý kết nối đồng thời
│   ├── httpadapter.py     # Trình phân tích và xử lý Request/Response HTTP
│   ├── request.py         # Lớp bao bọc Request HTTP
│   ├── response.py        # Lớp bao bọc Response HTTP
│   ├── proxy.py           # Các thành phần Proxy (nếu có)
│   └── dictionary.py      # Dictionary không phân biệt chữ hoa/thường cho HTTP headers
├── start_sampleapp.py     # File chạy chính của ứng dụng mẫu
└── README.md              # File bạn đang xem!
```

##  Hướng dẫn sử dụng

### Yêu cầu hệ thống
* Python 3.7 trở lên (để hỗ trợ `asyncio` và các tính năng Python hiện đại). Không yêu cầu cài đặt bất kỳ gói bên ngoài nào qua `pip`!

### Khởi chạy ứng dụng mẫu

Ứng dụng mẫu cung cấp một tập hợp các endpoint cho hệ thống chat Hybrid P2P (`/login`, `/submit-info`, `/get-list`, `/send-peer`, v.v.).

Để khởi động máy chủ, hãy đi tới thư mục dự án và chạy lệnh sau trên Terminal / Command Prompt:

```bash
python start_sampleapp.py --server-ip 127.0.0.1 --server-port 8000
```

*(Mặc định, máy chủ sẽ lắng nghe ở `0.0.0.0:8000` nếu không có tham số nào được truyền vào).*

### Ví dụ sử dụng (bằng cURL)


**1. Đăng nhập vào hệ thống**
```bash
# Mật khẩu được thiết lập cứng là 1234 trong file sampleapp.py
curl.exe -v -X POST http://localhost:8000/login -H "Authorization: Basic dXNlcjoxMjM0"
```

**2. Gửi tin nhắn đến Peer**
```bash
curl.exe -X POST http://localhost:8000/send-peer -H "Content-Type: application/json" -d '{\"sender\": \"Alice\", \"message\": \"Hello from AsynapRous!\"}'
```

**3. Lấy danh sách Peer**
```bash
curl.exe -X GET http://localhost:8000/get-list -H "Authorization: Basic dXNlcjoxMjM0"
```

##  Cơ chế hoạt động

### Đổi chế độ xử lý đồng thời (Concurrency Mode)
Trong file `daemon/backend.py`, bạn có thể chuyển đổi qua lại giữa các kiến trúc xử lý đồng thời khác nhau bằng cách sửa biến toàn cục `mode_async`:
```python
# Chọn một trong các chế độ sau:
# mode_async = "callback"
mode_async = "coroutine"
# mode_async = "threading"
```

### Tự tạo ứng dụng của riêng bạn
Việc xây dựng một ứng dụng riêng rất đơn giản, chỉ cần định nghĩa các route của bạn:

```python
from daemon import AsynapRous

app = AsynapRous()

@app.route('/hello', methods=['GET'])
def hello_world(req, resp):
    # Cấu hình status, headers, v.v. trên biến resp nếu cần
    return b'{"message": "Hello World!"}'

if __name__ == "__main__":
    app.prepare_address('127.0.0.1', 8080)
    app.run()
```


