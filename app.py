import cx_Oracle
from flask import Flask, render_template, request

app = Flask(__name__)

user_data = {
    'Name': '',
    'Password': '',
    'Role': 'Client'
}

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCLCDB.localdomain')
conn = cx_Oracle.connect(user='mihai', password='mihai16', dsn=dsn_tns)


@app.route('/')
def index():
    return render_template('index.html', user_data=user_data)


@app.route('/logout/')
def logout():
    global user_data
    user_data['Name'] = ''
    user_data['Role'] = 'Client'
    return render_template('index.html', user_data=user_data)


@app.route('/clienti', methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        cursor = conn.cursor()
        cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
                from CUSTOMERTBL''')
        return render_template('customers.html', data=cursor, user_data=user_data)
    else:
        cursor = conn.cursor()
        cursor.execute('''select num_rows from all_tables where table_name = 'CUSTOMERTBL' ''')
        client_id = int(cursor.fetchone()[0]) + 1
        client_name = request.form['newClientName']
        client_address = request.form['newClientAddress']
        client_city = request.form['newClientCity']
        client_county = request.form['newClientCounty']
        client_no_of_employees = int(request.form['newClientNoOfEmployees'])
        cursor.callproc('CreateCustomer', parameters=[client_id, client_name, client_address, client_city, client_county, client_no_of_employees, user_data['Name'], user_data['Password']])
        conn.commit()
        cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
                    from CUSTOMERTBL''')
        return render_template('customers.html', user_data=user_data, data=cursor)


@app.route('/locatii')
def locations():
    cursor = conn.cursor()
    cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
        from CHARGERTBL
        inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
        order by CHARGERID''')
    return render_template('locations.html', data=cursor, user_data=user_data)


@app.route('/furnizori')
def suppliers():
    cursor = conn.cursor()
    cursor.execute('select * from MIHAI.ELECTRICITYTBL')
    return render_template('suppliers.html', data=cursor, user_data=user_data)


@app.route('/autentificare', methods=['GET', 'POST'])
def login():
    global user_data
    if request.method == 'GET':
        return render_template('login.html', user_data=user_data)
    else:
        cursor = conn.cursor()
        username = request.form['username']
        password = request.form['password']
        cursor.execute('''select ROLENAME from USERROLES
            inner join USERS U on USERROLES.ROLEID = U.USERROLEID
            where USERNAME= :userName and USERPASSWORD=:userPassword''', userName=username, userPassword=password)
        res = cursor.fetchone()
        if res is None:
            return render_template('login_fail.html')
        else:
            user_data['Name'] = username
            user_data['Password'] = password
            user_data['Role'] = res[0]
            return render_template('index.html', user_data=user_data)


@app.route('/comenzi', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        return render_template('orders.html', user_data=user_data, data='')
    else:
        client = int(request.form['client'])
        cursor = conn.cursor()
        cursor.execute('''select TRANSACTIONID, CHARGERADDRESS, CHARGERCITY, UNITSSOLD, SALEDATE, VEHICLEREGNO from
            CHARGINGDETAILSTBL
            inner join CHARGERTBL C2 on CHARGINGDETAILSTBL.CHARGERID = C2.CHARGERID
            inner join VEHICLETBL V on CHARGINGDETAILSTBL.VEHICLEID = V.VEHICLEID
            where CUSTOMERID = :clientId''', clientId=client)
        if cursor.fetchone() is None:
            cursor = None
        return render_template('orders.html', user_data=user_data, data=cursor, client=client)


@app.route('/sterge_client/<string:client_id>')
def delete_client(client_id):
    client_id = int(client_id)
    cursor = conn.cursor()
    cursor.callproc('DeleteCustomer', parameters=[client_id, user_data['Name'], user_data['Password']])
    conn.commit()
    cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
            from CUSTOMERTBL''')
    return render_template('customers.html', user_data=user_data, data=cursor)


if __name__ == '__main__':
    app.run()
