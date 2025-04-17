from flask import jsonify
import pyodbc
import pymysql

# Kết nối SQL Server (HUMAN_2025)
sql_server_conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PHUONTHARO31;DATABASE=HUMAN;UID=sa;PWD=123456')
sql_cursor = sql_server_conn.cursor()

# Kết nối MySQL (PAYROLL)
mysql_conn = pymysql.connect(host='localhost', user='root', password='123456', database='payroll')
mysql_cursor = mysql_conn.cursor()

def setup_alert_routes(app):
    @app.route('/alerts/work-anniversary', methods=['GET'])
    def check_work_anniversaries():
        try:
            # Truy vấn những nhân viên sắp tới kỷ niệm làm việc (1, 5, 10 năm)
            sql_cursor.execute("""
                SELECT MaNV, HoTen, YEAR(GETDATE()) - YEAR(NgayBatDau) AS YearsWorked
                FROM Employees
                WHERE MONTH(NgayBatDau) = MONTH(GETDATE()) AND DAY(NgayBatDau) = DAY(GETDATE())
            """)
            anniversary_employees = sql_cursor.fetchall()
            anniversary_data = [{'MaNV': row[0], 'HoTen': row[1], 'YearsWorked': row[2]} for row in anniversary_employees]
            return jsonify(anniversary_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/alerts/excessive-leave', methods=['GET'])
    def check_excessive_leave():
        try:
            # Truy vấn những nhân viên có số ngày nghỉ phép vượt quá mức cho phép
            mysql_cursor.execute("""
                SELECT MaNV, HoTen, SUM(DaysOff) AS TotalLeave
                FROM Attendance
                WHERE DaysOff > 0
                GROUP BY MaNV, HoTen
                HAVING SUM(DaysOff) > 30  -- Ví dụ: nghỉ phép vượt quá 30 ngày
            """)
            leave_alerts = mysql_cursor.fetchall()
            leave_alerts_data = [{'MaNV': row[0], 'HoTen': row[1], 'TotalLeave': row[2]} for row in leave_alerts]
            return jsonify(leave_alerts_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
