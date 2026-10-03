# employee-compensation-service
Azure Functions Employee Compensation Service

# Employee Compensation Service

Azure Functions-based HR backend service for managing employee records and compensation data using Azure SQL Database.

## Tech Stack

- Python
- Azure Functions
- Azure SQL Database
- SQL Server
- pyodbc
- Postman

## Architecture

```text
Client / Postman
       |
       v
Azure Functions
       |
       v
Azure SQL Database
```

All employee reads and writes are handled through the Azure Functions API layer. Clients do not access the database directly.

---

## Part A — Employee CRUD APIs

### API Base URL

For local development:

```text
http://localhost:7071/api
```

### API Endpoints

| Operation                      | Method | Endpoint                                  |
| ------------------------------ | ------ | ----------------------------------------- |
| Create employee                | POST   | `/employees`                              |
| Get employee by ID             | GET    | `/employees/{employee_id}`                |
| Get all employees              | GET    | `/employees`                              |
| Filter employees by department | GET    | `/employees?departmentId={department_id}` |
| Update employee                | PUT    | `/employees/{employee_id}`                |
| Delete employee                | DELETE | `/employees/{employee_id}`                |

---

### 1. Create Employee

`POST /employees`

Creates a new employee record.

**Request**

```json
{
    "FirstName": "Test",
    "LastName": "Employee",
    "DepartmentID": 1,
    "Salary": 80000,
    "Bonus": 5000,
    "HireDate": "2025-01-10"
}
```

`FirstName`, `LastName`, `DepartmentID`, and `Salary` are required.
`Bonus` and `HireDate` are optional.

**Response**

`201 Created`

```text
Employee created successfully with EmployeeID: <id>
```

---

### 2. Get Employee by ID

`GET /employees/{employee_id}`

Retrieves an employee using their `EmployeeID`.

**Example**

```text
GET /employees/1
```

**Response**

`200 OK`

```json
{
    "EmployeeID": 1,
    "FirstName": "Aarav",
    "LastName": "Sharma",
    "DepartmentID": 1,
    "Salary": 75000.0,
    "Bonus": 5000.0,
    "HireDate": "2022-01-15"
}
```

---

### 3. Get All Employees

`GET /employees`

Returns all employee records.

**Example**

```text
GET /employees
```

**Response**

`200 OK`

Returns a JSON array containing employee records.

---

### 4. Get Employees by Department

`GET /employees?departmentId={department_id}`

The `departmentId` query parameter is optional.

**Get all employees**

```text
GET /employees
```

**Filter by department**

```text
GET /employees?departmentId=1
```

Returns only employees belonging to the specified department.

---

### 5. Update Employee

`PUT /employees/{employee_id}`

Updates an existing employee record.

**Example**

```text
PUT /employees/1
```

**Request**

```json
{
    "FirstName": "Aarav",
    "LastName": "Sharma",
    "DepartmentID": 1,
    "Salary": 80000,
    "Bonus": 6000,
    "HireDate": "2022-01-15"
}
```

**Response**

`200 OK`

```text
Employee updated successfully.
```

---

### 6. Delete Employee

`DELETE /employees/{employee_id}`

Deletes an employee using their `EmployeeID`.

**Example**

```text
DELETE /employees/1
```

No request body is required.

**Response**

`200 OK`

```text
Employee deleted successfully.
```

---

### Part A Status

- [x] Create employee
- [x] Get employee by ID
- [x] Get all employees
- [x] Filter employees by department
- [x] Update employee
- [x] Delete employee

---

## Part B — Compensation & Reporting APIs

Part B provides reporting endpoints for analysing employee bonuses, compensation, and salary information.

### Reporting Endpoints

| Report                                               | Method | Endpoint                                          |
| ---------------------------------------------------- | ------ | ------------------------------------------------- |
| Total bonus across company                           | GET    | `/reports/total-bonus`                            |
| Employees without bonus                              | GET    | `/reports/no-bonus`                               |
| Bonus as % of salary                                 | GET    | `/reports/bonus-percentage`                       |
| Departments where total bonus exceeds average salary | GET    | `/reports/departments-bonus-above-average-salary` |
| Employees ranked by bonus                            | GET    | `/reports/bonus-ranking`                          |
| Highest salary & total compensation                  | GET    | `/reports/highest-salary`                         |

---

### 1. Total Bonus Across Company

`GET /reports/total-bonus`

Calculates the total bonus paid across all employees.

Employees with a `NULL` bonus are treated as having a bonus value of `0`.

**Example**

```text
GET /reports/total-bonus
```

**Response**

`200 OK`

```json
{
    "TotalBonus": "<calculated value>"
}
```

---

### 2. Employees Without Bonus

`GET /reports/no-bonus`

Returns employees whose bonus is `NULL`.

**Example**

```text
GET /reports/no-bonus
```

**Response**

`200 OK`

Returns a JSON array containing employees who have no bonus.

---

### 3. Bonus as Percentage of Salary

`GET /reports/bonus-percentage`

Calculates the bonus received by each employee as a percentage of their base salary, rounded to two decimal places.

Employees without a bonus are shown with a bonus value of `0` and a bonus percentage of `0`.

**Formula**

```text
Bonus Percentage = (Bonus / Salary) × 100
```

**Example**

```text
GET /reports/bonus-percentage
```

**Response**

`200 OK`

```json
[
    {
        "EmployeeID": 1,
        "FirstName": "Aarav",
        "LastName": "Sharma",
        "Salary": 75000.0,
        "Bonus": 5000.0,
        "BonusPercentage": 6.67
    }
]
```

---

### 4. Departments Where Total Bonus Exceeds Average Salary

`GET /reports/departments-bonus-above-average-salary`

Returns departments where the total bonus paid to employees in that department exceeds the department's average employee salary.

**Example**

```text
GET /reports/departments-bonus-above-average-salary
```

**Response**

`200 OK`

Returns a JSON array containing:

- Department ID
- Department name
- Total bonus
- Average salary

If no department satisfies the condition, the API returns an empty array.

---

### 5. Employee Bonus Ranking

`GET /reports/bonus-ranking`

Ranks employees according to their bonus amount. Employees with higher bonuses receive higher rankings, and employees with `NULL` bonuses are placed at the end.

**Example**

```text
GET /reports/bonus-ranking
```

**Response**

`200 OK`

```json
[
    {
        "Rank": 1,
        "EmployeeID": 10,
        "FirstName": "Neha",
        "LastName": "Patil",
        "DepartmentID": 1,
        "Salary": 50000.0,
        "Bonus": 90000.0
    }
]
```

The ranking is calculated dynamically using SQL's `RANK()` window function and is not stored as a column in the `Employee` table.

---

### 6. Highest Base Salary and Total Compensation

`GET /reports/highest-salary`

Identifies:

- The employee with the highest base salary
- The employee with the highest total compensation
- Whether the two employees are the same person

**Formula**

```text
Total Compensation = Salary + Bonus
```

A `NULL` bonus is treated as `0`.

**Example**

```text
GET /reports/highest-salary
```

**Response**

`200 OK`

```json
{
    "HighestBaseSalaryEmployee": {
        "EmployeeID": 4,
        "FirstName": "Sneha",
        "LastName": "Desai",
        "DepartmentID": 3,
        "Salary": 95000.0,
        "Bonus": 10000.0,
        "TotalCompensation": 105000.0
    },
    "HighestTotalCompensationEmployee": {
        "EmployeeID": 10,
        "FirstName": "Neha",
        "LastName": "Patil",
        "DepartmentID": 1,
        "Salary": 50000.0,
        "Bonus": 90000.0,
        "TotalCompensation": 140000.0
    },
    "SameEmployee": false
}
```

---

### Part B Status

- [x] Total bonus across company
- [x] Employees without bonus
- [x] Bonus as percentage of salary
- [x] Departments where total bonus exceeds average salary
- [x] Employees ranked by bonus
- [x] Highest base salary employee
- [x] Highest total compensation employee
- [x] Comparison of highest salary and highest total compensation employee