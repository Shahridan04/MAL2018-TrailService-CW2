import pyodbc
import requests  # <--- NEW: Required to talk to External Auth API
from flask import Flask, jsonify, request, make_response
from flask_restx import Api, Resource, fields
import decimal
import datetime
from functools import wraps

# --- 1. CONFIGURATION ---------------------------------------------------------
# UPDATE THESE TO MATCH YOUR DOCKER/LOCAL SQL SERVER
DB_SERVER = 'localhost' 
DB_NAME = 'MAL2017 Trail Database' 
DB_USER = 'SA'
DB_PASS = 'C0mp2001!'

# AUTH API URL (From Assessment Brief)
AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

CONNECTION_STRING = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={DB_SERVER};'
    f'DATABASE={DB_NAME};'
    f'UID={DB_USER};'
    f'PWD={DB_PASS};'
    f'TrustServerCertificate=yes;'
)
# ------------------------------------------------------------------------------

# --- 2. FLASK-RESTX SETUP WITH AUTH -------------------------------------------
app = Flask(__name__)

# This enables the "Authorize" button in Swagger
authorizations = {
    'basicAuth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    app, 
    version='1.0', 
    title='TrailService API',
    description='Micro-service for Trail Application (Assessment 2)',
    doc='/swagger',
    authorizations=authorizations, # <--- Enable Auth UI
    security='basicAuth'           # <--- Apply Auth globally (can be overridden)
)

ns = api.namespace('trails', description='Trail CRUD operations')

# --- DATA MODEL ---
trail_model = api.model('Trail', {
    'TrailName': fields.String(required=True, description='Name of the trail'),
    'Length': fields.Float(required=True, description='Length in km'),
    'ElevationGain': fields.Integer(required=False, description='Elevation gain in meters'),
    'RouteType': fields.String(required=True, description='Loop, Out & Back, or Point to Point'),
    'Difficulty': fields.String(required=True, description='Easy, Moderate, Hard'),
    'Duration': fields.Integer(required=False, description='Estimated duration in minutes'),
    'Description': fields.String(required=False, description='Detailed description'),
    'OwnerID': fields.Integer(required=True, description='ID of the User who owns this trail')
})
# ------------------------------------------------------------------------------

# --- 3. AUTHENTICATION HELPER -------------------------------------------------
def check_auth(email, password):
    """
    Verifies credentials against the External University API.
    """
    credentials = {
        "email": email,
        "password": password
    }
    
    try:
        # We try to 'login' to the external system
        response = requests.post(AUTH_API_URL, json=credentials, timeout=5)
        
        # If the external API returns 200 OK, the user is valid (Verified, True)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Auth Error: {e}")
        return False

def login_required(f):
    """
    Decorator to protect routes. 
    1. Checks if Authorization header exists.
    2. Decodes Email/Pass.
    3. Calls check_auth().
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return {'message': 'Authentication required!'}, 401
        
        if not check_auth(auth.username, auth.password):
            return {'message': 'Invalid Credentials (Email/Password).'}, 403
            
        return f(*args, **kwargs)
    return decorated
# ------------------------------------------------------------------------------

# --- 4. DATABASE UTILITY FUNCTION ---------------------------------------------
def db_execute(sql_query, params=None, fetch=False):
    """
    Executes SQL query with AUTOCOMMIT enabled.
    """
    conn = None
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        conn.autocommit = True # <--- CRITICAL FIX: Ensure data saves immediately
        cursor = conn.cursor()
        
        if params:
            cursor.execute(sql_query, params)
        else:
            cursor.execute(sql_query)
        
        if fetch:
            columns = [column[0] for column in cursor.description]
            data = []
            
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                sanitized_dict = {}
                
                # Fix data types that JSON cannot handle natively
                for key, value in row_dict.items():
                    if isinstance(value, decimal.Decimal):
                        sanitized_dict[key] = float(value)
                    elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                        sanitized_dict[key] = value.isoformat()
                    else:
                        sanitized_dict[key] = value
                        
                data.append(sanitized_dict)
            return data
        else:
            return True 
            
    except pyodbc.Error as ex:
        # Return error details for debugging
        return {"error": True, "details": str(ex)}
        
    finally:
        if conn:
            conn.close()

# --- 5. API ENDPOINTS ---------------------------------------------------------

@ns.route('/')
class TrailList(Resource):
    
    # GET is PUBLIC (No @login_required)
    @ns.doc('get_all_trails', security=None) 
    def get(self):
        """
        Get all trails. Calls CW2.sp_GetAllTrails (Public)
        """
        procedure_call = "EXEC CW2.sp_GetAllTrails" 
        data = db_execute(procedure_call, fetch=True)
        
        if isinstance(data, dict) and data.get("error"):
            return {'message': 'Database error', 'details': data["details"]}, 500
            
        return data, 200

    # POST is PROTECTED
    @ns.doc('create_trail', security='basicAuth')
    @login_required # <--- Forces Login
    @ns.expect(trail_model)
    def post(self):
        """
        Create a new trail. Calls CW2.sp_CreateTrail (Admin Only)
        """
        data = request.json
        
        sql = """
            SET NOCOUNT ON;
            DECLARE @NewID INT;
            EXEC CW2.sp_CreateTrail ?, ?, ?, ?, ?, ?, ?, ?;
        """
        
        params = (
            data.get('TrailName'), 
            data.get('Length'), 
            data.get('ElevationGain'), 
            data.get('RouteType'), 
            data.get('Difficulty'), 
            data.get('Duration'), 
            data.get('Description'),
            data.get('OwnerID')
        )

        result = db_execute(sql, params, fetch=False)
        
        if isinstance(result, dict) and result.get("error"):
            return {'message': 'Failed to create trail.', 'details': result["details"]}, 500
        
        return {'message': 'Trail created successfully.'}, 201


@ns.route('/<int:id>')
@ns.param('id', 'The Trail ID')
class Trail(Resource):
    
    # GET Single Trail is PUBLIC
    @ns.doc('get_trail_by_id', security=None)
    def get(self, id):
        """
        Get single trail. Calls CW2.sp_GetTrailByID (Public)
        """
        sql = "EXEC CW2.sp_GetTrailByID ?" 
        data = db_execute(sql, (id,), fetch=True)
        
        if isinstance(data, dict) and data.get("error"):
            return {'message': 'Database error', 'details': data["details"]}, 500
            
        if not data:
            return {'message': f"Trail ID {id} not found."}, 404
            
        return data[0], 200

    # PUT is PROTECTED
    @ns.doc('update_trail', security='basicAuth')
    @login_required # <--- Forces Login
    @ns.expect(trail_model)
    def put(self, id):
        """
        Update trail. Calls CW2.sp_UpdateTrail (Admin Only)
        """
        data = request.json
        
        sql = "EXEC CW2.sp_UpdateTrail ?, ?, ?, ?, ?, ?, ?, ?" 
        
        params = (
            id, 
            data.get('TrailName'), 
            data.get('Length'), 
            data.get('ElevationGain'), 
            data.get('RouteType'), 
            data.get('Difficulty'), 
            data.get('Duration'), 
            data.get('Description')
        )

        result = db_execute(sql, params, fetch=False)
        
        if isinstance(result, dict) and result.get("error"):
            return {'message': f"Failed to update Trail ID {id}.", 'details': result["details"]}, 500
        
        return {'message': f"Trail ID {id} updated successfully."}, 200

    # DELETE is PROTECTED
    @ns.doc('delete_trail', security='basicAuth')
    @login_required # <--- Forces Login
    def delete(self, id):
        """
        Delete trail. Calls CW2.sp_DeleteTrail (Admin Only)
        """
        sql = "EXEC CW2.sp_DeleteTrail ?"
        
        result = db_execute(sql, (id,), fetch=False)

        if isinstance(result, dict) and result.get("error"):
            return {'message': f"Failed to delete Trail ID {id}.", 'details': result["details"]}, 500
            
        return {'message': f"Trail ID {id} deleted successfully."}, 200


# --- 5. RUN APP ---------------------------------------------------------------
if __name__ == '__main__':
    # Using port 8000 is often safer on Docker/Localhost to avoid conflicts
    app.run(host='0.0.0.0', port=8000, debug=True)