from flask import Flask, request, jsonify
import pyodbc
import pymysql
from pymysql.err import IntegrityError

app = Flask(__name__)

# Kết nối SQL Server (HUMAN_2025)
sql_server_conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PHUONTHARO31;DATABASE=HUMAN;UID=sa;PWD=123456')
sql_cursor = sql_server_conn.cursor()

# Kết nối MySQL (PAYROLL)
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='payroll'
)
mysql_cursor = mysql_conn.cursor()

@app.route('/employees', methods=['GET'])
def get_employees():
    sql_cursor.execute("SELECT * FROM Employees")
    rows = sql_cursor.fetchall()
    employees = [dict(zip([column[0] for column in sql_cursor.description], row)) for row in rows]
    return jsonify(employees)

@app.route('/payroll', methods=['GET'])
def get_payroll():
    mysql_cursor.execute("SELECT * FROM Payroll")
    rows = mysql_cursor.fetchall()
    payroll_data = [dict(zip([desc[0] for desc in mysql_cursor.description], row)) for row in rows]
    return jsonify(payroll_data)

@app.route('/add-employee', methods=['POST'])
def add_employee():
    data = request.get_json()

    required_fields = ['MaNV', 'HoTen', 'PhongBan', 'ChucVu', 'LuongCoBan']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Kiểm tra trùng MaNV
        sql_cursor.execute("SELECT 1 FROM Employees WHERE MaNV = ?", data['MaNV'])
        if sql_cursor.fetchone():
            return jsonify({'error': 'Employee already exists in SQL Server'}), 409

        mysql_cursor.execute("SELECT 1 FROM Employees WHERE MaNV = %s", (data['MaNV'],))
        if mysql_cursor.fetchone():
            return jsonify({'error': 'Employee already exists in MySQL'}), 409

        # Bắt đầu giao dịch
        sql_server_conn.autocommit = False
        mysql_conn.begin()

        # Thêm vào SQL Server
        sql_cursor.execute("""
            INSERT INTO Employees (MaNV, HoTen, PhongBan, ChucVu, LuongCoBan)
            VALUES (?, ?, ?, ?, ?)
        """, data['MaNV'], data['HoTen'], data['PhongBan'], data['ChucVu'], data['LuongCoBan'])
        sql_server_conn.commit()

        # Thêm vào MySQL
        mysql_cursor.execute("""
            INSERT INTO Employees (MaNV, HoTen, PhongBan, ChucVu, LuongCoBan)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['MaNV'], data['HoTen'], data['PhongBan'], data['ChucVu'], data['LuongCoBan']))
        mysql_conn.commit()

        return jsonify({'message': 'Employee added successfully'}), 201

    except Exception as e:
        sql_server_conn.rollback()
        mysql_conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/update-employee', methods=['PUT'])
def update_employee():
    data = request.get_json()
    try:
        sql_cursor.execute("""
            UPDATE Employees SET HoTen=?, PhongBan=?, ChucVu=?, LuongCoBan=?
            WHERE MaNV=?
        """, data['HoTen'], data['PhongBan'], data['ChucVu'], data['LuongCoBan'], data['MaNV'])
        sql_server_conn.commit()

        mysql_cursor.execute("""
            UPDATE Employees SET HoTen=%s, PhongBan=%s, ChucVu=%s, LuongCoBan=%s
            WHERE MaNV=%s
        """, (data['HoTen'], data['PhongBan'], data['ChucVu'], data['LuongCoBan'], data['MaNV']))
        mysql_conn.commit()

        return jsonify({'message': 'Employee updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-employee', methods=['DELETE'])
def delete_employee():
    ma_nv = request.args.get('MaNV')
    try:
        # Kiểm tra ràng buộc trong PAYROLL
        mysql_cursor.execute("SELECT * FROM Payroll WHERE MaNV = %s", (ma_nv,))
        if mysql_cursor.fetchone():
            return jsonify({'error': 'Cannot delete employee with payroll data'}), 400

        # Xóa trong SQL Server
        sql_cursor.execute("DELETE FROM Employees WHERE MaNV = ?", ma_nv)
        sql_server_conn.commit()

        # Xóa trong MySQL
        mysql_cursor.execute("DELETE FROM Employees WHERE MaNV = %s", (ma_nv,))
        mysql_conn.commit()

        return jsonify({'message': 'Employee deleted successfully'}), 200

    except Exception as e:
        sql_server_conn.rollback()
        mysql_conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/attendance', methods=['GET'])
def get_attendance():
    mysql_cursor.execute("SELECT * FROM Attendance")
    rows = mysql_cursor.fetchall()
    attendance = [dict(zip([desc[0] for desc in mysql_cursor.description], row)) for row in rows]
    return jsonify(attendance)

@app.route('/reports', methods=['GET'])
def get_reports():
    # Placeholder - cần viết truy vấn thực tế
    return jsonify({'message': 'HR, payroll, and dividend reports API'})

@app.route('/alerts', methods=['POST'])
def send_alerts():
    data = request.get_json()
    # Giả lập xử lý alert
    return jsonify({'message': 'Alert sent successfully', 'data': data})



if __name__ == '__main__':
    app.run(debug=True)
