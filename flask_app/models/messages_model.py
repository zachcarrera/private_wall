from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask_app.models import users_model
from flask import flash
import datetime

class Message:
    def __init__(self, data):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.recipient_id = data["recipient_id"]
        self.content = data["content"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]


    def time_since(self):
        # return the time since the message created in formatted string
        time_delta1 = datetime.datetime.now() - self.created_at
        print(time_delta1.total_seconds())

        formatted_time = ""

        seconds = time_delta1.total_seconds()

        if seconds < 60:
            formatted_time = f"{round(seconds)} seconds"
        elif seconds/60 < 60:
            formatted_time = f"{round(seconds/60)} minutes"
        elif seconds/3600 < 24:
            formatted_time = f"{round(seconds/3600)} hours"
        else:
            formatted_time = f"{round(seconds/86400)} days"
        
        return formatted_time



    # ----- CREATE -----
    @classmethod
    def new_message(cls, data):
        
        query = """
                INSERT INTO messages (user_id, recipient_id, content)
                VALUES ( %(user_id)s, %(recipient_id)s, %(content)s)"""

        return connectToMySQL(DATABASE).query_db(query, data)

    # ----- READ -----
    @classmethod
    def get_all_for_id(cls,data):
        # query db for all messages sent to one user

        query = """
                SELECT * FROM messages
                JOIN users ON messages.user_id = users.id
                WHERE recipient_id = %(id)s;
                """

        results = connectToMySQL(DATABASE).query_db(query, data)

        # make an empty list for all messages
        messages = []

        # loop through all the results and make a message
        # instance and attach the sender as a User instance
        for row in results:
            message = cls(row)

            sender_data = {
                **row,
                "id": row["users.id"],
                "created_at": row["users.created_at"],
                "updated_at": row["users.updated_at"]
            }
            
            message.sender = users_model.User(sender_data)
            messages.append(message)
        
        return messages

    # ----- DELETE -----
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM messages WHERE id = %(id)s"

        return connectToMySQL(DATABASE).query_db(query, data)


    # ----- VALIDATIONS
    @staticmethod
    def validate(form):
        is_valid = True
        
        if len(form["content"]) < 5:
            flash("Message must be atleast 5 characters.")
            is_valid = False
        
        return is_valid