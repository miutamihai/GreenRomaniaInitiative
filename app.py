from flask import Flask, render_template
import cx_Oracle

app = Flask(__name__)

dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCLCDB.localdomain')
conn = cx_Oracle.connect(user='mihai', password='mihai16', dsn=dsn_tns)


@app.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute('select * from MIHAI.ELECTRICITYTBL where ELECTRICITYID = :firstId', firstId=1)
    for row in cursor:
        print(row[0], '-', row[1])
    return render_template('index.html')


@app.route('/clienti')
def customers():
    cursor = conn.cursor()
    cursor.execute('''select CUSTOMERID, CUSTOMERNAME, CUSTOMERADDRESS, CUSTOMERCITY, CUSTOMERCOUNTY, CUSTOMERTYPE
        from CUSTOMERTBL''')
    return render_template('customers.html', data=cursor)


@app.route('/locatii')
def locations():
    cursor = conn.cursor()
    cursor.execute('''select chargerid, chargeraddress, chargercity, chargercounty, producername
        from CHARGERTBL
        inner join ELECTRICITYTBL E on CHARGERTBL.ELECTRICITYID = E.ELECTRICITYID
        order by CHARGERID''')
    return render_template('locations.html', data=cursor)


@app.route('/furnizori')
def suppliers():
    cursor = conn.cursor()
    cursor.execute('select * from MIHAI.ELECTRICITYTBL')
    return render_template('suppliers.html', data=cursor)


if __name__ == '__main__':
    app.run()
