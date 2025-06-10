# simple_chatbot.py
"""
A simple rule-based chatbot for Forever Boutique (no OpenAI, no async, no complex logic)
"""

def get_simple_response(message: str) -> str:
    msg = message.strip().lower()
    if any(kw in msg for kw in ["ปิดกี่โมง", "เปิดกี่โมง", "เวลาเปิด", "เวลา ปิด", "เปิดกี่โมง", "เวลาปิด", "ปิดมั้ย", "ปิดไหม"]):
        return "ร้านเปิดจันทร์-เสาร์ 10:00-20:00 น. อาทิตย์ 11:00-19:00 น. ค่ะ"
    if any(kw in msg for kw in ["ที่อยู่", "อยู่ที่ไหน", "ร้านอยู่ไหน", "พิกัด", "location"]):
        return "Block28x สามย่าน วังใหม่ ซอย จุฬาลงกรณ์ 5 กรุงเทพฯ ค่ะ"
    if any(kw in msg for kw in ["ราคา", "เท่าไหร่", "เท่าไร"]):
        return "ชุดราตรี 8,000-35,000 บาท, ชุดค็อกเทล 6,000-18,000 บาท ค่ะ"
    if any(kw in msg for kw in ["ชุด", "สินค้า", "มีอะไร"]):
        return "มีชุดราตรี ชุดค็อกเทล ชุดเจ้าสาว โทร 082 919 7199 ค่ะ"
    if any(kw in msg for kw in ["เบอร์", "โทร", "ติดต่อ"]):
        return "082 919 7199 ค่ะ"
    if any(kw in msg for kw in ["ที่จอดรถ", "parking"]):
        return "มีที่จอดรถของสามย่านที่สามารถใช้บริการได้ค่ะ"
    return "ขออภัยค่ะ สามารถตอบข้อมูลเกี่ยวกับเวลาเปิด-ปิด ที่อยู่ ราคา ชุด หรือการติดต่อร้านได้ค่ะ ถ้าต้องการสอบถามเพิ่มเติม โทร 082 919 7199 ค่ะ"
