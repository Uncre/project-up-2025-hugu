from postimage import resize_image, post_image
from save_to_db import init_db, save_to_db
#uuidじゃなくていい　インクリメントでおｋ

resize_image(R"C:\Users\hugu\Desktop\python\receipt_kanri\images\1741330693309.jpg")
response = post_image(R"C:\Users\hugu\Desktop\python\receipt_kanri\images\1741330693309.jpg")

init_db()
save_to_db(response)