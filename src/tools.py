"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Kiểm tra tình trạng một phòng họp cụ thể
    {
        "name": "check_room_availability",
        "description": "Kiểm tra một phòng họp cụ thể có trống tại thời gian yêu cầu hay không.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {
                    "type": "string",
                    "description": "Mã phòng họp cần kiểm tra (ví dụ: 'A101')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian cần kiểm tra phòng (ví dụ: '14:00 15/09/2026')"
                }
            },
            "required": ["room_id", "datetime_str"]
        }
    },

    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'book_room'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đặt phòng họp và thiết bị phục vụ cuộc họp.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - room_id (string): Mã phòng họp cần đặt (ví dụ: 'A101')
    #    - datetime_str (string): Thời gian bắt đầu cuộc họp
    #    - duration_hours (number): Thời lượng sử dụng phòng tính theo giờ
    #    - equipment (array): Danh sách thiết bị cần sử dụng
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "book_room",
        "description": "Đặt một phòng họp cụ thể kèm theo các thiết bị cần thiết phục vụ cuộc họp.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_id": {
                    "type": "string",
                    "description": "Mã phòng họp cần đặt (ví dụ: 'A101')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian bắt đầu sử dụng phòng (ví dụ: '14:00 15/09/2026')"
                },
                "duration_hours": {
                    "type": "number",
                    "description": "Thời lượng sử dụng phòng tính theo giờ (ví dụ: 2)"
                },
                "equipment": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Danh sách thiết bị cần sử dụng (ví dụ: ['Máy chiếu', 'Micro'])"
                }
            },
            "required": [
                "room_id",
                "datetime_str",
                "duration_hours"
            ]
        }
    },

    # Tool 3: Tìm các phòng họp phù hợp theo điều kiện
    {
        "name": "find_available_rooms",
        "description": "Tìm các phòng họp đang trống và phù hợp theo ngày, khung giờ, thời lượng, sức chứa và thiết bị yêu cầu. Sử dụng Tool này khi người dùng muốn tìm phòng nhưng chưa chỉ định mã phòng cụ thể.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Ngày cần tìm phòng (ví dụ: '15/09/2026')"
                },
                "start_time": {
                    "type": "string",
                    "description": "Thời gian bắt đầu sớm nhất có thể sử dụng phòng (ví dụ: '13:00')"
                },
                "end_time": {
                    "type": "string",
                    "description": "Thời gian bắt đầu muộn nhất có thể chấp nhận (ví dụ: '15:00')"
                },
                "duration_hours": {
                    "type": "number",
                    "description": "Thời lượng cần sử dụng phòng tính theo giờ (ví dụ: 2)"
                },
                "capacity": {
                    "type": "integer",
                    "description": "Sức chứa tối thiểu cần có của phòng (ví dụ: 20)"
                },
                "equipment": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Danh sách thiết bị cần có trong phòng (ví dụ: ['Máy chiếu', 'Micro'])"
                }
            },
            "required": [
                "date",
                "start_time",
                "end_time",
                "duration_hours"
            ]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "A101": {
        "room_name": "Phòng họp A101",
        "capacity": 20,
        "location": "Tầng 1 - Tòa A",
        "equipment": [
            "Máy chiếu",
            "Micro",
            "Bảng trắng"
        ],
        "status": "AVAILABLE",
        "booked_slots": [
            {
                "start": "09:00 15/09/2026",
                "duration_hours": 2
            }
        ]
    },
    "A102": {
        "room_name": "Phòng họp A102",
        "capacity": 10,
        "location": "Tầng 1 - Tòa A",
        "equipment": [
            "TV",
            "Bảng trắng"
        ],
        "status": "AVAILABLE",
        "booked_slots": [
            {
                "start": "13:00 15/09/2026",
                "duration_hours": 2
            }
        ]
    },
    "B201": {
        "room_name": "Phòng họp B201",
        "capacity": 30,
        "location": "Tầng 2 - Tòa B",
        "equipment": [
            "Máy chiếu",
            "Micro",
            "Loa",
            "Camera hội nghị"
        ],
        "status": "AVAILABLE",
        "booked_slots": []
    }
}


def parse_datetime(datetime_str: str) -> datetime:
    """Chuyển chuỗi thời gian dạng HH:MM DD/MM/YYYY thành datetime"""
    return datetime.strptime(datetime_str.strip(), "%H:%M %d/%m/%Y")


def is_time_slot_available(room: Dict[str, Any], datetime_str: str, duration_hours: float = 1) -> bool:
    """Kiểm tra phòng có trống trong khoảng thời gian yêu cầu hay không"""
    try:
        requested_start = parse_datetime(datetime_str)
        requested_end = requested_start + timedelta(hours=duration_hours)

        for slot in room.get("booked_slots", []):
            booked_start = parse_datetime(slot["start"])
            booked_end = booked_start + timedelta(hours=slot.get("duration_hours", 1))

            if requested_start < booked_end and requested_end > booked_start:
                return False

        return True
    except Exception:
        return room.get("status") == "AVAILABLE"


def normalize_equipment_name(name: str) -> str:
    """Chuẩn hóa tên thiết bị để so sánh không phân biệt hoa thường"""
    return name.strip().lower()


def execute_check_room_availability(room_id: str, datetime_str: str) -> str:
    """Thực thi kiểm tra tình trạng phòng họp theo mã phòng và thời gian"""
    normalized_room_id = room_id.strip().upper()
    room = MOCK_DATABASE.get(normalized_room_id)

    if not room:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy phòng họp có mã '{room_id}'"
        }, ensure_ascii=False)

    available = (
        room.get("status") == "AVAILABLE"
        and is_time_slot_available(room, datetime_str, 1)
    )

    return json.dumps({
        "status": "SUCCESS",
        "room_id": normalized_room_id,
        "datetime": datetime_str,
        "available": available,
        "data": {
            "room_name": room["room_name"],
            "capacity": room["capacity"],
            "location": room["location"],
            "equipment": room["equipment"],
            "status": "AVAILABLE" if available else "UNAVAILABLE"
        }
    }, ensure_ascii=False)


def execute_book_room(
    room_id: str,
    datetime_str: str,
    duration_hours: float,
    equipment: list = None
) -> str:
    """Thực thi đặt phòng họp và thiết bị"""
    if equipment is None:
        equipment = []

    normalized_room_id = room_id.strip().upper()
    room = MOCK_DATABASE.get(normalized_room_id)

    if not room:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy phòng họp có mã '{room_id}'"
        }, ensure_ascii=False)

    if room.get("status") != "AVAILABLE":
        return json.dumps({
            "status": "UNAVAILABLE",
            "room_id": normalized_room_id,
            "message": f"Phòng {normalized_room_id} hiện không khả dụng."
        }, ensure_ascii=False)

    if not is_time_slot_available(room, datetime_str, duration_hours):
        return json.dumps({
            "status": "UNAVAILABLE",
            "room_id": normalized_room_id,
            "datetime": datetime_str,
            "message": f"Phòng {normalized_room_id} đã có lịch trong khoảng thời gian yêu cầu."
        }, ensure_ascii=False)

    room_equipment_normalized = [
        normalize_equipment_name(item)
        for item in room.get("equipment", [])
    ]

    unavailable_equipment = [
        item for item in equipment
        if normalize_equipment_name(item) not in room_equipment_normalized
    ]

    if unavailable_equipment:
        return json.dumps({
            "status": "EQUIPMENT_UNAVAILABLE",
            "room_id": normalized_room_id,
            "unavailable_equipment": unavailable_equipment,
            "available_equipment": room["equipment"],
            "message": f"Phòng {normalized_room_id} không có đầy đủ thiết bị được yêu cầu."
        }, ensure_ascii=False)

    room["booked_slots"].append({
        "start": datetime_str,
        "duration_hours": duration_hours
    })

    booking_id = f"BK-{normalized_room_id}-{len(room['booked_slots']):03d}"

    return json.dumps({
        "status": "SUCCESS",
        "booking_id": booking_id,
        "room_id": normalized_room_id,
        "room_name": room["room_name"],
        "datetime": datetime_str,
        "duration_hours": duration_hours,
        "equipment": equipment,
        "message": f"Đặt phòng {normalized_room_id} thành công vào lúc {datetime_str} trong {duration_hours} giờ."
    }, ensure_ascii=False)


def execute_find_available_rooms(
    date: str,
    start_time: str,
    end_time: str,
    duration_hours: float,
    capacity: int = 0,
    equipment: list = None
) -> str:
    """Tìm các phòng họp đang trống và phù hợp với yêu cầu"""
    if equipment is None:
        equipment = []

    try:
        search_start = datetime.strptime(
            f"{start_time} {date}",
            "%H:%M %d/%m/%Y"
        )
        search_end = datetime.strptime(
            f"{end_time} {date}",
            "%H:%M %d/%m/%Y"
        )
    except ValueError:
        return json.dumps({
            "status": "INVALID_INPUT",
            "message": "Định dạng ngày hoặc giờ không hợp lệ. Vui lòng dùng ngày DD/MM/YYYY và giờ HH:MM."
        }, ensure_ascii=False)

    if search_end < search_start:
        return json.dumps({
            "status": "INVALID_INPUT",
            "message": "Thời gian kết thúc khung tìm kiếm phải lớn hơn hoặc bằng thời gian bắt đầu."
        }, ensure_ascii=False)

    matched_rooms = []
    current_start = search_start

    while current_start <= search_end:
        datetime_str = current_start.strftime("%H:%M %d/%m/%Y")

        for room_id, room in MOCK_DATABASE.items():
            if room.get("status") != "AVAILABLE":
                continue

            if room.get("capacity", 0) < capacity:
                continue

            room_equipment_normalized = [
                normalize_equipment_name(item)
                for item in room.get("equipment", [])
            ]

            missing_equipment = [
                item for item in equipment
                if normalize_equipment_name(item) not in room_equipment_normalized
            ]

            if missing_equipment:
                continue

            if not is_time_slot_available(room, datetime_str, duration_hours):
                continue

            already_added = any(
                item["room_id"] == room_id
                for item in matched_rooms
            )

            if not already_added:
                matched_rooms.append({
                    "room_id": room_id,
                    "room_name": room["room_name"],
                    "capacity": room["capacity"],
                    "location": room["location"],
                    "equipment": room["equipment"],
                    "available_start": current_start.strftime("%H:%M"),
                    "date": date,
                    "duration_hours": duration_hours
                })

        current_start += timedelta(minutes=30)

    if matched_rooms:
        return json.dumps({
            "status": "SUCCESS",
            "date": date,
            "search_start": start_time,
            "search_end": end_time,
            "duration_hours": duration_hours,
            "capacity": capacity,
            "required_equipment": equipment,
            "rooms": matched_rooms,
            "message": f"Tìm thấy {len(matched_rooms)} phòng phù hợp."
        }, ensure_ascii=False)

    return json.dumps({
        "status": "NOT_FOUND",
        "message": "Không tìm thấy phòng họp phù hợp trong khung thời gian và điều kiện yêu cầu."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "check_room_availability": execute_check_room_availability,
    "book_room": execute_book_room,
    "find_available_rooms": execute_find_available_rooms
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({
                "status": "EXECUTION_ERROR",
                "error": str(e)
            }, ensure_ascii=False)

    return json.dumps({
        "status": "UNKNOWN_TOOL",
        "error": f"Tool '{tool_name}' không tồn tại!"
    }, ensure_ascii=False)


# ==============================================================================
# TEST ĐỘC LẬP FILE tools.py
# ==============================================================================

if __name__ == "__main__":
    print(f"✅ [TOOLS CHECK]: Đã đăng ký thành công {len(TOOLS_SCHEMA)} Native Tools trong TOOLS_SCHEMA!")

    test_result_json = dispatch_tool_call(
        "find_available_rooms",
        {
            "date": "15/09/2026",
            "start_time": "13:00",
            "end_time": "15:00",
            "duration_hours": 2
        }
    )

    test_result = json.loads(test_result_json)

    if test_result.get("status") == "SUCCESS":
        rooms = test_result.get("rooms", [])
        room_ids = ", ".join(room.get("room_id", "") for room in rooms)
        print(f"🧪 Kết quả gọi thử find_available_rooms: Status SUCCESS (Phòng phù hợp: {room_ids})")
    else:
        print(f"❌ Kết quả gọi thử find_available_rooms: {test_result}")