from flask import Flask, jsonify
import pyodbc
import pymysql
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Kết nối SQL Server (HUMAN_2025)
def get_sql_server_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=PHUONTHARO31;DATABASE=HUMAN;UID=sa;PWD=123456'
    )

# Kết nối MySQL (PAYROLL)
def get_mysql_connection():
    return pymysql.connect(
        host='localhost', user='root', password='123456', database='payroll'
    )

# Route cho báo cáo HR
@app.route('/reports/hr-report', methods=['GET'])
def get_hr_report():
    try:
        with get_sql_server_connection() as sql_server_conn:
            sql_cursor = sql_server_conn.cursor()
            sql_cursor.execute("""
                SELECT PhongBan, COUNT(*) AS TotalEmployees
                FROM Employees
                GROUP BY PhongBan
            """)
            hr_report = sql_cursor.fetchall()
            hr_report_data = [{'PhongBan': row[0], 'TotalEmployees': row[1]} for row in hr_report]
            return jsonify(hr_report_data)

    except Exception as e:
        logger.error(f"Error in get_hr_report: {e}")
        return jsonify({'error': 'An error occurred while generating HR report.'}), 500

# Route cho báo cáo Payroll
@app.route('/reports/payroll-report', methods=['GET'])
def get_payroll_report():
    try:
        with get_mysql_connection() as mysql_conn:
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute("""
                SELECT PhongBan, SUM(LuongCoBan) AS TotalSalary
                FROM Payroll
                GROUP BY PhongBan
            """)
            payroll_report = mysql_cursor.fetchall()
            payroll_report_data = [{'PhongBan': row[0], 'TotalSalary': row[1]} for row in payroll_report]
            return jsonify(payroll_report_data)

    except Exception as e:
        logger.error(f"Error in get_payroll_report: {e}")
        return jsonify({'error': 'An error occurred while generating Payroll report.'}), 500

# Route cho báo cáo Dividend
@app.route('/reports/dividend-report', methods=['GET'])
def get_dividend_report():
    try:
        with get_sql_server_connection() as sql_server_conn:
            sql_cursor = sql_server_conn.cursor()
            sql_cursor.execute("""
                SELECT SUM(DividendAmount) AS TotalDividend, COUNT(*) AS TotalShareholders
                FROM Shareholders
                WHERE IsEmployee = 1
            """)
            dividend_report = sql_cursor.fetchall()
            dividend_report_data = [{'TotalDividend': row[0], 'TotalShareholders': row[1]} for row in dividend_report]
            return jsonify(dividend_report_data)

    except Exception as e:
        logger.error(f"Error in get_dividend_report: {e}")
        return jsonify({'error': 'An error occurred while generating Dividend report.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
