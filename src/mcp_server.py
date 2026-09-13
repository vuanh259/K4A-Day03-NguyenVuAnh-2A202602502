"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class MCPFacilitiesServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    phục vụ Trợ lý Đặt Phòng họp & Thiết bị.
    """

    def __init__(self, server_name: str = "facilities-booking-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        [TASK 2.1] HỌC VIÊN HOÀN THIỆN HÀM THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC.
        """

        # --------------------------------------------------------------------------
        # TODO 2.1: HỌC VIÊN HOÀN THIỆN HÀM GỌI TOOL CHUẨN MCP JSON-RPC
        # 🎯 YÊU CẦU THỰC THI THUẬT TOÁN:
        # 1. Gọi hàm dispatch_tool_call(tool_name, arguments)
        #    để lấy chuỗi JSON kết quả từ Tool Router.
        # 2. Chuyển đổi chuỗi JSON kết quả thành Python Dictionary
        #    bằng json.loads().
        # 3. Đóng gói phản hồi và trả về Dict theo chuẩn MCP JSON-RPC 2.0:
        #    - "jsonrpc": "2.0"
        #    - "server": self.server_name
        #    - "tool": tool_name
        #    - "result": content
        # --------------------------------------------------------------------------

        # Bước 1: Gọi Tool Router
        result_json = dispatch_tool_call(tool_name, arguments)

        # Bước 2: Chuyển chuỗi JSON thành Python Dictionary
        content = json.loads(result_json)

        # Bước 3: Đóng gói phản hồi theo JSON-RPC 2.0
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (facilities-booking-mcp-server)")
    print("==========================================================")

    server = MCPFacilitiesServer()
    tools = server.list_tools()

    print(
        f"✅ Khởi tạo thành công MCP Server: "
        f"{server.server_name} (Version: {server.version})"
    )
    print(f"📦 Số lượng Tools công bố: {len(tools)}")

    # Kiểm tra trạng thái TODO 1.2 (Tool Schema)
    book_tool = next(
        (t for t in tools if t.get("name") == "book_room"),
        None
    )

    if book_tool and not book_tool.get("parameters", {}).get("properties"):
        print(
            "⏳ [TODO 1.2]: Tool 'book_room' chưa được định nghĩa "
            "properties trong 'src/tools.py'."
        )
    else:
        print(
            "✅ [TODO 1.2]: Tool 'book_room' đã có schema đầy đủ."
        )

    # Kiểm tra trạng thái TODO 2.1 (call_tool)
    test_result = server.call_tool(
        "check_room_availability",
        {
            "room_id": "A101",
            "datetime_str": "14:00 15/09/2026"
        }
    )

    if not test_result:
        print(
            "⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. "
            "Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!"
        )
    else:
        print(
            "✅ [TODO 2.1]: Test dispatch tool "
            "'check_room_availability' thành công:"
        )
        print(
            f"   Phản hồi JSON-RPC: "
            f"{json.dumps(test_result, ensure_ascii=False)}"
        )