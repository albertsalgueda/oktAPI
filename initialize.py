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
                "password": "$2b$12$t2dj3l9K2HQCjIPdnso4BeJ672WHzKnzKiEFEkaHCi9ZJM5bUW9p.",
                "scopes": ["admin", "read", "write", "me", "api"],
                "tokens": [],
                "firstLogin": False
            }
        )
    else:
        print("Admin user already exist.")
