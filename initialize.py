from utils.db_connector import DBConnector, Collections

#Admin user can create/delete users

if __name__ == "__main__":
    connector = DBConnector()
    connector.collection(Collections.USERS).insert_one(
        {
            "username": "admin",
            "password": "$2y$12$RBcV6xWFhHucm4a1YRmQXuEZHqz9NadpMuzIB6xEIXOhg.QzngiiO",
            "scopes": ["admin", "read", "write", "me", "api"],
            "tokens": [], #create new users
            "firstLogin": True
        }
    )
