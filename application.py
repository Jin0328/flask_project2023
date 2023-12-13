from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask import jsonify
from database import DBhandler
import hashlib
import sys
import math
import random

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
        return redirect(url_for('hello'))
    else:
        flash("Wrong ID or PW!")
        return redirect(url_for('login'))

@application.route("/signup")
def signup():
    return render_template("회원가입.html")


@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return redirect(url_for('login'))
    else:
        flash("user id already exist!")
        return render_template("회원가입.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('main_page'))

@application.route("/")
def hello():
    return redirect(url_for('main_page'))

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    per_page = 6
    per_row = 3
    row_count = int(per_page/per_row)
    start_idx = per_page*page
    end_idx = per_page*(page+1)
    if category=="all":
        data = DB.get_items()
        print(data)
    else:
        data = DB.get_items_bycategory(category)
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False))
    item_counts = len(data)

    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
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
        "상품전체조회.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int(math.ceil(item_counts/per_page)),
        total=item_counts,
        category=category)


@application.route('/main_page')
def main_page():
    return render_template('main_first.html')
    
@application.route("/agreement")
def agreement():
    return render_template("이용약관.html")

@application.route('/review')
def review_page():
    return render_template('리뷰작성.html')


correct_answers = {
    "소방 안전교육 3번째 영상의 제목은 무엇인가요?": "3.소화기 점검 및 사용법",
    "안전교육 2번째 영상의 제목은 무엇인가요?": "직장 안전점검 체크리스트",
    "장애인식개선 교육을 실시하는 주체는 어디인가요?": "장애학생지원센터",
    "장애인식개선 교육의 시작일은? 5월 00일(숫자만)": "22"
}

@application.route("/certification", methods=['GET', 'POST'])
def view_certification():
    questions = [
        "소방 안전교육 3번째 영상의 제목은 무엇인가요?",
        "안전교육 2번째 영상의 제목은 무엇인가요?",
        "장애인식개선 교육을 실시하는 주체는 어디인가요?",
        "장애인식개선 교육의 시작일은? 5월 00일(숫자만)"
    ]

    if request.method == 'POST':
        # 사용자가 제출한 답변과 현재 랜덤으로 선택된 질문에 대한 정답을 가져옵니다.
        current_question = session.pop('current_question', None)
        print(current_question)
        user_answer = request.form.get('answer')
        print(user_answer)
        correct_answer = correct_answers.get(current_question)
        print(correct_answer)
        # 정답과 사용자가 입력한 답변을 비교합니다.
        if user_answer == correct_answer:
            # 정답이 맞으면 인증 성공 페이지로 리다이렉트합니다.
            my_check = DB.update_certification(session['id'],'Y')
            flash("인증 완료!")
            return redirect(url_for('my_page'))
        else:
            flash("정답이 틀렸습니다. 다시 시도해주세요.")
            return redirect(url_for('view_certification'))
    
    random_question = random.choice(questions)
    session['current_question'] = random_question
    return render_template("이화인인증.html", random_question=random_question)


@application.route("/badge")
def badge():
    return render_template("배지안내.html")


@application.route("/reg_items")
def reg_item():
    user_id = session.get('id')  # 로그인한 사용자의 ID

    if user_id:
        return render_template("상품등록.html", user_id=user_id)
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))
        

@application.route("/reg_profile")
def reg_profile():
    user_id = session.get('id')  # 로그인한 사용자의 ID

    if user_id:
        return render_template("프로필편집.html", user_id=user_id)
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))
    
@application.route("/submit_profile_post", methods=['POST'])
def reg_profile_submit_post():

    user_id = session.get('id')  # 로그인한 사용자의 ID

    if user_id:
        image_file = request.files["file"]
        image_file.save("static/images/{}".format(image_file.filename))

        prname = request.form.get("prname")
        prseller = user_id
        printro = request.form.get("printro")

        # 데이터베이스에 데이터 삽입 로직 수행
        if DB.insert_profile(prseller, {
        'prname': prname,
        'printro': printro
        }, "static/images/{}".format(image_file.filename)):
            print("데이터:", request.form)
            print("이미지 경로:", "static/images/{}".format(image_file.filename))
            return render_template(
                "마켓찜.html",
                prseller=prseller,
                prname=prname,
                printro=printro,
                img_path="static/images/{}".format(image_file.filename)
            )
        else:
            flash("상품 등록에 실패했습니다. 다시 시도해주세요.")

    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))


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
    total_rating, individual_ratings = DB.get_review_ratings()
    return render_template(
        "리뷰_전체조회.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int((item_counts/per_page)+1), 
        total=item_counts,
        total_rating=total_rating,
        individual_ratings=individual_ratings)


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
    data = DB.get_reviews()
    item_counts = len(data)
    item_counts = len(data)
    per_page = 6
    page_count = int((item_counts / per_page) + 1)
    return redirect(url_for('view_review'))


# @application.route("/submit_item", methods=['POST'])
# def reg_item_submit():
#     name = request.args.get("name")
#     seller = request.args.get("seller")
#     addr = request.args.get("addr")
#     money = request.args.get("money")
#     category = request.args.get("category")
#     status = request.args.get("status")
#     intro = request.args.get("intro")


@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():

    user_id = session.get('id')  # 로그인한 사용자의 ID

    if user_id:
        image_file = request.files["file"]
        image_file.save("static/images/{}".format(image_file.filename))

        name = request.form.get("name")
        seller = user_id
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
            print("성공")
        else:
            flash("상품 등록에 실패했습니다. 다시 시도해주세요.")

        return redirect(url_for('view_item_detail', name=name))
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))


@application.route("/buy_now/<name>", methods=['GET'])
def buy_now(name):
    user_id = session.get('id')  # 로그인한 사용자의 ID
    if user_id:
        data = DB.get_item_byname(str(name))
        return render_template("상품주문.html", name=name, data=data)
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))

@application.route("/get_liked/<user_id>", methods=['GET'])
def get_liked(user_id):
    liked_items = DB.get_liked_items(user_id)
    sel_item = DB.get_items_byseller(user_id)
    filtered_items = {item: info for item, info in liked_items.items() if info.get('interested') == 'Y'}
    data= DB.get_profile_by_seller(user_id)
    return render_template('마이페이지(상품찜 보기).html', seller_item=sel_item, liked_items=filtered_items, data=data)


@application.route('/signup_page')
def signup_page():
    return render_template('회원가입.html')

@application.route('/my_page')
def my_page():
    user_id = session.get('id')  # 로그인한 사용자의 ID
    if user_id:
        return redirect(url_for('my_page_user', user_id=user_id))
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))


@application.route('/my_page/<user_id>')
def my_page_user(user_id):
    sel_item = DB.get_items_byseller(user_id)
    data= DB.get_profile_by_seller(user_id)
    return render_template('마이페이지(마켓찜 보기).html', seller_item=sel_item, user_id=user_id, data=data)



# @application.route("/get_liked", methods=['GET'])
# def get_liked():
#     user_id = session.get('id')  # 로그인한 사용자의 ID
#     if user_id:
#         liked_items = DB.get_liked_items(user_id)
#         filtered_items = {item: info for item, info in liked_items.items() if info.get('interested') == 'Y'}
#         return render_template('마이페이지(상품찜 보기).html', liked_items=filtered_items)
#     else:
#         # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
#         flash("로그인이 필요합니다")
#         return redirect(url_for('login'))


@application.route("/view_detail/<name>/")
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
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
    item_info = DB.get_item_byname(name)
    money = item_info.get('money', '0')  # 가격
    img_path = item_info.get('img_path', '/default/image.jpg')
    my_heart = DB.update_heart(session['id'],'Y',name, money, img_path)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    item_info = DB.get_item_byname(name)
    money = item_info.get('money', '0')  # 가격
    img_path = item_info.get('img_path', '/default/image.jpg')
    my_heart = DB.update_heart(session['id'],'N',name, money, img_path)
    return jsonify({'msg': '안좋아요 완료!'})

@application.route("/add_to_cart/<name>", methods=['GET'])
def add_to_cart(name):
    user_id = session.get('id')  # 로그인한 사용자의 ID
    print(user_id)
    if user_id:
        DB.add_to_cart(user_id, name)  # 사용자의 장바구니에 상품 추가
        return redirect(url_for('view_cart'))
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))



@application.route("/cart")
def view_cart():
    # 현재 로그인한 사용자의 장바구니 조회 (가정: user_id는 세션에 저장되어 있다고 가정)
    user_id = session.get('id')  # 로그인한 사용자의 ID
    if user_id:
        cart_items = DB.get_cart(user_id)  # 사용자의 장바구니 정보 가져오기
        # 장바구니 화면에 cart_items 전달하여 렌더링
        return render_template("cart.html", cart_items=cart_items, user_id=user_id)
    else:
        # 로그인되지 않은 경우 로그인 페이지로 이동 또는 메시지 표시
        flash("로그인이 필요합니다")
        return redirect(url_for('login'))


if __name__ == "__main__":
    application.run(host='0.0.0.0')
