# encoding: utf8
from __future__ import unicode_literals

# Source: https://github.com/wannaphongcom/pythainlp/blob/dev/pythainlp/corpus/stopwords-th.txt
# stop words as whitespace-separated list
STOP_WORDS = set(
    """
นี้ นํา นั้น นัก นอกจาก ทุก ที่สุด ที่ ทําให้ ทํา ทาง ทั้งนี้ ดัง ซึ่ง ช่วง จาก จัด จะ คือ ความ ครั้ง คง ขึ้น ของ
ขอ รับ ระหว่าง รวม ยัง มี มาก มา พร้อม พบ ผ่าน ผล บาง น่า เปิดเผย เปิด เนื่องจาก เดียวกัน เดียว เช่น เฉพาะ เข้า ถ้า
ถูก ถึง ต้อง ต่างๆ ต่าง ต่อ ตาม ตั้งแต่ ตั้ง ด้าน ด้วย อีก อาจ ออก อย่าง อะไร อยู่ อยาก หาก หลาย หลังจาก แต่ เอง เห็น
เลย เริ่ม เรา เมื่อ เพื่อ เพราะ เป็นการ เป็น หลัง หรือ หนึ่ง ส่วน ส่ง สุด สําหรับ ว่า ลง ร่วม ราย ขณะ ก่อน ก็ การ กับ กัน
กว่า กล่าว จึง ไว้ ไป ได้ ให้ ใน โดย แห่ง แล้ว และ แรก แบบ ๆ ทั้ง วัน เขา เคย ไม่ อยาก เกิน เกินๆ เกี่ยวกัน เกี่ยวกับ
เกี่ยวข้อง เกี่ยวเนื่อง เกี่ยวๆ เกือบ เกือบจะ เกือบๆ แก แก่ แก้ไข ใกล้ ใกล้ๆ ไกล ไกลๆ ขณะเดียวกัน ขณะใด ขณะใดๆ ขณะที่ ขณะนั้น ขณะนี้ ขณะหนึ่ง ขวาง
ขวางๆ ขั้น ใคร ใคร่ ใคร่จะ ใครๆ ง่าย ง่ายๆ ไง จง จด จน จนกระทั่ง จนกว่า จนขณะนี้ จนตลอด จนถึง จนทั่ว จนบัดนี้ จนเมื่อ จนแม้ จนแม้น
จรด จรดกับ จริง จริงจัง จริงๆ จริงๆจังๆ จวน จวนจะ จวนเจียน จวบ ซึ่งก็ ซึ่งก็คือ ซึ่งกัน ซึ่งกันและกัน ซึ่งได้แก่ ซึ่งๆ ณ ด้วย ด้วยกัน ด้วยเช่นกัน ด้วยที่ ด้วยประการฉะนี้
ด้วยเพราะ ด้วยว่า ด้วยเหตุที่ ด้วยเหตุนั้น ด้วยเหตุนี้ ด้วยเหตุเพราะ ด้วยเหตุว่า ด้วยเหมือนกัน ดั่ง ดังกล่าว ดังกับ ดั่งกับ ดังกับว่า ดั่งกับว่า ดังเก่า
ดั่งเก่า ดังเคย ใดๆ ได้ ได้แก่ ได้แต่ ได้ที่ ได้มา ได้รับ ตน ตนเอง ตนฯ ตรง ตรงๆ ตลอด ตลอดกาล ตลอดกาลนาน ตลอดจน ตลอดถึง ตลอดทั้ง
ตลอดทั่ว ตลอดทั่วถึง ตลอดทั่วทั้ง ตลอดปี ตลอดไป ตลอดมา ตลอดระยะเวลา ตลอดวัน ตลอดเวลา ตลอดศก ต่อ ต่อกัน ถึงแก่ ถึงจะ ถึงบัดนั้น ถึงบัดนี้
ถึงเมื่อ ถึงเมื่อใด ถึงเมื่อไร ถึงแม้ ถึงแม้จะ ถึงแม้ว่า ถึงอย่างไร ถือ ถือว่า ถูกต้อง ถูกๆ เถอะ เถิด ทรง ทว่า ทั้งคน ทั้งตัว ทั้งที ทั้งที่ ทั้งนั้น ทั้งนั้นด้วย ทั้งนั้นเพราะ
นอก นอกจากที่ นอกจากนั้น นอกจากนี้ นอกจากว่า นอกนั้น นอกเหนือ นอกเหนือจาก น้อย น้อยกว่า น้อยๆ นะ น่ะ นักๆ นั่น นั่นไง นั่นเป็น นั่นแหละ
นั่นเอง นั้นๆ นับ นับจากนั้น นับจากนี้ นับตั้งแต่ นับแต่ นับแต่ที่ นับแต่นั้น เป็นต้น เป็นต้นไป เป็นต้นมา เป็นแต่ เป็นแต่เพียง เป็นที เป็นที่ เป็นที่สุด เป็นเพราะ
เป็นเพราะว่า เป็นเพียง เป็นเพียงว่า เป็นเพื่อ เป็นอัน เป็นอันมาก เป็นอันว่า เป็นอันๆ เป็นอาทิ เป็นๆ เปลี่ยน เปลี่ยนแปลง เปิด เปิดเผย ไป่ ผ่าน ผ่านๆ
ผิด ผิดๆ ผู้ เพียงเพื่อ เพียงไร เพียงไหน เพื่อที่ เพื่อที่จะ เพื่อว่า เพื่อให้ ภาค ภาคฯ ภาย ภายใต้ ภายนอก ภายใน ภายภาค ภายภาคหน้า ภายหน้า ภายหลัง
มอง มองว่า มัก มักจะ มัน มันๆ มั้ย มั้ยนะ มั้ยนั่น มั้ยเนี่ย มั้ยล่ะ ยืนนาน ยืนยง ยืนยัน ยืนยาว เยอะ เยอะแยะ เยอะๆ แยะ แยะๆ รวด รวดเร็ว ร่วม รวมกัน ร่วมกัน
รวมด้วย ร่วมด้วย รวมถึง รวมทั้ง ร่วมมือ รวมๆ ระยะ ระยะๆ ระหว่าง รับรอง รึ รึว่า รือ รือว่า สิ้นกาลนาน สืบเนื่อง สุดๆ สู่ สูง สูงกว่า สูงส่ง สูงสุด สูงๆ เสมือนกับ
เสมือนว่า เสร็จ เสร็จกัน เสร็จแล้ว เสร็จสมบูรณ์ เสร็จสิ้น เสีย เสียก่อน เสียจน เสียจนกระทั่ง เสียจนถึง เสียด้วย เสียนั่น เสียนั่นเอง เสียนี่ เสียนี่กระไร เสียยิ่ง
เสียยิ่งนัก เสียแล้ว ใหญ่ๆ ให้ดี ให้แด่ ให้ไป ใหม่ ให้มา ใหม่ๆ ไหน ไหนๆ อดีต อนึ่ง อย่าง อย่างเช่น อย่างดี อย่างเดียว อย่างใด อย่างที่ อย่างน้อย อย่างนั้น
อย่างนี้ อย่างโน้น ก็คือ ก็แค่ ก็จะ ก็ดี ก็ได้ ก็ต่อเมื่อ ก็ตาม ก็ตามแต่ ก็ตามที ก็แล้วแต่ กระทั่ง กระทำ กระนั้น กระผม กลับ กล่าวคือ กลุ่ม กลุ่มก้อน
กลุ่มๆ กว้าง กว้างขวาง กว้างๆ ก่อนหน้า ก่อนหน้านี้ ก่อนๆ กันดีกว่า กันดีไหม กันเถอะ กันนะ กันและกัน กันไหม กันเอง กำลัง กำลังจะ กำหนด กู เก็บ
เกิด เกี่ยวข้อง แก่ แก้ไข ใกล้ ใกล้ๆ ข้า ข้าง ข้างเคียง ข้างต้น ข้างบน ข้างล่าง ข้างๆ ขาด ข้าพเจ้า ข้าฯ เข้าใจ เขียน คงจะ คงอยู่ ครบ ครบครัน ครบถ้วน
ครั้งกระนั้น ครั้งก่อน ครั้งครา ครั้งคราว ครั้งใด ครั้งที่ ครั้งนั้น ครั้งนี้ ครั้งละ ครั้งหนึ่ง ครั้งหลัง ครั้งหลังสุด ครั้งไหน ครั้งๆ ครัน ครับ ครา คราใด คราที่ ครานั้น ครานี้ คราหนึ่ง
คราไหน คราว คราวก่อน คราวใด คราวที่ คราวนั้น คราวนี้ คราวโน้น คราวละ คราวหน้า คราวหนึ่ง คราวหลัง คราวไหน คราวๆ คล้าย คล้ายกัน คล้ายกันกับ
คล้ายกับ คล้ายกับว่า คล้ายว่า ควร ค่อน ค่อนข้าง ค่อนข้างจะ ค่อยไปทาง ค่อนมาทาง ค่อย ค่อยๆ คะ ค่ะ คำ คิด คิดว่า คุณ คุณๆ
เคยๆ แค่ แค่จะ แค่นั้น แค่นี้ แค่เพียง แค่ว่า แค่ไหน ใคร่ ใคร่จะ ง่าย ง่ายๆ จนกว่า จนแม้ จนแม้น จังๆ จวบกับ จวบจน จ้ะ จ๊ะ จะได้ จัง จัดการ จัดงาน จัดแจง
จัดตั้ง จัดทำ จัดหา จัดให้ จับ จ้า จ๋า จากนั้น จากนี้  จากนี้ไป จำ จำเป็น  จำพวก จึงจะ จึงเป็น จู่ๆ ฉะนั้น ฉะนี้ ฉัน เฉกเช่น เฉย เฉยๆ ไฉน ช่วงก่อน
ช่วงต่อไป ช่วงถัดไป ช่วงท้าย ช่วงที่ ช่วงนั้น ช่วงนี้ ช่วงระหว่าง ช่วงแรก ช่วงหน้า ช่วงหลัง ช่วงๆ ช่วย ช้า ช้านาน ชาว ช้าๆ เช่นก่อน เช่นกัน เช่นเคย
เช่นดัง เช่นดังก่อน เช่นดังเก่า เช่นดังที่ เช่นดังว่า เช่นเดียวกัน เช่นเดียวกับ เช่นใด เช่นที่ เช่นที่เคย เช่นที่ว่า เช่นนั้น เช่นนั้นเอง เช่นนี้ เช่นเมื่อ เช่นไร เชื่อ
เชื่อถือ เชื่อมั่น เชื่อว่า ใช่ ใช่ไหม ใช้ ซะ ซะก่อน ซะจน ซะจนกระทั่ง ซะจนถึง ซึ่งได้แก่ ด้วยกัน ด้วยเช่นกัน ด้วยที่ ด้วยเพราะ ด้วยว่า ด้วยเหตุที่ ด้วยเหตุนั้น
ด้วยเหตุนี้ ด้วยเหตุเพราะ ด้วยเหตุว่า ด้วยเหมือนกัน ดังกล่าว ดังกับว่า ดั่งกับว่า ดังเก่า ดั่งเก่า ดั่งเคย ต่างก็ ต่างหาก ตามด้วย ตามแต่ ตามที่
ตามๆ เต็มไปด้วย เต็มไปหมด เต็มๆ แต่ก็ แต่ก่อน แต่จะ แต่เดิม แต่ต้อง แต่ถ้า แต่ทว่า แต่ที่ แต่นั้น แต่เพียง แต่เมื่อ แต่ไร แต่ละ แต่ว่า แต่ไหน แต่อย่างใด โต
โตๆ ใต้ ถ้าจะ ถ้าหาก ถึงแก่ ถึงแม้ ถึงแม้จะ ถึงแม้ว่า ถึงอย่างไร ถือว่า ถูกต้อง ทว่า ทั้งนั้นด้วย ทั้งปวง ทั้งเป็น ทั้งมวล ทั้งสิ้น ทั้งหมด ทั้งหลาย ทั้งๆ ทัน
ทันใดนั้น ทันที ทันทีทันใด ทั่ว ทำไม ทำไร ทำให้ ทำๆ ที ที่จริง ที่ซึ่ง ทีเดียว ทีใด ที่ใด ที่ได้ ทีเถอะ ที่แท้ ที่แท้จริง ที่นั้น ที่นี้ ทีไร ทีละ ที่ละ
ที่แล้ว ที่ว่า ที่แห่งนั้น ที่ไหน ทีๆ ที่ๆ ทุกคน ทุกครั้ง ทุกครา ทุกคราว ทุกชิ้น ทุกตัว ทุกทาง ทุกที ทุกที่ ทุกเมื่อ ทุกวัน ทุกวันนี้ ทุกสิ่ง ทุกหน ทุกแห่ง ทุกอย่าง
ทุกอัน ทุกๆ เท่า เท่ากัน เท่ากับ เท่าใด เท่าที่ เท่านั้น เท่านี้ เท่าไร เท่าไหร่ แท้ แท้จริง เธอ นอกจากว่า น้อย น้อยกว่า น้อยๆ น่ะ นั้นไว นับแต่นี้ นาง
นางสาว น่าจะ นาน นานๆ นาย นำ นำพา นำมา นิด นิดหน่อย นิดๆ นี่ นี่ไง นี่นา นี่แน่ะ นี่แหละ นี้แหล่ นี่เอง นี้เอง นู่น นู้น เน้น เนี่ย
เนี่ยเอง ในช่วง ในที่ ในเมื่อ ในระหว่าง บน บอก บอกแล้ว บอกว่า บ่อย บ่อยกว่า บ่อยครั้ง บ่อยๆ บัดดล บัดเดี๋ยวนี้ บัดนั้น บัดนี้ บ้าง บางกว่า
บางขณะ บางครั้ง บางครา บางคราว บางที บางที่ บางแห่ง บางๆ ปฏิบัติ ประกอบ ประการ ประการฉะนี้ ประการใด ประการหนึ่ง ประมาณ ประสบ ปรับ
ปรากฏ ปรากฏว่า ปัจจุบัน ปิด เป็นด้วย เป็นดัง เป็นต้น เป็นแต่ เป็นเพื่อ เป็นอัน เป็นอันมาก เป็นอาทิ ผ่านๆ ผู้ ผู้ใด เผื่อ เผื่อจะ เผื่อที่ เผื่อว่า ฝ่าย
ฝ่ายใด พบว่า พยายาม พร้อมกัน พร้อมกับ พร้อมด้วย พร้อมทั้ง พร้อมที่ พร้อมเพียง พวก พวกกัน พวกกู พวกแก พวกเขา พวกคุณ พวกฉัน พวกท่าน
พวกที่ พวกเธอ พวกนั้น พวกนี้ พวกนู้น พวกโน้น พวกมัน พวกมึง พอ พอกัน พอควร พอจะ พอดี พอตัว พอที พอที่ พอเพียง พอแล้ว พอสม พอสมควร
พอเหมาะ พอๆ พา พึง พึ่ง พื้นๆ พูด เพราะฉะนั้น เพราะว่า เพิ่ง เพิ่งจะ เพิ่ม เพิ่มเติม เพียง เพียงแค่ เพียงใด เพียงแต่ เพียงพอ เพียงเพราะ
เพื่อว่า เพื่อให้ ภายใต้ มองว่า มั๊ย มากกว่า มากมาย มิ มิฉะนั้น มิใช่ มิได้ มีแต่ มึง มุ่ง มุ่งเน้น มุ่งหมาย เมื่อก่อน เมื่อครั้ง เมื่อครั้งก่อน
เมื่อคราวก่อน เมื่อคราวที่ เมื่อคราว เมื่อคืน เมื่อเช้า เมื่อใด เมื่อนั้น เมื่อนี้ เมื่อเย็น เมื่อไร เมื่อวันวาน เมื่อวาน เมื่อไหร่ แม้ แม้กระทั่ง แม้แต่ แม้นว่า แม้ว่า
ไม่ค่อย ไม่ค่อยจะ ไม่ค่อยเป็น ไม่ใช่ ไม่เป็นไร ไม่ว่า ยก ยกให้ ยอม ยอมรับ ย่อม ย่อย ยังคง ยังงั้น ยังงี้ ยังโง้น ยังไง ยังจะ ยังแต่ ยาก
ยาว ยาวนาน ยิ่ง ยิ่งกว่า ยิ่งขึ้น ยิ่งขึ้นไป ยิ่งจน ยิ่งจะ ยิ่งนัก ยิ่งเมื่อ ยิ่งแล้ว ยิ่งใหญ่ ร่วมกัน รวมด้วย ร่วมด้วย รือว่า เร็ว เร็วๆ เราๆ เรียก เรียบ เรื่อย
เรื่อยๆ ไร ล้วน ล้วนจน ล้วนแต่ ละ ล่าสุด เล็ก เล็กน้อย เล็กๆ เล่าว่า แล้วกัน แล้วแต่ แล้วเสร็จ วันใด วันนั้น วันนี้ วันไหน สบาย สมัย สมัยก่อน
สมัยนั้น สมัยนี้ สมัยโน้น ส่วนเกิน ส่วนด้อย ส่วนดี ส่วนใด ส่วนที่ ส่วนน้อย ส่วนนั้น ส่วนมาก ส่วนใหญ่ สั้น สั้นๆ สามารถ สำคัญ สิ่ง
สิ่งใด สิ่งนั้น สิ่งนี้ สิ่งไหน สิ้น เสร็จแล้ว เสียด้วย เสียแล้ว แสดง แสดงว่า หน หนอ หนอย หน่อย หมด หมดกัน หมดสิ้น หรือไง หรือเปล่า หรือไม่ หรือยัง
หรือไร หากแม้ หากแม้น หากแม้นว่า หากว่า หาความ หาใช่ หารือ เหตุ เหตุผล เหตุนั้น เหตุนี้ เหตุไร เห็นแก่ เห็นควร เห็นจะ เห็นว่า เหลือ เหลือเกิน เหล่า
เหล่านั้น เหล่านี้ แห่งใด แห่งนั้น แห่งนี้ แห่งโน้น แห่งไหน แหละ ให้แก่ ใหญ่ ใหญ่โต อย่างเช่น อย่างดี อย่างเดียว อย่างใด อย่างที่ อย่างน้อย อย่างนั้น อย่างนี้
อย่างโน้น อย่างมาก อย่างยิ่ง อย่างไร อย่างไรก็ อย่างไรก็ได้ อย่างไรเสีย อย่างละ อย่างหนึ่ง อย่างไหน อย่างๆ อัน อันจะ อันใด อันได้แก่ อันที่
อันที่จริง อันที่จะ อันเนื่องมาจาก อันละ อันไหน อันๆ อาจจะ อาจเป็น อาจเป็นด้วย อื่น อื่นๆ เอ็ง เอา ฯ ฯล ฯลฯ
""".split()
)
