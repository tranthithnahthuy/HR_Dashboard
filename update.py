import pyodbc  # Dùng cho SQL Server
import mysql.connector  # Dùng cho MySQL

# Kết nối đến HUMAN_2025 (SQL Server)
conn_hr = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_sqlserver_host;"
    "DATABASE=HUMAN_2025;UID=your_user;PWD=your_password"
)
cursor_hr = conn_hr.cursor()

# Kết nối đến PAYROLL (MySQL)
conn_payroll = mysql.connector.connect(
    host="your_mysql_host",
    user="your_user",
    password="your_password",
    database="PAYROLL"
)
cursor_payroll = conn_payroll.cursor()

def update_employee(employee_id, new_department, new_position, new_status):
    try:
        # --- Cập nhật SQL Server ---
        cursor_hr.execute("""
            UPDATE Employees
            SET Department = ?, Position = ?, WorkStatus = ?
            WHERE EmployeeID = ?
        """, (new_department, new_position, new_status, employee_id))
        conn_hr.commit()

        # --- Cập nhật MySQL (nếu có liên quan đến lương) ---
        cursor_payroll.execute("""
            UPDATE EmployeePayroll
            SET Department = %s, Position = %s
            WHERE EmployeeID = %s
        """, (new_department, new_position, employee_id))
        conn_payroll.commit()

        print("Employee updated successfully in both systems.")
    except Exception as e:
        print("Error updating employee:", e)
        conn_hr.rollback()
        conn_payroll.rollback()

# Ví dụ sử dụng:
update_employee(employee_id=101, new_department="Sales", new_position="Manager", new_status="Active")

# Đóng kết nối
cursor_hr.close()
conn_hr.close()
cursor_payroll.close()
conn_payroll.close()
