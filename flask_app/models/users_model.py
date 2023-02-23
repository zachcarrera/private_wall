from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE, BCRYPT
from flask import flash

import re

# regex we will use to test email validity
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]


    # ----- CREATE -----
    @classmethod
    def create(cls, form):
        query = """INSERT INTO users (first_name, last_name, email, password)
                    VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"""

        data = {
            **form,
            "password": BCRYPT.generate_password_hash(form["password"])
        }
        
        
        return connectToMySQL(DATABASE).query_db(query, data)


    # ----- READ -----

    @classmethod
    def get_one_by_id(cls, data):
        # query the db for the user with a specific email

        query = """SELECT * FROM users WHERE id = %(id)s;"""

        results = connectToMySQL(DATABASE).query_db(query,data)

        if results:
            return cls(results[0])
        
        return False


    @classmethod
    def get_one_by_email(cls, data):
        # query the db for the user with a specific email

        query = """SELECT * FROM users WHERE email = %(email)s;"""

        results = connectToMySQL(DATABASE).query_db(query,data)

        if results:
            return cls(results[0])
        
        return False

    @classmethod
    def get_other_users(cls, data):
        # get all users except the user of a specific id

        query = "SELECT * FROM users WHERE id != %(id)s ORDER BY first_name ASC;"

        results = connectToMySQL(DATABASE).query_db(query, data)

        users = []
        for row in results:
            users.append(cls(row))

        return users






    # ----- VALIDATIONS -----
    @classmethod
    def validate_login(cls, data):

        found_user = cls.get_one_by_email(data)

        if not found_user: 
            flash("Invalid Login", "login")
            return False
        
        if not BCRYPT.check_password_hash(found_user.password, data["password"]):
            flash("Invalid Login", "login")
            return False

        return found_user


    @staticmethod
    def validate_new(form):
        is_valid = True

        # check the length of first_name
        if len(form["first_name"]) < 2:
            flash("First name must be atleast 2 characters.", "register")
            is_valid = False

        # check the length of last_name
        if len(form["last_name"]) < 2:
            flash("Last name must be atleast 2 characters.", "register")
            is_valid = False
        
        # check if the email is in a valid format
        if not EMAIL_REGEX.match(form["email"]):
            flash("Email must be a valid email.", "register")
            is_valid = False

        # check if the email already exists in the db
        if User.get_one_by_email(form):
            flash("This email is already registered.", "register")
            is_valid = False


        # check the length of the password
        if len(form["password"]) < 8:
            flash("Password must be atleast 8 characters", "register")
            is_valid = False
        

        # check if password and confirm_password are the same
        if form["password"] != form["confirm_password"]:
            flash("The password confirmation does not match.", "register")
            is_valid = False

        return is_valid