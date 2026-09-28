import mysql.connector
class EcommerceApp:
    #constructor
    def __init__(self):
        self.current_user=None #stores:{'id':int,'name':str,'role':str}
    def run(self):
      while True:
        if not self.current_user: 
            print("\n=================================")
      
            print("\nECOMMERCE SYSYTEM")
            print("=========================================-")
            print ("1.BROWSE CATALOG")
            print ("2. LOGIN ")
            print("3.REGISTER")
            print ("4.EXIT")
            choice =input("select an option (1-4): ").strip()
            if choice=='1':
                self.view_products()
            elif choice=='2':
                self.login()
            elif choice=='3':
                self.Register()
        else:
           # print("current user: {self.current_user}")
            print (f"\n----Logged in as :{self.current_user['name']} [{self.current_user['role'].upper()} ]")
            print ("1.Browse Catalog ")
            print ("2.Add Item to Cart ")
            print ("3.View Cart ")
            print ("4.Checkout")
            print ("5.Order History")
            if self.current_user['role']=='admin':
                print("6.[Admin] Add new product")
                print("7.[Admin] View All Customer Orders")
            print("0.LOGOUT")

            choice =input("select an option:").strip()    #strip used to clean extra space
            if choice=='1':
                self.view_products()
            elif choice=='2':
                self.add_to_cart()
            elif choice=='3':
                self.view_cart()
            elif choice=='4':
                self.checkout()
            elif choice=='5':
                self.view_order_histroy()
            elif choice=='0':
                self.logout()
            elif choice=='6':
                self.admin_add_product()
    def get_db(self):
        conn=mysql.connector.connect(
                                            host="localhost",
                                            user="root",
                                            password="KW2005",
                                            database="ecommerce_db"
                                        )  
        return conn                           


#---------------CATALOG & CART--------------------  
    def view_products(self):
        print("/n"+ "="*70)
        print (f"{'ID':<5}{'PRODUCT NAME':<30} {'Category':<15}{'PRICE (INR)':<12}{'STOCK':<8}")
        print("="*70)
        conn=mysql.connector.connect(
            host="localhost",
            user="root",
            password="KW2005",
            database=" ecommerce_db"
        )   
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * from product ORDER BY id ASC")
        products=cursor.fetchall()
        cursor.close()
        conn.close()

        if not products:
            print ("catalog is empty") 
            return
        for p in products:
            print (f"{p['id']:<5}{p['name']:<30} {p['category']:<15} {float(p['price']):<11.2f} {p['stock']:<8}")
        print("="*70)    

#================AUTHENTICATION==============================
    def Register(self):
        print("\n------Register new user----")
        name=input("Enter full name: ").strip()
        email=input("Enter Email: ").strip()
        pwd=input("enter password : ").strip().lower()

        if not name or not email or not pwd :
            print("[!] all field are required.")
            return

        conn=mysql.connector.connect(host="localhost",
                                     user="root",
                                     password="KW2005",
                                     database="ecommerce_db"
                                     )
        cursor=conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM users WHERE email=%s",(email,))
            if cursor.fetchone():
                print("[!] Email is already registered. please login .")
                return
            cursor.execute(
               "INSERT INTO users(name ,email,password_hash) VALUES (%s,%s,%s)",
                (name,email,pwd)
            )
            conn.commit()
            print("[+] Registration successful ! you can now login.")
        except mysql.connector.Error  as err:
            print(f"[!]DATABASE ERROR:{err}")
        finally:
            cursor.close()
            conn.close()
    #==========LOGIN======================     
    def login(self):
        print("\n-----------LOGIN---------")
        email=input("Email: ").strip()
        pwd=input("enter password: ").strip().lower()

        conn=mysql.connector.connect(
            host="localhost",
            user="root",
            password="KW2005",
            database="ecommerce_db"
        )  
        cursor=conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
            user=cursor.fetchone()
            if user and user['password_hash'] == pwd:
                self.current_user={
                    "id":user['id'],
                    "name":user['name'],
                    "role":user['role']
                }
                print (f"\n[+] welcome back ,{user['name']}! (Role:{user['role']})")
            else:
                print ("[!]INVALID EMAIL AND PASSWORD.")
        finally:
            cursor.close()
            conn.close() 
     ##########################################       
    def add_to_cart(self):
        self.view_products()
        try:
            prod_id=int(input("\nEnter Product ID to add:")) 
            qty=int(input("enter Quantity:"))
            if qty <= 0:
                print("[!]Quantity must be at least 1.")
                return
        except ValueError:
            print("[!] Invalid input. Numbers only.")
            return

        conn=mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="KW2005",
                    database="ecommerce_db"
                )  
        cursor=conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT stock From product WHERE id=%s",(prod_id ,))
            product=cursor.fetchone() #this product is variable 
            if not product:
                print("[!] Product not found")
                return 
            if product['stock']<qty:
                print(f"[!] Insufficient stock .Only {product['stock']}available.")
                return

            cursor.execute("""
            INSERT INTO cart_items(user_id,product_id,quanity)
            VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE quanity=quanity + %s
            """,(self.current_user['id'],prod_id,qty,qty))

            conn.commit()
            print("[+] Item added to cart successfully.")
        finally:
            cursor.close()
            conn.close()    
                   
############################################    
    def view_cart(self):
        conn=mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="KW2005",
                            database="ecommerce_db"
                        )  
        cursor=conn.cursor(dictionary=True)
        cursor.execute("""
          SELECT ci.product_id, p.name, p.price, ci.quanity,(p.price * ci.quanity)as subtotal
          FROM cart_items ci
          JOIN product p ON ci.product_id=p.id
          WHERE ci.user_id=%s
        """,(self.current_user['id'],))
        items=cursor.fetchall()
        cursor.close()
        conn.close()

        print("\n"+ "-"*65)
        print(f"{'PID':<6}{'PRODUCT NAME':<30}{'PRICE':<10}{'QTY':<6}{'SUBTOTAL':<10}")
        print("-"*65)
        if not items:
            print("your cart is empty.")
            print("-"*65)
            return False
        total=0
        for item in items:
            total += float(item['price']) * item['quanity']
            print(f"{item['product_id']:<6}{item['name']:<30} Rs{float(item['price']):<9.2f}{item['quanity']:<6}RS{float(item['subtotal']):<9.2f} ")
        print("-"*65)
        print(f"Total Cart Value: Rs{total:.2f}")
        print("-"*65)
        return True
    ##################################################
    #========================ORDERS AND CHECKOUT======================
    def checkout(self):
        if not self.view_cart():
            return
        confirm= input("\nProceed to checkout? (y/n):").strip()
        if confirm != 'y':
            print("Checkout canceled")
            return
        address =input("ENTER DELIVERY ADDRESS:").strip()
        if not address:
            print("[!]Delivery address cannot be empty.")
            return
        conn=mysql.connector.connect(
                                    host="localhost",
                                    user="root",
                                    password="KW2005",
                                    database="ecommerce_db"
                                )  
        cursor=conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            cursor.execute("""
               SELECT ci.product_id, ci.quantity, p.price, p.stock
               FROM cart_items ci
               JOIN product p ON ci.product_id=p.id
               WHERE ci.user_id =%s FOR UPDATE
            """,(self.current_user['id'],))
            items= cursor.fetchall()

            if not items:
               conn.rollback()
               print("[!]Cart is empty.")
               return    
            total_amount=0
            for item in items:
               if item['stock']< item['quantity']:
                conn.rollback
                print(f"[!] Checkout Failed:item ID {item['product_id']} has insufficient stock.")
                return
               total_amount += float(item['price']) * item['quantity']  
            cursor.execute(
               "INSRT INTO orders(user_id, total_amount , delivery_address)VALUES (%s,%s,%s)",
               (self.current_user['id'],total_amount,address)
            )      
            order_id=cursor.lastrowid
            for item in items:
              cursor.execute(
                "INSERT INTO order_items(order_id, product_id, quantity,price)VALUES(%s,%s,%s,%s)",
                (order_id ,item['product_id'],item['quantity'],item['price'] )
              )
              cursor.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (item['quantity'], item['product_id'])
              )
                

            # Clear cart
            cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (self.current_user['id'],))

            conn.commit()
            print(f"\n[+] Order #{order_id} placed successfully! Total Paid: ₹{total_amount:.2f}")

        except Exception as e:
           conn.rollback()
           print(f"[!] Order processing error: {e}")
        finally:
           cursor.close()
           conn.close()

##############################################################3
    def view_order_histroy(self):
       conn=mysql.connector.connect(
                                        host="localhost",
                                        user="root",
                                        password="KW2005",
                                        database="ecommerce_db"
                                    )  
       cursor=conn.cursor(dictionary=True)
       cursor.execute(""" SELECT o.id ,o.total_amount,o.status,o.created_at,
        GROUP_CONCAT(CONCAT(p.name,'(x',oi.quantity, ')')SEPARATOR ', ')as items FROM orders o 
        JOIN order_items oi ON o.id=oi.order_id
         JOIN products p ON oi.product_id=p.id
         WHERE o.user_id=%s
         GROUP BY o.id
          ORDER BY o.created_at DESC """,(self.current_user['id'],))
       orders=cursor.fetchall()
       cursor.close()
       conn.close()

       print("\n-------Your Order Histroy------")
       if not orders:
         print("No previous orders found ")
         return
       for o in orders:
         print(f"\nOrder Id:#{o['id']}  |  Date:{o['created_at']}  | Status: {o['status']}")
         print(f"Items:{o['items']}")
         print(f"Total amount: Rs{float(o['total_amount']):.2f}")
         print("-"*50)
 ################################################################################
    def admin_add_product(self) :
        if self.current_user.get('role') != 'admin':
            print("[!]Unauthorized access")
            return
        print("\n--------Add New Product-------------")
        name=input("product Name : ").strip()
        category=input("category: ").strip()
        try:
            price=float(input("Price (INR): "))
            stock=int(input("Stock Quantity: "))
        except ValueError:
            print("[!]Invalid numeric values for price or stock.")
            return
        conn=mysql.connector.connect(
                                            host="localhost",
                                            user="root",
                                            password="KW2005",
                                            database="ecommerce_db"
                                        )  
        cursor=conn.cursor()  
        cursor.execute("INSERT INTO products (name , category, price ,stock)VALUES (%s,%s,%s,%s)",
                       (name,category,price,stock))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[+] Product '{name}' added Successfully") 
    def logout(self):
        self.current_user=None
        print("[+]LOgged Out successfully. ")    

   
            
##################################################3
ecom=EcommerceApp()
ecom.run()                
