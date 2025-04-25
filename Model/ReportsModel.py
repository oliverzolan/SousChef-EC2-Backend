import logging
from datetime import datetime


class ReportsModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_reports(self, user_id):
        """
        Fetch all reports for a specific user.
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, user_id, subject, description, date
                    FROM Reports
                    WHERE user_id = %s
                    ORDER BY date DESC
                    """,
                    (user_id,)
                )
                reports = cursor.fetchall()

            logging.info(f"Fetched {len(reports)} reports for user_id {user_id}")
            return reports

        except Exception as e:
            logging.error(f"Error fetching reports for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while fetching reports", "details": str(e)}


    def add_report(self, user_id, subject, description):
        """
        Add a new report
        """
        try:
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Reports (user_id, subject, description, date)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, subject, description, current_date)
                )
            self.db.commit()
            logging.info(f"Report added for user_id {user_id}")
            return {"message": "Report added successfully"}
        except Exception as e:
            logging.error(f"Error adding report for user_id {user_id}: {str(e)}", exc_info=True)
            return {"error": "An error occurred while adding the report", "details": str(e)}