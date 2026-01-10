import pymongo
import certifi

def check_users():
    with open("users_dump.txt", "w", encoding="utf-8") as f:
        f.write("🔍 Inspecting MongoDB Users...\n")
        try:
            uri = "mongodb+srv://aditya2006:adi2006@cluster0.xdbxki9.mongodb.net/gov_access?retryWrites=true&w=majority&appName=Cluster0"
            client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
            db = client['ctrl_a_db']
            
            users = list(db.users.find({}, {"password_hash": 0}))
            
            f.write(f"✅ Found {len(users)} users\n")
            
            for user in users:
                f.write(f"\nUser ID: {user.get('_id')}\n")
                f.write(f"Email: {user.get('email')}\n")
                f.write(f"Disability Type: {user.get('disability_type')}\n")
                f.write(f"Address: {user.get('address')}\n")
                
        except Exception as e:
            f.write(f"❌ Error inspecting users: {e}\n")

if __name__ == "__main__":
    check_users()
