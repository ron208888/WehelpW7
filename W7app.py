import json
from flask import jsonify
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from flask import Response
import mysql.connector
from mysql.connector import Error

connection = mysql.connector.connect(
     host = "localhost",
     database = "W6member",
     user = "root",
     passwd = "12345678",
     charset = "utf8mb3"
)

app = Flask(
    __name__,
)
app.secret_key = "test"

@app.route("/", methods = ["GET","POST"])
def index():
    return render_template("W6.html")

@app.route("/signup", methods = ["POST"])
def signup():
    Rname = request.form["Rname"]
    account = request.form["account"]
    passwords = request.form["passwords"]
    cursor = connection.cursor()
    command = "insert into member(name, account, password) values(%s, %s, %s);"
    # setId = "ALTER TABLE member AUTO_INCREMENT = 1;"
    
    try:
        # cursor.execute(setId)
        cursor.execute(command, (Rname, account, passwords))
        connection.commit()
        print("更新成功")
        # messagebox.showinfo("註冊成功",f"歡迎{account}加入!")
        return redirect("http://127.0.0.1:3000/")

    except Error as ex:
        print(ex)
        if Rname == "" or account == "" or passwords == "":
            message = "請輸入完整資料"
            return redirect(url_for("error", message = message))
        else:
            message="帳號已被註冊"
            return redirect(url_for("error", message = message))

@app.route("/signin", methods = ["POST"])
def signin():
    name = request.form["name"]
    password = request.form["password"]
    passwd = (f"{password}",)
    session["username"] = name
    cursor = connection.cursor()
    matchAccount = "Select password from member where account = %s"
    userNum = "select id from member where account = %s"
    
    try:
        cursor.execute(matchAccount, (name,))
        result = cursor.fetchall()
        print(result)
        
        if result[0] == passwd:
            cursor.execute(userNum, (name,))
            userId = cursor.fetchall()
            print(userId[0][0])
            session["userID"] = userId[0][0]
            session.permanent = True
            return redirect("http://127.0.0.1:3000/member")
        
        elif result[0] == () or result[0] != passwd:
            message = "帳號、或密碼輸入錯誤"
            return redirect(url_for("error", message = message))
            
    except Error as ex:
        print(ex)
        message = "請輸入帳號密碼"
        return redirect(url_for("error", message = message))


@app.route("/member")
def member():
    name = session["username"]
    return render_template("member.html",name=name)

@app.route("/error")
def error():
    message = request.args.get("message")
    return render_template("error.html", errortype = message)
    
@app.route("/signout")
def signout():
    session.permanent = False
    return redirect("http://127.0.0.1:3000/")

@app.route("/message")
def message():
    message = request.args.get("message")
    name = session["username"]
    userID = session["userID"]
    cursor = connection.cursor()
    writeMessage = "insert into message(id, account, message)values(%s, %s, %s)"
    
    try:
        cursor.execute(writeMessage, (userID, name, message))
        print(message)
        connection.commit()
        return redirect("http://127.0.0.1:3000/member")
    
    except Error as ex:
        print(ex)
        message = "請輸入留言"
        return redirect(url_for("error", message = message))
    
@app.route("/api/member", methods = ["GET","PATCH"])
def api_member():
    data = {"data":""}
    username = request.args.get("username")
    cursor = connection.cursor()
    search = "select id, name, account from member where account = %s"
    changeName = "update member set name = %s where account = %s"
    
    if request.method == "PATCH":
        change = eval(request.get_data().decode("utf-8"))
        originName = session["username"]
        newName = change["name"]
        success = {"ok":True}
        fail = {"error":True}
        
        try:
            cursor.execute(changeName, (newName, originName))
            return jsonify(success)
          
        except Error as ex:
            print(ex)
            return jsonify(fail)

    try:
        cursor.execute(search, (username, ))
        result = cursor.fetchall()
     
        if result == []:
            data["data"] = None
            return jsonify(data)
        else:
            column = [index[0] for index in cursor.description]
            data_dict = [dict(zip(column, row)) for row in result]
            data["data"] = data_dict[0]
            return jsonify(data)
    
     except Error as ex:
         print(ex)

app.run(port = 3000)
