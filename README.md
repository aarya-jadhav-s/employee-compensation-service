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