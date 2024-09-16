import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import render_template, Flask, redirect, url_for, request, send_file
from flask_dance.contrib.github import make_github_blueprint, github
import random
import time
from datetime import datetime
from termcolor import cprint

from py_tools import *

db = DbActions(env_to_var("DB_URL"))
app = Flask(__name__)
app.secret_key = env_to_var("APP_SECRET")

github_blueprint = make_github_blueprint(client_id=env_to_var("GITHUB_CLIENT_ID"),
                                         client_secret=env_to_var("GITHUB_CLIENT_SECRET"))

app.register_blueprint(github_blueprint, url_prefix="/login")

ai = groq()

@app.route("/")
def home():
    global username
        
    if not github.authorized:
        return render_template("index.html", db=db, username=None)
    try:
        db.read("app_user", "username", github.get("/user").json()["login"])
    except:
        return render_template("location.html")
    else:
        account_info = github.get("/user")
        username = account_info.json()["login"]
        if account_info.ok:
            
            try:
                if len(db.read("posts", "location", db.read("app_user", "username", account_info.json()["login"])[0][2])) == 0:
                    return render_template("location.html")
            except:
                return render_template("location.html")

            
            return render_template("index.html", random=random, db=db, username=account_info.json()["login"])
    return "request failed"

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/posts/<int:id>")
def posts(id):
    posts = db.read("posts", "location", "EdisonNJ")
    
    db.increment_post(id)
    
    for post in posts:
        if post[0] == id:
            
            solutions_prompt=f"""
                What is a potential solution to this problem?
                {post[1]} {post[2]}
            """
            
            all_posts = db.read_table("posts")
            
            
            news_prompt = f"""
                What are 3 posts that is related to this post include only the title separated by commas example: title1, title2, title3? Include nothing else except for those 3 titles. This is the post that i need to find related articles for: {post[1]} {post[2]}. Here are all the articles {all_posts}
            """
            
            solutions = ai.send_message(solutions_prompt)
            time.sleep(0.5)
            news_link = ai.send_message(news_prompt)
            
            news_link = news_link.replace("\n", "")
            news_link = news_link.split(", ")
            ids =[]
            for link in news_link:
                id = db.read("posts", "title", link)
                try:
                    ids.append([id[0][0], id[0][1]])
                except:
                    continue
            #db.read("posts", "title", "Edison police cracking down on car thefts amid stateside rise in incidents")
            return render_template("post.html", post=post, solutions=solutions, links=ids)
    
    return render_template("404.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.form['location']

    global reddits
    
    reddits = reddit(data)
    
    account_info = github.get("/user")
    username = account_info.json()["login"]

    
    if len(db.read("app_user", "location", data)) == 0:
        db.append([username, data])
        
        reddits.filter()

    return redirect(url_for("home"))

@app.route("/analytics")
def analytics():
    
    try:
        reddits.graph()
    except:
        reddits = reddit(db.read("app_user", "username", username)[0][2])
        reddits.graph()
    
    
    file = reddits.find_newest_file("static/graphs/")
    
    return render_template("analytics.html", file=file, db=db, topics=db.view_post())

@app.route("/petition", methods=["POST", "GET"])
def petition():
    if request.method == "POST":       
        data = request.form["id"]   
        data = db.read("posts", "id", data)[0]
        
        return render_template("petition.html", data=data)
    else:
        try:
            location = db.read("app_user", "username", username)[0][2]
        except:
            return render_template("error.html", error="You are not authorized to view this page")
        return render_template("view_petitions.html", db=db, location=location, random=random)

@app.route("/petition/create", methods=["POST"])
def create_petition():
    
    info = [ "id", "title", "location", "desc"]
    data = []
    for i in info:
        try:
            data.append(request.form[i])
        except:
            continue
    
    time_now = round(datetime.now().timestamp())
    
    for row in db.read_table("petitions"):
        if row[1] == data[1]:
            return render_template("error.html", error="Petition already exists")

    if len(data) == 4:
        db.append([data[1], int(data[0]), data[3], data[2], time_now])
    else:
        db.append([data[1], int(data[0]), "", data[2], time_now])

    return render_template("success.html", data=data)

@app.route("/petition/<int:id>")
def view_petition(id):
    data = db.read("petitions", "alternate_id", id)[0]
    try:
        location = db.read("app_user", "username", username)[0][2]
    except:
        return render_template("error.html", error="You are not authorized to view this page")
    
    return render_template("view_petition.html", data=data, location=location)

@app.route("/petition/sign/<int:id>", methods=["POST"])
def sign_petition(id):
    data = db.read("petitions", "alternate_id", id)[0]
    
    try:
        username
    except:
        return render_template("error.html", error="You are not authorized to view this page")
    
    check = True
    if check:
        for row in db.read("signatures", "petition_id", data[1]):
            if row[2] == username:
                
                signatures = []
                for row in db.read_table("signatures"):
                    if row[1] == data[1]:
                        signatures.append(row[2])
                
                signatures = [signatures[i:i+2] for i in range(0, len(signatures), 2)]

                path = generate(signatures, data[2])
                
                return render_template("pdf.html", db=db, signatures=signatures, path=path)
        
    db.append([data[1], username])
    
    signatures = []
    for row in db.read_table("signatures"):
        if row[1] == data[1]:
            signatures.append(row[2])
    
    signatures = [signatures[i:i+2] for i in range(0, len(signatures), 2)]

    path = generate(signatures, data[2])
        
    return render_template("pdf.html", db=db, signatures=signatures, path=path)

@app.route("/download", methods=["POST"])
def download():
    
    #cprint(f"DOWNLOAD PATH: {request.form["path"]}", "red")
    
    return send_file(request.form["path"], as_attachment=True)

if __name__ == "__main__":
    
    app.run(debug=True)