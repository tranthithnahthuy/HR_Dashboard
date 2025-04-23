from functools import wraps
from flask import request, jsonify

# Giả lập một bộ phân quyền (có thể thay thế bằng cơ sở dữ liệu thực tế)
USER_ROLES = {
    'admin': ['admin'],
    'hr_manager': ['hr_manager', 'admin'],
    'payroll_manager': ['payroll_manager', 'admin'],
    'employee': ['employee']
}

# Định nghĩa decorator kiểm tra quyền truy cập
def requires_role(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_role = request.headers.get('Role')  # Giả lập lấy vai trò người dùng từ header
            if user_role not in USER_ROLES.get(role, []):
                return jsonify({'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
