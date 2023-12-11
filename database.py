import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/Authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_user(self, data, pw):
        user_info ={
            "id":data['id'],
            "pw":pw,
            "name":data['name']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info) 
            print(data)
            return True
        else:
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()
            if value['id'] == id_string:
                return False
            return True

    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False

    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['seller'],
            "addr": data['addr'],
            "money": data['money'],
            "category": data['category'],
            "status": data['status'],
            "intro": data['intro'],
            "img_path": img_path
        }
        self.db.child("item").child(name).set(item_info)
        return True

    def get_items(self):
        items = self.db.child("item").get().val()
        return items

    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value = ""
        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()
        return target_value

    def insert_profile(self, prseller, data, img_path):
            profile_info = {
                "prname": data['prname'],
                "printro": data['printro'],
                "img_path": img_path
            }
            self.db.child("profile").child(prseller).set(profile_info)
            return True
    
    def get_profile(self):
        profile = self.db.child("profile").get().val()
        return profile
    
    def get_profile_by_seller(self, prseller):
        # prseller에 해당하는 프로필 정보 가져오기
        profile_info = self.db.child("profile").child(prseller).get().val()
        return profile_info
    
    def get_profile_seller(self, prname):
        prname = self.db.child("prname").get()
        target_value = ""
        for res in  prname.each():
            key_value = res.key()
            if key_value == prname:
                target_value = res.val()
        return target_value


    def reg_review(self, data, img_path):
        review_info = {
            "title" : data['reviewTitle'],
            "id" : data['reviewID'],
            "gender" : data['reviewGender'],
            "age" : data['reviewAge'],
            "rate" : data['reviewStar'],
            "review" : data['reviewContents'],
            "img_path": img_path
        }
        self.db.child("review").child(data['name']).set(review_info)
        return True

    def get_reviews(self):
        reviews = self.db.child("review").get().val()
        return reviews

    def get_review_ratings(self):
        reviews = self.db.child("review").get()
        total_rating = 0
        individual_ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for res in reviews.each():
            value = res.val()
            rating = int(value.get("rate", 0))

            total_rating += rating
            individual_ratings[rating] += 1

        return total_rating, individual_ratings



    def get_review_byname(self, name):
        reviews = self.db.child("review").get()
        target_value = ""
        for res in reviews.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()
        return target_value

    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""
        if hearts.val() == None:
            return target_value

        for res in hearts.each():
            key_value = res.key()

            if key_value == name:
                target_value=res.val()
                
        return target_value


    def update_heart(self, user_id, isHeart, item, money, img_path):
        heart_info ={
            "interested": isHeart,
            "money" : money,
            "img_path": img_path
        }
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True

    def update_certification(self, user_id, check):
        certification_info ={
            "certification": check
        }
        self.db.child("ewha").child(user_id).set(certification_info)
        return True

    def add_to_cart(self, user_id, item, quantity=1):
        cart_ref = self.db.child("carts").child(user_id)
        product_ref = cart_ref.child(item)

        existing_quantity = product_ref.get().val()
        if existing_quantity:
            existing_quantity = existing_quantity.get('quantity', 0)
            quantity += int(existing_quantity)

        self.db.child("carts").child(user_id).child(item).update({"quantity": quantity})
        return True

    def get_cart(self, user_id):
        cart_ref = self.db.child("carts").child(user_id)
        cart = cart_ref.get().val()
        return cart if cart else {}

    def get_items_bycategory(self, cate):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()

            if value['category'] == cate:
                target_value.append(value)
                target_key.append(key_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict

    def get_liked_items(self, user_id):
        liked_items = self.db.child("heart").child(user_id).get().val()
        return liked_items


    def get_items_byseller(self, sel):
        items = self.db.child("item").get()
        target_value=[]
        target_key=[]
        for res in items.each():
            value = res.val()
            key_value = res.key()

            if value['seller'] == sel:
                target_value.append(value)
                target_key.append(key_value)
        new_dict={}
        for k,v in zip(target_key,target_value):
            new_dict[k]=v
        return new_dict
