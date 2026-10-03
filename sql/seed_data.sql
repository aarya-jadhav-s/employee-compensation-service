INSERT INTO Department (DepartmentID, DepartmentName, Location)
VALUES
(1, 'Engineering', 'Pune'),
(2, 'Human Resources', 'Mumbai'),
(3, 'Finance', 'Bangalore'),
(4, 'Sales', 'Delhi');


INSERT INTO Employee
    (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
VALUES
('Aarav', 'Sharma', 1, 75000.00, 5000.00, '2022-01-15'),
('Priya', 'Patel', 1, 85000.00, NULL, '2021-06-10'),
('Rahul', 'Mehta', 2, 60000.00, 3000.00, '2023-03-20'),
('Sneha', 'Desai', 3, 95000.00, 10000.00, '2020-11-05'),
('Vikram', 'Joshi', 4, 70000.00, NULL, '2024-01-12'),
('Ananya', 'Kulkarni', 1, 90000.00, 7500.00, '2019-08-25');
