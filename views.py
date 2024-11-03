from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
import sqlite3
from .auth import query

views = Blueprint('views', __name__)
conn = sqlite3.connect("database.db")

def fetch(query, *args):
  with sqlite3.connect("database.db") as conn:
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def convert(list):
  string = ""
  for x in list:
    string += "" + x
  return string

def data_function(sql, data):
      with sqlite3.connect("database.db") as conn:  
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return 

@views.route('/')
@login_required
def home():
  # checking authority of user
  a_email = current_user.email
  auth = query("""SELECT authority FROM userinfo where email=?""", (a_email,))

  if auth[0][0] == "Employee":
    flash("Insufficient Authority!", category='Error')
    return redirect(url_for('views.employee_view'))
  
  else:
    # statistics
    revenue = fetch('SELECT SUM(unitPrice * stockSold) FROM sellingProduct')
    costs = fetch('SELECT SUM(unitCost * stockBought) FROM buyingProduct')
    profit = fetch('''SELECT SUM(unitPrice * stockSold) - SUM(unitCost * stockBought)
    FROM sellingProduct
    INNER JOIN buyingProduct 
    ON sellingProduct.productID=buyingProduct.productID;''')
   
    #display of products
    high = query('''SELECT name
    FROM sellingProduct
    ORDER BY (unitPrice * stockSold) DESC
    LIMIT 5
    ''')
    highest = [h[0] for h in high]
    low = query('''SELECT name
    FROM sellingProduct
    ORDER BY (unitPrice * stockSold) ASC
    LIMIT 5
    ''')
    lowest = [i[0] for i in low]
    return render_template("home.html", revenue="{:.2f}".format(revenue[0]), costs="{:.2f}".format(costs[0]), profit="{:.2f}".format(profit[0]), 
                          a1=highest[0], b1=highest[1], c1=highest[2], d1=highest[3], e1=highest[4], a2=lowest[0], b2=lowest[1], c2=lowest[2], d2=lowest[3], e2=lowest[4], user=current_user)

@views.route('/product-retail', methods=['GET', 'POST'])
@login_required
def retail():
  # checking authority of user
  a_email = current_user.email
  auth = query("""SELECT authority FROM userinfo where email=?""", (a_email,))

  if auth[0][0] == "Employee":
    flash("Insufficient Authority!", category='Error')
    return redirect(url_for('views.employee_view'))
  
  else:
    if request.method == 'POST':
      # getting data for add via form
      name = request.form.get('name')
      numberInStock = request.form.get('numberInStock')
      unitPrice = request.form.get('unitPrice')
      stockSold = request.form.get('stockSold')
      add = (name, numberInStock, unitPrice, stockSold)
      
      #getting data for update via form
      u_name = request.form.get('u_name')
      u_numberInStock = request.form.get('u_numberInStock')
      u_unitPrice = request.form.get('u_unitPrice')
      u_stockSold = request.form.get('u_stockSold')  
      check = query("""SELECT name FROM sellingProduct where name=?""", (u_name,))
      update = (u_numberInStock, u_unitPrice, u_stockSold, u_name,)

      #getting data for delete via form 
      d_name = request.form.get('d_name')
      delete = (d_name)
      d_check = query("""SELECT name FROM sellingProduct where name=?""", (d_name,))

      #adding data into database
      if add[0] != None:
        if add[1] and add[2] and add[3]:
          data_function("""INSERT INTO sellingProduct(name, numberInStock, unitPrice, stockSold) VALUES (?, ?, ?, ?)""", add)
          flash('Product Added!', category='Success')
          return redirect(url_for('views.retail'))
        else:
          flash('Please Fill All Required Fields!', category='Error')
      
      #updating data in database
      elif update[3] != None:
        if len(check) != 0:
          if len(update[0]) != 0:
            data_function("""UPDATE sellingProduct SET numberInstock=? WHERE name=?""", (u_numberInStock, u_name,))
          if len(update[1]) != 0:
            data_function("""UPDATE sellingProduct SET unitPrice=? WHERE name=?""", (u_unitPrice, u_name,))
          if len(update[2]) != 0:
            data_function("""UPDATE sellingProduct SET stockSold=? WHERE name=?""", (u_stockSold, u_name,))
          flash('Product updated!')
          return redirect(url_for('views.retail'))
        else:
          flash('Please Enter Correct Name!', category='Error')
      

      #deleting data from database
      elif delete[0] != None:
        if len(d_check) != 0:
          print(d_name)
          data_function("""DELETE FROM sellingProduct WHERE name=?""", (d_name,))
          flash('Product Deleted!', category='Error')
          return redirect(url_for('views.retail'))
        else:
          flash('Product does not exist!', category='Error')  
      
    #retrieving data for table
    data = query('''SELECT *
                FROM sellingProduct
                ORDER BY productID ASC''')
    #recommendations
    r = query('''SELECT name
                FROM sellingProduct
                ORDER BY numberInStock ASC
                LIMIT 3''')
    recommend = [i[0] for i in r]
    return render_template("retail.html", a=recommend[0], b=recommend[1], c=recommend[2], data=data, user=current_user)

@views.route('/product-purchases', methods=['GET', 'POST'])
@login_required
def purchases():
  # checking authority of user
  a_email = current_user.email
  auth = query("""SELECT authority FROM userinfo where email=?""", (a_email,))
  print(auth[0][0])

  if auth[0][0] == "Employee":
    flash("Insufficient Authority!", category='Error')
    return redirect(url_for('views.employee_view'))
  
  else:
    if request.method == 'POST':
      # getting data for add via form
      name = request.form.get('name')
      supplier = request.form.get('supplier')
      unitCost = request.form.get('unitCost')
      stockBought = request.form.get('stockBought')
      add = (supplier, unitCost, stockBought)
      print(name)
      id = query("SELECT productID FROM sellingProduct WHERE name=?", (name,))
    
      #getting data for update via form
      u_name = request.form.get('u_name')
      u_supplier = request.form.get('u_supplier')
      u_unitCost = request.form.get('u_unitCost')
      u_stockBought = request.form.get('u_stockBought')  
      u_check = query("SELECT name FROM sellingProduct where name=?", (u_name,))
      update = (u_supplier, u_unitCost, u_stockBought, u_name,)
    
      #getting data for delete via form 
      d_name = request.form.get('d_name')
      delete = (d_name,)
      d_check = query("""SELECT name FROM sellingProduct where name=?""", (d_name,))

      #adding data into database
      if add[0] and add[1] and add[2] != None:
        print(id)
        print(query("SELECT name FROM sellingProduct WHERE productID=?", (7,)))
        if len(id):
          print(id)
          id_check = query("""SELECT productID FROM buyingProduct WHERE productID=?""", (id[0][0],))
          if len(id_check) == 0:
            data_function("""INSERT INTO buyingProduct(productID, supplier, unitCost, stockBought) VALUES (?, ?, ?, ?)""", (id[0][0], supplier, unitCost, stockBought))
            flash('Product Added!', category='Success')
            return redirect(url_for('views.purchases'))
          else:
            flash('Product information already exists!', category='Error')
        else:
          flash('Product must exist in retail or incorrect product name', category='Error')
      
      #updating data in database
      elif update[3] != None:
        if len(u_check) != 0:
          id = query("""SELECT productID from sellingProduct where name=?""", (u_name,))
          if len(update[0]) != 0:
            data_function("""UPDATE buyingProduct SET supplier=? WHERE productID=?""", (u_supplier, id[0][0],))
          if len(update[1]) != 0:
            data_function("""UPDATE buyingProduct SET unitCost=? WHERE productID=?""", (u_unitCost, id[0][0],))
          if len(update[2]) != 0:
            data_function("""UPDATE buyingProduct SET stockBought=? WHERE ProductID=?""", (u_stockBought, id[0][0],))
          flash('Product updated!')
          return redirect(url_for('views.purchases'))
        else:
          flash('Please Enter Correct Name!', category='Error')
      

      #deleting data from database
      elif delete[0] != None:
        if len(d_check) != 0:
          id = query("""SELECT productID from sellingProduct where name=?""", (d_name,))
          data_function("""DELETE FROM buyingProduct WHERE productID=?""", (id[0][0],))
          flash('Product Deleted!', category='Error')
          return redirect(url_for('views.purchases'))
        else:
          flash('Product does not exist!', category='Error')

    #table data
    data = query('''SELECT buyingProduct.productID, name, supplier, unitCost, stockBought
                  FROM buyingProduct
                  INNER JOIN sellingProduct
                  ON buyingProduct.productID=sellingProduct.productID
                  ORDER BY buyingProduct.productID ASC''')
    
    #highest costing products
    r = query('''SELECT name
                FROM buyingProduct
                INNER JOIN sellingProduct
                ON buyingProduct.productID=sellingProduct.productID
                ORDER BY (unitCost * stockBought) DESC
                LIMIT 3''')
    recommend = [i[0] for i in r]
    return render_template("purchases.html", a=recommend[0], b=recommend[1], c=recommend[2], data=data, user=current_user)

@views.route('/employee-record', methods=['GET', 'POST'])
@login_required
def record():
  # checking authority of user
  a_email = current_user.email
  auth = query("""SELECT authority FROM userinfo where email=?""", (a_email,))
  print(auth[0][0])

  if auth[0][0] == "Employee":
    return redirect(url_for('views.employee_view'))
  
  else:
    if request.method == 'POST':
      #getting data for update via form
      u_forename = request.form.get('u_forename')
      u_surname = request.form.get('u_surname')
      u_email = request.form.get('u_email')
      u_authority = request.form.get('u_authority')  
      update = (u_forename, u_surname, u_email, u_authority,)

      #getting data for delete via form 
      d_email = request.form.get('d_email')
      delete = (d_email,)

      #updating data in database
      if update[2] != None:
        id = query("""SELECT userID from userinfo where email=?""", (u_email,))
        if len(id) != 0:
          if len(update[0]) != 0:
            data_function("""UPDATE userinfo SET forename=? WHERE userID=?""", (u_forename, id[0][0],))
          if len(update[1]) != 0:
            data_function("""UPDATE userinfo SET surname=? WHERE userID=?""", (u_surname, id[0][0],))
          if len(update[2]) != 0:
            data_function("""UPDATE userinfo SET email=? WHERE userID=?""", (u_email, id[0][0],))
          if len(update[3]) != 0:
            data_function("""UPDATE userinfo SET authority=? WHERE userID=?""", (u_authority, id[0][0],)) 
          flash('User updated!')
          return redirect(url_for('views.record'))
        else:
          flash('Please Enter Correct Email!', category='Error')
      

      #deleting data from database
      elif delete[0] != None:
        id = query("""SELECT userID from userinfo where email=?""", (d_email,))
        if len(id) != 0:
          data_function("""DELETE FROM userinfo WHERE userID=?""", (id[0][0],))
          flash('User Deleted!', category='Error')
          return redirect(url_for('views.record'))
        else:
          flash('Please Enter Correct Email!', category='Error')

    #table data
    data = query('''SELECT forename, surname, email, authority
                FROM userInfo
                ORDER BY userID ASC''')
    return render_template("record.html", data=data, user=current_user)

@views.route('/employee-view')
@login_required
def employee_view():
  data = query('''SELECT forename, surname, email, authority
                FROM userInfo
                ORDER BY userID ASC''')
  return render_template("user_record.html", data=data, user=current_user)