import logging
from flask import Blueprint, jsonify, request
from Config.Db import Database
from Cache.FbCache import get_cached_uid_redis
from Model.ReportsModel import ReportsModel

class ReportsController:
    """
     Controller with routes, function calling, error handling, and logging.
    """
    def __init__(self):
        self.blueprint = Blueprint('reports_blueprint', __name__)
        self.db = Database()

        # Logger setup
        logging.basicConfig(
            filename='/var/log/flask_app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Routes
        self.blueprint.add_url_rule('/fetch', view_func=self.get_all_reports, methods=['GET'])
        self.blueprint.add_url_rule('/add', view_func=self.add_report, methods=['POST'])

    def get_all_reports(self):
        """
        Fetch all submitted reports.
        """
        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/all] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/all] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            connection = self.db.connect_read()
            reports_model = ReportsModel(connection)
            result = reports_model.get_all_reports(user_id)
            return jsonify(result), 200
        except Exception as e:
            self.logger.error(f"[/fetch] Error fetching reports: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

    def add_report(self):
        """
        Add a report for the authenticated user.
        """
        try:
            id_token = request.headers.get('Authorization')
            if not id_token:
                self.logger.warning("[/add] Missing Authorization token")
                return jsonify({"error": "Authorization token is missing"}), 401

            user_id = get_cached_uid_redis(id_token)
            if not user_id:
                self.logger.warning("[/add] Invalid or expired token")
                return jsonify({"error": "User ID not found from token"}), 401

            data = request.get_json()
            subject = data.get("subject")
            description = data.get("description")

            if not subject or not description:
                return jsonify({"error": "Subject and description are required"}), 400

            connection = self.db.connect_write()
            reports_model = ReportsModel(connection)
            result = reports_model.add_report(user_id, subject, description)
            return jsonify(result), 201

        except Exception as e:
            self.logger.error(f"[/add] Error creating report: {str(e)}", exc_info=True)
            return jsonify({"error": "An error occurred", "details": str(e)}), 500

# Register controller and blueprint
reports_controller = ReportsController()
reports_blueprint = reports_controller.blueprint