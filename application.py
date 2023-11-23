from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys 

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()


@application.route("/login")
def login():
    return render_template("로그인.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest() 
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('view_list')) 
    else:
        flash("Wrong ID or PW!")
        return render_template("로그인.html")

@application.route("/signup")
def signup():
    return render_template("회원가입.html")


@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return render_template("로그인.html") 
    else:
        flash("user id already exist!")
        return render_template("회원가입.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect("/")

@application.route("/")
def hello():
    return render_template("상품전체조회.html")

@application.route("/list")
def view_list():
    
    data = DB.get_items()
    tot_count = len(data)
    return render_template("상품전체조회.html", datas=data.items(), total=tot_count)

@application.route("/certification")
def view_review():
    return render_template("이화인인증.html")

@application.route("/reg_items")
def reg_item():
    return render_template("상품등록.html")

@application.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")


@application.route("/submit_item", methods=['POST'])
def reg_item_submit():
    name = request.args.get("name")
    seller = request.args.get("seller")
    addr = request.args.get("addr")
    money = request.args.get("money")
    category = request.args.get("category")
    status = request.args.get("status")
    intro = request.args.get("intro")
    
    # print(name, seller, addr, category, status, description)
    #return render_template("reg_item.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))

    name = request.form.get("name")
    seller = request.form.get("seller")
    addr = request.form.get("addr")
    money = request.form.get("money")
    category = request.form.get("category")
    status = request.form.get("status")
    intro = request.form.get("intro")

    # 데이터베이스에 데이터 삽입 로직 수행
    if DB.insert_item(name, {
        'seller': seller,
        'addr': addr,
        'money': money,
        'category': category,
        'status': status,
        'intro': intro
    }, "static/images/{}".format(image_file.filename)):
        flash("상품이 성공적으로 등록되었습니다!")
    else:
        flash("상품 등록에 실패했습니다. 다시 시도해주세요.")

    return render_template(
        "submit_item_result.html",
        data=request.form,
        img_path="static/images/{}".format(image_file.filename)
    )
    # data=request.form
    # return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))
    # 여기서 데이터베이스에 데이터 삽입 로직 수행
    # DB.insert_item(name, seller, addr, money, category, status, intro)
    # return redirect(url_for('view_list'))

@application.route('/signup_page')
def signup_page():
    return render_template('회원가입.html')

if __name__ == "__main__":
    application.run(host='0.0.0.0')