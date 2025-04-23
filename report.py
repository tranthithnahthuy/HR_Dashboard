from flask import Flask, request, jsonify
import pyodbc
import pymysql

app = Flask(__name__)

# Kết nối SQL Server (HUMAN_2025)
sql_server_conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PHUONTHARO31;DATABASE=HUMAN;UID=sa;PWD=123456')
sql_cursor = sql_server_conn.cursor()

# Kết nối MySQL (PAYROLL)
mysql_conn = pymysql.connect(host='localhost', user='root', password='123456', database='payroll')
mysql_cursor = mysql_conn.cursor()

# Route cho báo cáo HR
@app.route('/reports/hr-report', methods=['GET'])
def get_hr_report():
    try:
        sql_cursor.execute("""
            SELECT PhongBan, COUNT(*) AS TotalEmployees
            FROM Employees
            GROUP BY PhongBan
        """)
        hr_report = sql_cursor.fetchall()
        hr_report_data = [{'PhongBan': row[0], 'TotalEmployees': row[1]} for row in hr_report]
        return jsonify(hr_report_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route cho báo cáo Payroll
@app.route('/reports/payroll-report', methods=['GET'])
def get_payroll_report():
    try:
        mysql_cursor.execute("""
            SELECT PhongBan, SUM(LuongCoBan) AS TotalSalary
            FROM Payroll
            GROUP BY PhongBan
        """)
        payroll_report = mysql_cursor.fetchall()
        payroll_report_data = [{'PhongBan': row[0], 'TotalSalary': row[1]} for row in payroll_report]
        return jsonify(payroll_report_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route cho báo cáo Dividend
@app.route('/reports/dividend-report', methods=['GET'])
def get_dividend_report():
    try:
        sql_cursor.execute("""
            SELECT SUM(DividendAmount) AS TotalDividend, COUNT(*) AS TotalShareholders
            FROM Shareholders
            WHERE IsEmployee = 1
        """)
        dividend_report = sql_cursor.fetchall()
        dividend_report_data = [{'TotalDividend': row[0], 'TotalShareholders': row[1]} for row in dividend_report]
        return jsonify(dividend_report_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
