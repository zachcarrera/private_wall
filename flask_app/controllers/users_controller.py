from flask import render_template, redirect, request, session, flash
from flask_app import app

from flask_app.models.users_model import User
from flask_app.models.messages_model import Message

# route to show login and registration forms
@app.route("/")
def index():
    return render_template("index.html")


# form submission for registration
@app.route("/register", methods=["POST"])
def register():

    # if the form data does not pass validation, redirect to "/"
    if not User.validate_new(request.form):
        return redirect("/")

    session["user_id"] = User.create(request.form)
    return redirect("/dashboard")


# from submission for login
@app.route("/login", methods=["POST"])
def login_user():
    print(request.form)

    # validate the login requeset and save the result
    logged_in_user = User.validate_login(request.form)

    # if the user is not logged in then redirect to "/"
    if not logged_in_user:
        return redirect("/")
    
    # if the login was successful then save the user's id in session
    session["user_id"] = logged_in_user.id
    return redirect("/dashboard")


# route to logout user
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



# route to show the dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("You must be logged in to see this page.", "secure")
        return redirect("/")

    messages = Message.get_all_for_id({"id":session["user_id"]})
    user = User.get_one_by_id({"id": session["user_id"]})
    other_users = User.get_other_users({"id": session["user_id"]})


    return render_template("dashboard.html", messages=messages, user=user, other_users=other_users)


@app.route("/send_message", methods=["POST"])
def new_message():
    print(request.form)

    if not Message.validate(request.form):
        return redirect("/dashboard")

    Message.new_message(request.form)
    return redirect("/dashboard")


@app.route("/delete/<int:message_id>")
def delete_message(message_id):
    print("deleting message", message_id)


    Message.delete({"id": message_id})
    return redirect("/dashboard")