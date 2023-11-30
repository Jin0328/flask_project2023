from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask import jsonify
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
    return redirect(url_for('view_list'))

@application.route("/")
def hello():
    return redirect(url_for('view_list'))

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3
    row_count = int(per_page/per_row)
    start_idx = per_page*page
    end_idx = per_page*(page+1)
    data = DB.get_items()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):
        if (i == row_count-1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())
            [i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())
            [i*per_row:(i+1)*per_row])
    return render_template(
        "상품전체조회.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)


@application.route('/main_page')
def main_page():
    return render_template('main_first.html')


@application.route('/review')
def review_page():
    return render_template('리뷰작성.html')


@application.route("/certification")
def view_certification():
    return render_template("이화인인증.html")


@application.route("/badge")
def badge():
    return render_template("배지안내.html")


@application.route("/reg_items")
def reg_item():
    return render_template("상품등록.html")

@application.route("/view_review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3
    row_count = int(per_page/per_row)
    start_idx = per_page*page
    end_idx = per_page*(page+1)
    data = DB.get_reviews()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())
                                                 [i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())
                                                 [i*per_row:(i+1)*per_row])
    return render_template(
        "리뷰_전체조회.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1),
        total=item_counts)


# @application.route("/reviews")
# def get_reviews():
#     reviews = DB.get_reviews()
#     return render_template("reviews.html", reviews=reviews)


@application.route("/reg_review_init/<name>/", methods=['GET', 'POST'])
def reg_review_init(name):
    return render_template("리뷰작성.html", name=name)
                                                                        
@application.route("/reg_review", methods=['POST'])
def reg_review():
    try:
        image_file = request.files["chooseFile"]
        image_path = "static/images/{}".format(image_file.filename)
        print("이미지 경로:", image_path)

        image_file.save("static/images/{}".format(image_file.filename))
        data = request.form
        print("Review data:", data)
        DB.reg_review(data, image_path)
    except Exception as e:
        print("Error:", str(e))
        return str(e)

    return render_template("리뷰_전체조회.html")



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
        print()
    else:
        flash("상품 등록에 실패했습니다. 다시 시도해주세요.")

    return render_template(
        "상품세부.html",
        data=request.form,
        img_path="static/images/{}".format(image_file.filename)
    )


@application.route('/signup_page')
def signup_page():
    return render_template('회원가입.html')

@application.route('/my_page')
def my_page():
    return render_template('마이페이지(마켓찜 보기).html')

@application.route('/my_page2')
def my_page2():
    return render_template('마이페이지(상품찜 보기).html')

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:", name)
    data = DB.get_item_byname(str(name))
    print("####data:", data)
    return render_template("상품세부.html", name=name, data=data)


@application.route('/view_review_detail/<name>')
def view_review_detail(name):
    data = DB.get_review_byname(str(name))
    return render_template("리뷰상세.html", name=name, data=data)


@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '안좋아요 완료!'})

if __name__ == "__main__":
    application.run(host='0.0.0.0')
