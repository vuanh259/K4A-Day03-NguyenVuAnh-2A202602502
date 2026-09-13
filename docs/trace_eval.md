# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Vũ Anh
> **Mã Sinh Viên / Mã Học viên:** 2A202602502 
> **Chủ đề Lựa chọn:** Trợ lý Đặt Phòng họp & Thiết bị (Facilities Agent)

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4/ 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? | Trợ lý đặt phòng họp & Thiết bị thì sẽ phải kiểm tra xem liệu phòng hay thiết bị này lúc đó có đang có sẵn không. Nếu không thì đề xuất xem có lựa chọn nào thay thế được luôn không. Nếu không có sự thay thế nào ngay lúc đó thì kiểm tra và đề xuất thời gian thời gian gần nhất mà phòng & thiết bị đó có sẵn cho người dùng.
| **2. Tool Interaction** | 4/ 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? | Agent cần tương tác với các công cụ hoặc hệ thống quản lý nội bộ thông qua MCP Server/API để tra cứu trạng thái phòng họp, thiết bị và thực hiện đặt chỗ. Các dữ liệu này có thể nằm trong cơ sở dữ liệu nội bộ của tổ chức nhưng Agent vẫn cần sử dụng công cụ để truy xuất và cập nhật trạng thái theo thời gian thực.
| **3. Dynamic Decision** | 5/ 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? | Bước tiếp theo hoàn toàn phụ thuộc vào kết quả của bước quan sát trước, do nếu quan sát thấy có phòng họp & thiết bị có thể đặt được luôn thì không cần đến các bước sau
| **4. Long Horizon Goal** | 3/ 5 | Agent cần duy trì mục tiêu và các ràng buộc của yêu cầu đặt phòng xuyên suốt nhiều bước hoặc nhiều lượt tương tác, kể cả khi phải tìm phương án thay thế. Tuy nhiên, quy trình đặt phòng thường được hoàn thành trong một phiên làm việc tương đối ngắn nên mức độ “long horizon” không quá cao.
| **TỔNG ĐIỂM AGENTIC FIT** | **17/ 20** | : Bài toán rất phù hợp triển khai Agentic System.|

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
    {
    "step": 1,
    "query": "kiểm tra cho tôi xem chiều ngày 15/9/2026 có phòng nào trống không",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "find_available_rooms",
    "arguments": {
      "end_time": "17:00",
      "start_time": "13:00",
      "date": "15/09/2026",
      "duration_hours": 1
    },
    "observation": {
      "status": "SUCCESS",
      "date": "15/09/2026",
      "search_start": "13:00",
      "search_end": "17:00",
      "duration_hours": 1,
      "capacity": 0,
      "required_equipment": [],
      "rooms": [
        {
          "room_id": "A101",
          "room_name": "Phòng họp A101",
          "capacity": 20,
          "location": "Tầng 1 - Tòa A",
          "equipment": [
            "Máy chiếu",
            "Micro",
            "Bảng trắng"
          ],
          "available_start": "13:00",
          "date": "15/09/2026",
          "duration_hours": 1
        },
        {
          "room_id": "B201",
          "room_name": "Phòng họp B201",
          "capacity": 30,
          "location": "Tầng 2 - Tòa B",
          "equipment": [
            "Máy chiếu",
            "Micro",
            "Loa",
            "Camera hội nghị"
          ],
          "available_start": "13:00",
          "date": "15/09/2026",
          "duration_hours": 1
        },
        {
          "room_id": "A102",
          "room_name": "Phòng họp A102",
          "capacity": 10,
          "location": "Tầng 1 - Tòa A",
          "equipment": [
            "TV",
            "Bảng trắng"
          ],
          "available_start": "15:00",
          "date": "15/09/2026",
          "duration_hours": 1
        }
      ],
      "message": "Tìm thấy 3 phòng phù hợp."
    },
    "latency_ms": 6364.5
  },
  {
    "step": 2,
    "query": "kiểm tra cho tôi xem chiều ngày 15/9/2026 có phòng nào trống không",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Chiều ngày **15/09/2026** (khung giờ từ 13:00 đến 17:00) hiện có **3 phòng trống** phù hợp:\n\n1. **Phòng A101** (Phòng họp A101)\n   - **Vị trí:** Tầng 1 - Tòa A\n   - **Sức chứa:** 20 người\n   - **Thiết bị:** Máy chiếu, Micro, Bảng trắng\n   - **Khung giờ trống:** Từ **13:00**\n\n2. **Phòng B201** (Phòng họp B201)\n   - **Vị trí:** Tầng 2 - Tòa B\n   - **Sức chứa:** 30 người\n   - **Thiết bị:** Máy chiếu, Micro, Loa, Camera hội nghị\n   - **Khung giờ trống:** Từ **13:00**\n\n3. **Phòng A102** (Phòng họp A102)\n   - **Vị trí:** Tầng 1 - Tòa A\n   - **Sức chứa:** 10 người\n   - **Thiết bị:** TV, Bảng trắng\n   - **Khung giờ trống:** Từ **15:00**\n\nAnh/Chị có muốn đặt phòng nào ở trên không? Vui lòng cung cấp **mã phòng**, **thời gian bắt đầu** và **thời lượng sử dụng** để em hỗ trợ đặt phòng nhé!",
    "latency_ms": 5031.02
  },
  {
    "step": 1,
    "query": "đặt cho tôi phòng có máy chiếu, tôi muốn sử dụng trong 2 giờ bắt đầu từ 13h",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "book_room",
    "arguments": {
      "room_id": "A101",
      "equipment": [
        "Máy chiếu"
      ],
      "datetime_str": "13:00 15/09/2026",
      "duration_hours": 2
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "BK-A101-002",
      "room_id": "A101",
      "room_name": "Phòng họp A101",
      "datetime": "13:00 15/09/2026",
      "duration_hours": 2,
      "equipment": [
        "Máy chiếu"
      ],
      "message": "Đặt phòng A101 thành công vào lúc 13:00 15/09/2026 trong 2 giờ."
    },
    "latency_ms": 8002.99
  },
  {
    "step": 2,
    "query": "đặt cho tôi phòng có máy chiếu, tôi muốn sử dụng trong 2 giờ bắt đầu từ 13h",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Em đã đặt phòng thành công cho Anh/Chị! Dưới đây là thông tin chi tiết:\n\n- **Mã đặt phòng:** `BK-A101-002`\n- **Tên phòng:** Phòng họp A101 (Tầng 1 - Tòa A)\n- **Thời gian bắt đầu:** 13:00 ngày 15/09/2026\n- **Thời lượng:** 2 giờ (13:00 - 15:00)\n- **Thiết bị yêu cầu:** Máy chiếu\n\nNếu Anh/Chị cần hỗ trợ thêm thông tin hoặc thay đổi gì khác, xin vui lòng cho em biết nhé!",
    "latency_ms": 4465.32
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
