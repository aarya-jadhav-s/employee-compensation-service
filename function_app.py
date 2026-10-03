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

def error_response(message: str, status_code: int = 500) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            "error": message
        }),
        status_code=status_code,
        mimetype="application/json"
    )

# PART A
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

    except ValueError:
        return error_response(
            "Invalid request body. Please provide valid JSON.",
            400
        )

    except pyodbc.IntegrityError:
        return error_response(
            "Invalid employee data. Please check the DepartmentID and other required fields.",
            400
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while creating the employee.",
            500
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
                COALESCE(Bonus, Salary * 0.05) AS EffectiveBonus,
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
            "EffectiveBonus": float(row.EffectiveBonus),
            "HireDate": str(row.HireDate) if row.HireDate is not None else None
        }

        return func.HttpResponse(
            json.dumps(employee),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError:
        return error_response(
            "Invalid employee ID.",
            400
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while retrieving the employee.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while retrieving the employee.",
            500
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
                    COALESCE(Bonus, Salary * 0.05) AS EffectiveBonus,
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
                    COALESCE(Bonus, Salary * 0.05) AS EffectiveBonus,
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
                "EffectiveBonus": float(row.EffectiveBonus),
                "HireDate": str(row.HireDate) if row.HireDate is not None else None
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError:
        return error_response(
            "Invalid department ID.",
            400
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while retrieving employees.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while retrieving employees.",
            500
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

    except ValueError:
        return error_response(
            "Invalid request body. Please provide valid JSON.",
            400
        )

    except pyodbc.IntegrityError:
        return error_response(
            "Invalid employee data. Please check the DepartmentID and other required fields.",
            400
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while updating the employee.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while updating the employee.",
            500
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

    except ValueError:
        return error_response(
            "Invalid employee ID.",
            400
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while deleting the employee.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while deleting the employee.",
            500
        )

# PART B
# 1. The total bonus paid across the whole company, treating employees with no bonus as 0.    
@app.route(route="reports/total-bonus", methods=["GET"])
def get_total_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(Bonus), 0) AS TotalBonus
            FROM Employee
            """
        )

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        result = {
            "TotalBonus": float(row.TotalBonus)
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while calculating total bonus.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while calculating total bonus.",
            500
        )
        
        
# 2. A list of all employees who have never received a bonus.
@app.route(route="reports/no-bonus", methods=["GET"])
def get_employees_without_bonus(req: func.HttpRequest) -> func.HttpResponse:
    try:
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
                HireDate
            FROM Employee
            WHERE Bonus IS NULL
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
                "HireDate": str(row.HireDate) if row.HireDate is not None else None
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while retrieving employees without bonus.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while retrieving employees without bonus.",
            500
        )

# 3. For each employee who has a bonus, their bonus as a percentage of their salary, rounded to 2 decimal places.
@app.route(route="reports/bonus-percentage", methods=["GET"])
def get_bonus_percentage(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                EmployeeID,
                FirstName,
                LastName,
                Salary,
                Bonus,
                ROUND(
                    (CAST(COALESCE(Bonus, 0) AS DECIMAL(12,2))
                    / NULLIF(CAST(Salary AS DECIMAL(12,2)), 0)) * 100,
                    2
                ) AS BonusPercentage
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
                "Salary": float(row.Salary),
                # "Bonus": float(row.Bonus),
                "Bonus": float(row.Bonus) if row.Bonus is not None else 0,
                "BonusPercentage": float(row.BonusPercentage)
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while calculating bonus percentage.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while calculating bonus percentage.",
            500
        )

# 4. Departments where the total bonus paid exceeds the department's average salary.

@app.route(route="reports/departments-bonus-above-average-salary", methods=["GET"])
def get_departments_bonus_above_average_salary(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                d.DepartmentID,
                d.DepartmentName,
                SUM(COALESCE(e.Bonus, 0)) AS TotalBonus,
                AVG(e.Salary) AS AverageSalary
            FROM Department d
            INNER JOIN Employee e
                ON d.DepartmentID = e.DepartmentID
            GROUP BY
                d.DepartmentID,
                d.DepartmentName
            HAVING SUM(COALESCE(e.Bonus, 0)) > AVG(e.Salary)
            """
        )

        rows = cursor.fetchall()

        departments = []

        for row in rows:
            departments.append({
                "DepartmentID": row.DepartmentID,
                "DepartmentName": row.DepartmentName,
                "TotalBonus": float(row.TotalBonus),
                "AverageSalary": float(row.AverageSalary)
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(departments),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while calculating department bonus comparison.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while calculating department bonus comparison.",
            500
        )   

# 5. Employees ranked by bonus amount, with employees who have no bonus ranked last rather than excluded.

@app.route(route="reports/bonus-ranking", methods=["GET"])
def get_bonus_ranking(req: func.HttpRequest) -> func.HttpResponse:
    try:
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
                RANK() OVER (
                    ORDER BY
                        CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END,
                        Bonus DESC
                ) AS BonusRank
            FROM Employee
            ORDER BY
                CASE WHEN Bonus IS NULL THEN 1 ELSE 0 END,
                Bonus DESC
            """
        )

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                "Rank": row.BonusRank,
                "EmployeeID": row.EmployeeID,
                "FirstName": row.FirstName,
                "LastName": row.LastName,
                "DepartmentID": row.DepartmentID,
                "Salary": float(row.Salary),
                "Bonus": float(row.Bonus) if row.Bonus is not None else None
            })

        cursor.close()
        conn.close()

        return func.HttpResponse(
            json.dumps(employees),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while calculating bonus ranking.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while calculating bonus ranking.",
            500
        )
        
# 6. The employee with the highest base salary, and — separately — whether that same person also has the highest total compensation (salary + bonus).
      
@app.route(route="reports/highest-salary", methods=["GET"])
def get_highest_salary_employee(req: func.HttpRequest) -> func.HttpResponse:
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            WITH EmployeeCompensation AS (
                SELECT
                    EmployeeID,
                    FirstName,
                    LastName,
                    DepartmentID,
                    Salary,
                    Bonus,
                    Salary + COALESCE(Bonus, 0) AS TotalCompensation
                FROM Employee
            ),
            HighestSalary AS (
                SELECT TOP 1 *
                FROM EmployeeCompensation
                ORDER BY Salary DESC
            ),
            HighestCompensation AS (
                SELECT TOP 1 *
                FROM EmployeeCompensation
                ORDER BY TotalCompensation DESC
            )
            SELECT
                hs.EmployeeID AS SalaryEmployeeID,
                hs.FirstName AS SalaryFirstName,
                hs.LastName AS SalaryLastName,
                hs.DepartmentID AS SalaryDepartmentID,
                hs.Salary AS HighestSalary,
                hs.Bonus AS SalaryEmployeeBonus,
                hs.TotalCompensation AS SalaryEmployeeTotalCompensation,

                hc.EmployeeID AS CompensationEmployeeID,
                hc.FirstName AS CompensationFirstName,
                hc.LastName AS CompensationLastName,
                hc.DepartmentID AS CompensationDepartmentID,
                hc.Salary AS CompensationEmployeeSalary,
                hc.Bonus AS HighestCompensationBonus,
                hc.TotalCompensation AS HighestTotalCompensation
            FROM HighestSalary hs
            CROSS JOIN HighestCompensation hc
            """
        )

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:
            return func.HttpResponse(
                "No employees found.",
                status_code=404
            )

        result = {
            "HighestBaseSalaryEmployee": {
                "EmployeeID": row.SalaryEmployeeID,
                "FirstName": row.SalaryFirstName,
                "LastName": row.SalaryLastName,
                "DepartmentID": row.SalaryDepartmentID,
                "Salary": float(row.HighestSalary),
                "Bonus": float(row.SalaryEmployeeBonus)
                if row.SalaryEmployeeBonus is not None else None,
                "TotalCompensation": float(row.SalaryEmployeeTotalCompensation)
            },
            "HighestTotalCompensationEmployee": {
                "EmployeeID": row.CompensationEmployeeID,
                "FirstName": row.CompensationFirstName,
                "LastName": row.CompensationLastName,
                "DepartmentID": row.CompensationDepartmentID,
                "Salary": float(row.CompensationEmployeeSalary),
                "Bonus": float(row.HighestCompensationBonus)
                if row.HighestCompensationBonus is not None else None,
                "TotalCompensation": float(row.HighestTotalCompensation)
            },
            "SameEmployee": (
                row.SalaryEmployeeID == row.CompensationEmployeeID
            )
        }

        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )

    except pyodbc.Error:
        return error_response(
            "A database error occurred while calculating highest salary and compensation.",
            500
        )

    except Exception:
        return error_response(
            "An unexpected error occurred while calculating highest salary and compensation.",
            500
        )
