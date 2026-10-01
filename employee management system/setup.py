"""
Employee Tracker System - Setup
Simple and error-free
"""

from setuptools import setup

setup(
    name="EmployeeTracker",
    version="1.0.0",
    description="Employee Tracker System with UI",
    author="Your Name",
    py_modules=['employee_tracker', 'ui', 'database', 'threading_manager'],
    entry_points={
        'console_scripts': [
            'employee-tracker=employee_tracker:main',
        ],
    },
    python_requires='>=3.6',
)