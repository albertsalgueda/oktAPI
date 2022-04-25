from utils.db_connector import DBConnector, Collections

if __name__ == "__main__":
    #os.system('')
    connector = DBConnector()
    if connector.collection(Collections.USERS).find_one(
        {
            "username": "admin"
        }
    ) is None:
        connector.collection(Collections.USERS).insert_one(
            {
                "username": "admin",
                "password": "$2b$12$EYKzmTkytuuuzCvBcmhjVu9zrynZAwCwUxMcAK2z98dkJ1S2wZ8Ea",
                "scopes": ["admin", "read", "write", "me", "api"],
                "tokens": [],
                "firstLogin": True
            }
        )
    else:
        print("Admin user already exist.")
