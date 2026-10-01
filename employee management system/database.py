import sqlite3
from datetime import datetime
import threading
import os

class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'employees.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT,
                hire_date TEXT,
                salary REAL,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                check_in TEXT,
                check_out TEXT,
                date TEXT,
                status TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        self.conn.commit()
    
    def add_employee(self, name, position, department, hire_date, salary):
        with self._lock:
            self.cursor.execute('''
                INSERT INTO employees (name, position, department, hire_date, salary)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, position, department, hire_date, salary))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def get_all_employees(self):
        with self._lock:
            self.cursor.execute('SELECT * FROM employees WHERE status="active"')
            return self.cursor.fetchall()
    
    def delete_employee(self, emp_id):
        with self._lock:
            self.cursor.execute('UPDATE employees SET status="inactive" WHERE id = ?', (emp_id,))
            self.conn.commit()
    
    def record_attendance(self, employee_id, check_in, check_out=None, status='present'):
        with self._lock:
            date = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute('''
                INSERT INTO attendance (employee_id, check_in, check_out, date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (employee_id, check_in, check_out, date, status))
            self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()