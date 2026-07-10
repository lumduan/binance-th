# การติดตั้ง

[หน้าแรก](../index.md) > เริ่มต้นใช้งาน > การติดตั้ง

[English](../../getting-started/installation.md) · **ไทย**

binance-th ต้องใช้ **Python 3.12 ขึ้นไป**

## ติดตั้ง

```bash
uv add binance-th        # แนะนำ
pip install binance-th
```

เท่านี้ก็พร้อมใช้งานข้อมูลตลาดสาธารณะและ WebSocket stream แล้ว ส่วน dependency ที่ต้องใช้ตอนรันทาม —
`httpx`, `pydantic`, `pydantic-settings` และ `websockets` — จะถูกติดตั้งตามมาให้อัตโนมัติ

## ตรวจสอบ

```bash
python -c "import binance_th; print(binance_th.__version__)"
# 1.0.0
```

## การตรวจสอบชนิด (type checking)

binance-th แนบไฟล์ `py.typed` มาให้ ดังนั้น `mypy` และ editor ของคุณจะรับรู้ชนิดของมันได้ทันทีโดยไม่ต้องตั้งค่าเพิ่ม

## ดูเพิ่มเติม

- [เริ่มต้นอย่างรวดเร็ว](quickstart.md) — สคริปต์แรกของคุณ
- [การยืนยันตัวตน](authentication.md) — จำเป็นเฉพาะการเรียกแบบ signed และ user-data stream
