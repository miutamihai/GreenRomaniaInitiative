import pyodbc
from flask import Flask, render_template, request

app = Flask(__name__)

user_data = {
    'Name': '',
    'Password': '',
    'Role': 'Client'
}

conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0};"
    "Server=;"  # aici pui numele laptopului tau 
    "Database=GreenRomaniaInitiative;"
    "Trusted_Connection=yes;"
)


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
                from dbo.CUSTOMERTBL''')
        return render_template('customers.html', data=cursor, user_data=user_data)
    else:
        cursor = conn.cursor()
        client_name = request.form['newClientName']
        client_address = request.form['newClientAddress']
        client_city = request.form['newClientCity']
        client_county = request.form['newClientCounty']
        client_no_of_employees = int(request.form['newClientNoOfEmployees'])
        cursor.execute('exec CreateCustomer ?, ?, ?, ?, ?, ?', (
            client_name, client_address, client_city, client_county, client_no_of_employees, user_data['Name'],
            user_data['Password']))
        conn.commit()
        cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
                    from dbo.CUSTOMERTBL''')
        return render_template('customers.html', user_data=user_data, data=cursor)


@app.route('/locatii', methods=['GET', 'POST'])
def locations():
    if request.method == 'GET':
        cursor = conn.cursor()
        cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
                from dbo.CHARGERTBL
                inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
                order by CHARGERID''')
        return render_template('locations.html', data=cursor, user_data=user_data)
    else:
        cursor = conn.cursor()
        location_address = request.form['newLocationAddress']
        location_city = request.form['newLocationCity']
        location_county = request.form['newLocationCounty']
        location_provider_id = int(request.form['newLocationProviderId'])
        cursor.execute(
            'insert into dbo.CHARGERTBL(chargerid, chargeraddress, chargercity, chargercounty, electricityid) values (?, ?, ?, ?, ?)',
            (location_address, location_city, location_county, location_provider_id))
        conn.commit()
        cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
                        from dbo.CHARGERTBL
                        inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
                        order by CHARGERID''')
        return render_template('locations.html', data=cursor, user_data=user_data)


@app.route('/furnizori', methods=['GET', 'POST'])
def suppliers():
    if request.method == 'GET':
        cursor = conn.cursor()
        cursor.execute('select * from dbo.ELECTRICITYTBL')
        return render_template('suppliers.html', data=cursor, user_data=user_data)
    else:
        cursor = conn.cursor()
        provider_name = request.form['newProviderName']
        provider_price_per_unit = int(request.form['newProviderPricePerUnit'])
        cursor.execute(
            'insert into dbo.ELECTRICITYTBL(ELECTRICITYID, PRODUCERNAME, PRICEPERUNIT) VALUES (?, ?, ?)',
            (provider_name, provider_price_per_unit))
        conn.commit()
        cursor.execute('select * from dbo.ELECTRICITYTBL')
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
        cursor.execute('''select ROLENAME from dbo.USERROLES
            inner join USERS U on USERROLES.ROLEID = U.USERROLEID
            where USERNAME= ? and USERPASSWORD=?''', (username, password))
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
    elif 'client' in request.form:
        client = int(request.form['client'])
        cursor = conn.cursor()
        cursor.execute('''select TRANSACTIONID, CHARGERADDRESS, CHARGERCITY, UNITSSOLD, SALEDATE, VEHICLEREGNO from
                    dbo.CHARGINGDETAILSTBL
                    inner join CHARGERTBL C2 on CHARGINGDETAILSTBL.CHARGERID = C2.CHARGERID
                    inner join VEHICLETBL V on CHARGINGDETAILSTBL.VEHICLEID = V.VEHICLEID
                    where CUSTOMERID = ?''', client)
        res = cursor.fetchall()
        if not res:
            res = None
        return render_template('orders.html', user_data=user_data, data=res, client=client)
    else:
        station_id = int(request.form['stationId'])
        units = int(request.form['units'])
        reg_no = request.form['regNo']
        cursor = conn.cursor()
        cursor.execute('exec InsertOrder ?, ?, ?, ?, ?', (station_id, units, reg_no, user_data['Name'], user_data['Password']))
        conn.commit()
        return render_template('order_success.html')


@app.route('/sterge_client/<string:client_id>')
def delete_client(client_id):
    client_id = int(client_id)
    cursor = conn.cursor()
    cursor.execute('exec DeleteCustomer ?, ?, ?', (client_id, user_data['Name'], user_data['Password']))
    conn.commit()
    cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
            from dbo.CUSTOMERTBL''')
    return render_template('customers.html', user_data=user_data, data=cursor)


@app.route('/sterge_locatie/<string:location_id>')
def delete_location(location_id):
    location_id = int(location_id)
    cursor = conn.cursor()
    cursor.execute('delete from dbo.CHARGERTBL where CHARGERID = ?', location_id)
    conn.commit()
    cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
            from dbo.CHARGERTBL
            inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
            order by CHARGERID''')
    return render_template('locations.html', data=cursor, user_data=user_data)


@app.route('/sterge_furnizor/<string:provider_id>')
def delete_provider(provider_id):
    provider_id = int(provider_id)
    cursor = conn.cursor()
    cursor.execute('delete from dbo.ELECTRICITYTBL where ELECTRICITYID = ?', provider_id)
    conn.commit()
    cursor.execute('select * from dbo.ELECTRICITYTBL')
    return render_template('suppliers.html', data=cursor, user_data=user_data)


if __name__ == '__main__':
    app.run()
