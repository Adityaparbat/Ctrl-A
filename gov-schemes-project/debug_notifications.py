
import pymongo
import certifi
from bson.objectid import ObjectId
from datetime import datetime

uri = "mongodb+srv://aditya2006:adi2006@cluster0.xdbxki9.mongodb.net/gov_access?retryWrites=true&w=majority&appName=Cluster0"

def debug_notifications():
    try:
        client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
        db = client['ctrl_a_db']
        
        print(f"{'ID':<24} | {'Email':<30} | {'Type':<20} | {'Address':<30}")
        print("-" * 110)
        users = list(db.users.find())
        for u in users:
            d_type = u.get('disability_type', 'N/A')
            addr = u.get('address', 'N/A') or 'N/A'
            print(f"{str(u['_id']):<24} | {u.get('email', 'N/A'):<30} | {d_type:<20} | {addr:<30}")
            
        if not users:
            print("No users found!")
            return

        target_user = users[0]
        user_id = target_user['_id']
        print(f"\n--- ATTEMPTING TO NOTIFY USER: {target_user.get('email')} ({user_id}) ---")
        
        notification = {
            "user_id": str(user_id),
            "message": f"DEBUG TEST NOTIFICATION {datetime.now().strftime('%H:%M:%S')}: If you see this, DB connection is working.",
            "is_read": False,
            "created_at": datetime.now()
        }
        
        result = db.notifications.insert_one(notification)
        print(f"Inserted notification with ID: {result.inserted_id}")
        
        print("\n--- VERIFYING INSERTION ---")
        saved = db.notifications.find_one({"_id": result.inserted_id})
        print(f"Retrieved: {saved}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_notifications()
