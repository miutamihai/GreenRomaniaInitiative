from flask import Flask, render_template, request
import cx_Oracle

app = Flask(__name__)

user_role = 'Client'
username = ''

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCLCDB.localdomain')
conn = cx_Oracle.connect(user='mihai', password='mihai16', dsn=dsn_tns)


@app.route('/')
def index():
    return render_template('index.html', user_role=user_role, username=username)


@app.route('/logout/')
def logout():
    global username
    global user_role
    username = ''
    user_role = 'Client'
    return render_template('index.html', username=username, user_role=user_role)


@app.route('/clienti')
def customers():
    cursor = conn.cursor()
    cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
        from CUSTOMERTBL''')
    return render_template('customers.html', data=cursor, user_role=user_role, username=username)


@app.route('/locatii')
def locations():
    cursor = conn.cursor()
    cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
        from CHARGERTBL
        inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
        order by CHARGERID''')
    return render_template('locations.html', data=cursor, user_role=user_role, username=username)


@app.route('/furnizori')
def suppliers():
    cursor = conn.cursor()
    cursor.execute('select * from MIHAI.ELECTRICITYTBL')
    return render_template('suppliers.html', data=cursor, user_role=user_role, username=username)


@app.route('/autentificare', methods=['GET', 'POST'])
def login():
    global user_role
    if request.method == 'GET':
        return render_template('login.html', user_role=user_role)
    else:
        cursor = conn.cursor()
        global username
        username = request.form['username']
        password = request.form['password']
        cursor.execute('''select ROLENAME from USERROLES
            inner join USERS U on USERROLES.ROLEID = U.USERROLEID
            where USERNAME= :userName and USERPASSWORD=:userPassword''', userName=username, userPassword=password)
        res = cursor.fetchone()
        if res is None:
            username = ''
            return render_template('login_fail.html')
        else:
            user_role = res[0]
            return render_template('index.html', user_role=user_role, username=username)


@app.route('/comenzi', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        return render_template('orders.html', user_role=user_role, data='')
    else:
        client = int(request.form['client'])
        cursor = conn.cursor()
        cursor.execute('''select TRANSACTIONID, CHARGERADDRESS, CHARGERCITY, UNITSSOLD, SALEDATE, VEHICLEREGNO from
            CHARGINGDETAILSTBL
            inner join CHARGERTBL C2 on CHARGINGDETAILSTBL.CHARGERID = C2.CHARGERID
            inner join VEHICLETBL V on CHARGINGDETAILSTBL.VEHICLEID = V.VEHICLEID
            where CUSTOMERID = :clientId''', clientId=client)
        print(cursor.fetchone())
        return render_template('orders.html', user_role=user_role, data=cursor, client=client)


if __name__ == '__main__':
    app.run()
