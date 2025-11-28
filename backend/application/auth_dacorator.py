from functools import wraps
from flask import request, jsonify
import jwt
import os

SECRET_KEY = os.environ.get('secret','This_is_my_secret')

def token_required(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        auth_header = request.headers.get('Authrization')

        if not auth_header:
            return jsonify({'message': 'Token is missing'}),401
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    return decorator

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.user_role != required_role:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
