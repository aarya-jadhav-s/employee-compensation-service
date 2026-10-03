import os
import json
import pyodbc
import azure.functions as func

app = func.FunctionApp()


def get_connection():
    connection_string = os.environ["SQL_CONNECTION_STRING"]

    if "DRIVER=" not in connection_string.upper():
        connection_string = "DRIVER={SQL Server};" + connection_string

    return pyodbc.connect(connection_string)

# 1. Create a new employee. The bonus is optional and may be left unset.

@app.route(route="employees", methods=["POST"])
def create_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = json.loads(req.get_body().decode("utf-8"))

        first_name = data.get("FirstName")
        last_name = data.get("LastName")
        department_id = data.get("DepartmentID")
        salary = data.get("Salary")
        bonus = data.get("Bonus")
        hire_date = data.get("HireDate")

        if not first_name or not last_name or department_id is None or salary is None:
            return func.HttpResponse(
                "FirstName, LastName, DepartmentID and Salary are required.",
                status_code=400
            )

        conn = get_connection()
        print("Connected to EmployeeCompensationDB")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Employee
                (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
            OUTPUT INSERTED.EmployeeID
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            first_name,
            last_name,
            department_id,
            salary,
            bonus,
            hire_date
        )

        employee_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            f"Employee created successfully with EmployeeID: {employee_id}",
            status_code=201
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error creating employee: {str(e)}",
            status_code=500
        )
        
        
# 2. Retrieve a single employee by their ID.
@app.route(route="employees/{employee_id}", methods=["GET"])
def get_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = req.route_params.get("employee_id")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                EmployeeID,
                FirstName,
                LastName,
                DepartmentID,
                Salary,
                Bonus,
                HireDate
            FROM Employee
            WHERE EmployeeID = ?
            """,
            employee_id
        )

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        employee = {
            "EmployeeID": row.EmployeeID,
            "FirstName": row.FirstName,
            "LastName": row.LastName,
            "DepartmentID": row.DepartmentID,
            "Salary": float(row.Salary),
            "Bonus": float(row.Bonus) if row.Bonus is not None else None,
            "HireDate": str(row.HireDate) if row.HireDate is not None else None
        }

        return func.HttpResponse(
            json.dumps(employee),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error retrieving employee: {str(e)}",
            status_code=500
        )
        
# 3. Retrieve a list of employees, with optional filtering by department.

@app.route(route="employees", methods=["GET"])
def get_employees(req: func.HttpRequest) -> func.HttpResponse:
    try:
        department_id = req.params.get("departmentId")

        conn = get_connection()
        cursor = conn.cursor()

        if department_id:
            cursor.execute(
                """
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    DepartmentID,
                    Salary,
                    Bonus,
                    HireDate
                FROM Employee
                WHERE DepartmentID = ?
                """,
                department_id
            )
        else:
            cursor.execute(
                """
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    DepartmentID,
                    Salary,
                    Bonus,
                    HireDate
                FROM Employee
                """
            )

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "EmployeeID": row.EmployeeID,
                "FirstName": row.FirstName,
                "LastName": row.LastName,
                "DepartmentID": row.DepartmentID,
                "Salary": float(row.Salary),
                "Bonus": float(row.Bonus) if row.Bonus is not None else None,
                "HireDate": str(row.HireDate) if row.HireDate is not None else None
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error retrieving employees: {str(e)}",
            status_code=500
        )
        
# 4. Update an existing employee (for example, changing their bonus).

@app.route(route="employees/{employee_id}", methods=["PUT"])
def update_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = req.route_params.get("employee_id")
        data = json.loads(req.get_body().decode("utf-8"))

        first_name = data.get("FirstName")
        last_name = data.get("LastName")
        department_id = data.get("DepartmentID")
        salary = data.get("Salary")
        bonus = data.get("Bonus")
        hire_date = data.get("HireDate")

        if not first_name or not last_name or department_id is None or salary is None:
            return func.HttpResponse(
                "FirstName, LastName, DepartmentID and Salary are required.",
                status_code=400
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Employee
            SET
                FirstName = ?,
                LastName = ?,
                DepartmentID = ?,
                Salary = ?,
                Bonus = ?,
                HireDate = ?
            WHERE EmployeeID = ?
            """,
            first_name,
            last_name,
            department_id,
            salary,
            bonus,
            hire_date,
            employee_id
        )

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()

            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            "Employee updated successfully.",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error updating employee: {str(e)}",
            status_code=500
        )
        
# 5. Delete an employee.

@app.route(route="employees/{employee_id}", methods=["DELETE"])
def delete_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        employee_id = req.route_params.get("employee_id")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM Employee
            WHERE EmployeeID = ?
            """,
            employee_id
        )

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()

            return func.HttpResponse(
                "Employee not found.",
                status_code=404
            )

        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(
            "Employee deleted successfully.",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Error deleting employee: {str(e)}",
            status_code=500
        )