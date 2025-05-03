from flask import jsonify
from sqlalchemy import func
from datetime import datetime
from app import db, Employees, attendance  # Import db and models from app.py
import logging  # Import logging module

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
import logging  # Import logging module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_alert_routes(app):
    @app.route('/alerts/work-anniversary', methods=['GET'])
    def check_work_anniversaries():
        try:
            # Get the current date
            today = datetime.now()

            # Query employees with work anniversaries (matching day and month of HireDate)
            anniversary_employees = db.session.query(Employees).filter(
                func.month(Employees.HireDate) == today.month,
                func.day(Employees.HireDate) == today.day
            ).all()

            # Calculate years worked and convert to a list of dictionaries
            anniversary_data = [
                {
                    'EmployeeID': emp.EmployeeID,
                    'FullName': emp.FullName,
                    'YearsWorked': today.year - emp.HireDate.year
                }
                for emp in anniversary_employees
            ]
            logging.error(f"Error in check_work_anniversaries: {e}")
            return jsonify(anniversary_data), 200

        except Exception as e:
            # Log the error for debugging purposes
            logger.error(f"Error in check_work_anniversaries: {e}")
            return jsonify({'error': 'An error occurred while processing work anniversaries.'}), 500

    @app.route('/alerts/excessive-leave', methods=['GET'])
    def check_excessive_leave():
        try:
            # Query leave days from the attendance table, grouped by EmployeeID
            leave_alerts = db.session.query(
                attendance.EmployeeID,
                Employees.FullName,
                func.sum(attendance.LeavesDay).label('TotalLeave')
            ).join(
                Employees, attendance.EmployeeID == Employees.EmployeeID
            ).group_by(
                attendance.EmployeeID, Employees.FullName
            ).having(
                func.sum(attendance.LeavesDay) > 30  # Leaves exceeding 30 days
            ).all()

            # Convert to a list of dictionaries
            leave_alerts_data = [
                {'EmployeeID': row[0], 'FullName': row[1], 'TotalLeave': row[2]}
                for row in leave_alerts
            ]
            logging.error(f"Error in check_excessive_leave: {e}")
            return jsonify(leave_alerts_data), 200

        except Exception as e:
            # Log the error for debugging purposes
            logger.error(f"Error in check_excessive_leave: {e}")
            return jsonify({'error': 'An error occurred while processing excessive leave alerts.'}), 500