import os

from flask import Flask, render_template, request, redirect, flash

import sqlite3


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "ThisShouldBeRandomOrChanged"
    #app.config.from_mapping(
    #    SECRET_KEY='dev',
    #    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    #)
    
    connection=sqlite3.connect("warehouse.db",check_same_thread=False)


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

 # THESE FUNCTIONS FOR MANIPULATING THE DATABASE
    @app.route('/items', methods=["GET"])
    def get_items():
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM warehouseitems ORDER BY location ASC, description ASC")

        return render_template('items.html',items=rows)

    @app.route('/item/new', methods=["GET"])
    def item_new_get():
        return render_template('newitem.html')

    @app.route('/item/new', methods=["POST"])
    def item_new_post():
        location = request.form.get("location")
        description = request.form.get("description")
        
        try:
           amount = int(request.form.get("amount"))
        except:
           flash("Amount must be an integer")
           return redirect("/item/new")
           
        if amount<1:
           flash("Amount must be at least 1")
           return redirect("/item/new")
                 
        
        cursor = connection.cursor()
        
        sql = '''SELECT Count() FROM warehouseitems WHERE location=? AND description=?'''
        cursor.execute(sql, (location,description))
        numberOfRows = cursor.fetchone()[0]
        
        if numberOfRows != 0:
           flash("Item "+description+" already exists at location "+location)
           return redirect("/items")
        
        sql='''INSERT INTO warehouseitems(location,description,amount) VALUES (?,?,?)'''

        result = cursor.execute(sql, (location,description,amount) )
        connection.commit()
        
        print("database insert result is ",result)
                
        return redirect("/items")



    @app.route('/item/delete/<loc>/<des>', methods=["GET"])
    def delete_item(loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("DELETE FROM warehouseitems WHERE location=? AND description=?", (loc,des))

        return redirect("/items")

    @app.route('/item/increase/<loc>/<des>', methods=["GET"])
    def increase_amount(loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("SELECT amount FROM warehouseitems WHERE location=? AND description=?", (loc,des))
        result = rows.fetchone()
        
        old_amount = result[0]
        print("Result is ",old_amount)
        new_amount = old_amount + 1
        print("New amount is ",new_amount)
        
        sql='''UPDATE warehouseitems SET amount=? WHERE  location=? AND description=?'''
        
        result = cursor.execute(sql, (new_amount, loc, des ))
        connection.commit()       
                
        return redirect("/items")

    @app.route('/item/decrease/<loc>/<des>', methods=["GET"])
    def decrease_amount(loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("SELECT amount FROM warehouseitems WHERE location=? AND description=?", (loc,des))
        result = rows.fetchone()
        
        old_amount = result[0]
        print("Result is ",old_amount)
        
        if old_amount==1:
           flash("Can't reduce the number of item below 1. Use delete instead")
        else:
           new_amount = old_amount - 1
           sql='''UPDATE warehouseitems SET amount=? WHERE  location=? AND description=?'''
           result = cursor.execute(sql, (new_amount, loc, des ))
           connection.commit()       
                
        return redirect("/items")
       
                
        
        

 # THESE FUNCTIONS FOR MANIPULATING THE USERS
    @app.route('/users', methods=["GET"])
    def get_users():
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM users")

        return render_template('users.html',users=rows)
        
    @app.route('/user/new', methods=["GET"])
    def user_new_get():
        return render_template('newuser.html')

    @app.route('/user/new', methods=["POST"])
    def user_new_post():
        username = request.form.get("username")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")
       
        print(username, password, confirmpassword)
        
        cursor = connection.cursor()
        
        sql = '''SELECT Count() FROM users WHERE username=?'''
        cursor.execute(sql, (username,))
        numberOfRows = cursor.fetchone()[0]
        print("number of rows for users is",numberOfRows)
        
        if numberOfRows != 0:
           print("Username already exists")
           flash("User "+username+" already exists")
           print("redirecting")
           return redirect("/user/new")
           
        
        sql='''INSERT INTO users(username,password) VALUES (?,?)'''

        result = cursor.execute(sql, (username,password) )
        connection.commit()
        
        print("database insert result is ",result)
                
        return redirect("/users")
        
# T
    @app.route('/', methods=["GET"])
    def home():


        return render_template('index.html')
        
        

# THESE FUNCTIONS FOR MANIPULATING THE USERS
    @app.route('/picklists', methods=["GET"])
    def get_picklists():
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM picklist ORDER BY picklistnumber ASC, location ASC, description ASC")

        return render_template('picklists.html',picklist=rows)
        
    @app.route('/picklist/<picklistnumber>', methods=["GET"])
    def get_picklist(picklistnumber):
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM picklist WHERE picklistnumber=? ORDER BY picklistnumber ASC, location ASC, description ASC", (picklistnumber))

        return render_template('picklists.html',picklist=rows, picklistnumber=picklistnumber)
        
        
    @app.route('/picklist/new', methods=["GET"])
    def picklist_new_get():
        cursor = connection.cursor()
        users = cursor.execute("SELECT username FROM users")
        
        cursor = connection.cursor()
        items = cursor.execute("SELECT * FROM warehouseitems")
   
   
   
        return render_template('newpicklist.html',users=users, items = items)





    @app.route('/picklist/new', methods=["POST"])
    def picklist_new_post():
        picklistnumber = request.form.get("picklistnumber")
        assignto = request.form.get("assignto")
        warehouseitem = request.form.get("warehouseitem")
        amount = request.form.get("amount")
      
        description = warehouseitem.split(",")[1]
        location = warehouseitem.split(",")[0]
        
        collected = False
        print(picklistnumber, assignto, warehouseitem)
        
        cursor = connection.cursor()
        
        sql='''INSERT INTO picklist(picklistnumber, assignto, location, description, amount, collected) VALUES (?,?,?,?,?,?)'''

        result = cursor.execute(sql, (picklistnumber, assignto, location, description, amount, collected) )
        connection.commit()
        
        print("database insert result is ",result)
                
        return redirect("/picklists")
        
        
    
    @app.route('/picklist/delete/<plist>/<loc>/<des>', methods=["GET"])
    def delete_picklist(plist,loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("DELETE FROM picklist WHERE picklistnumber=? AND location=? AND description=?", (plist,loc,des))

        return redirect("/picklists")
    
    @app.route('/picklist/increase/<plist>/<loc>/<des>', methods=["GET"])
    def increase_amount_picklist(plist,loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("SELECT amount FROM picklist WHERE  picklistnumber=? AND location=? AND description=?", (plist,loc,des))
        result = rows.fetchone()
        
        old_amount = result[0]
        print("Result is ",old_amount)
        new_amount = old_amount + 1
        print("New amount is ",new_amount)
        
        sql='''UPDATE picklist SET amount=? WHERE picklistnumber=? AND location=? AND description=?'''
        
        result = cursor.execute(sql, (new_amount, plist, loc, des ))
        connection.commit()       
                
        return redirect("/picklists")

    @app.route('/picklist/decrease/<plist>/<loc>/<des>', methods=["GET"])
    def decrease_amount_picklist(plist,loc,des):
        cursor = connection.cursor()
        rows = cursor.execute("SELECT amount FROM picklist WHERE picklistnumber=? AND location=? AND description=?", (plist,loc,des))
        result = rows.fetchone()
        
        old_amount = result[0]
        print("Result is ",old_amount)
        new_amount = old_amount - 1
        print("New amount is ",new_amount)
        
        sql='''UPDATE picklist SET amount=? WHERE picklistnumber=? AND location=? AND description=?'''
        
        result = cursor.execute(sql, (new_amount, plist, loc, des ))
        connection.commit()
        
        return redirect("/picklists")  
    
    return app
