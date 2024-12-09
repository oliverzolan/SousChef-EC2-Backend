import logging

class UserModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_by_firebase_uid(self, firebase_uid):
        """
        Check if a user with the given Firebase UID already exists.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT id FROM Users WHERE firebase_uid = %s", (firebase_uid,))
                return cursor.fetchone()
        except Exception as e:
            # Log the error
            logging.error(f"Error fetching user by Firebase UID {firebase_uid}: {str(e)}", exc_info=True)
            # Return an error message
            return {"error": "An error occurred while fetching the user", "details": str(e)}

    def create_user(self, firebase_uid, email):
        """
        Create a new user with the given Firebase UID and email.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Users (firebase_uid, email) VALUES (%s, %s)",
                    (firebase_uid, email)
                )
                self.db.commit()
                return cursor.lastrowid
        except Exception as e:
            # Rollback the transaction if something goes wrong
            self.db.rollback()
            # Log the error
            logging.error(f"Error creating user with Firebase UID {firebase_uid} and email {email}: {str(e)}", exc_info=True)
            # Return an error message
            return {"error": "An error occurred while creating the user", "details": str(e)}