import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import csv
import os
from database import Database
from threading_manager import thread_manager

class EmployeeTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Tracker System")
        self.root.geometry("1200x750")
        
        # Set styles
        self.setup_styles()
        
        self.db = Database()
        thread_manager.start_workers(3)
        
        # Setup UI
        self.setup_ui()
        self.load_employees()
    
    def setup_styles(self):
        """Configure modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#3498DB',
            'success': '#27AE60',
            'danger': '#E74C3C',
            'light': '#ECF0F1',
            'dark': '#2C3E50',
            'white': '#FFFFFF',
            'bg_light': '#F0F4F8',  # Light background for details
            'bg_dark': '#1a1a2e',   # Dark background option
            'card_bg': '#FFFFFF',   # Card background
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D',
        }
        
        # Treeview heading
        style.configure(
            'Treeview.Heading',
            font=('Helvetica', 11, 'bold'),
            background=self.colors['primary'],
            foreground='white',
            padding=8
        )
        
        # Treeview rows
        style.configure(
            'Treeview',
            font=('Helvetica', 10),
            rowheight=35,
            background='white',
            fieldbackground='white'
        )
        
        # Buttons
        style.configure(
            'Success.TButton',
            font=('Helvetica', 10, 'bold'),
            padding=8,
            background=self.colors['success'],
            foreground='white',
            borderwidth=0
        )
        
        style.configure(
            'Danger.TButton',
            font=('Helvetica', 10, 'bold'),
            padding=8,
            background=self.colors['danger'],
            foreground='white',
            borderwidth=0
        )
        
        style.configure(
            'Action.TButton',
            font=('Helvetica', 10, 'bold'),
            padding=8,
            background=self.colors['secondary'],
            foreground='white',
            borderwidth=0
        )
        
        # LabelFrame style
        style.configure(
            'Details.TLabelframe',
            background=self.colors['bg_light'],
            borderwidth=2,
            relief='solid'
        )
        
        style.configure(
            'Details.TLabelframe.Label',
            font=('Helvetica', 12, 'bold'),
            foreground=self.colors['primary'],
            background=self.colors['bg_light']
        )
    
    def setup_ui(self):
        """Setup the main UI"""
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Ready")
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            font=('Helvetica', 9),
            background=self.colors['dark'],
            foreground='white',
            padding=5
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu
        self.create_menu()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Content - Left and Right panels
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # LEFT PANEL - Employee List
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Search bar
        self.create_search_bar(left_frame)
        
        # Treeview
        self.create_treeview(left_frame)
        
        # RIGHT PANEL - Employee Details
        right_frame = ttk.Frame(content_frame, width=450)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Employee Details with proper display
        self.create_details_panel(right_frame)
        
        # Action buttons
        self.create_action_buttons(right_frame)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_employee_select)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📤 Export Data", command=self.export_data)
        file_menu.add_command(label="📋 Attendance Report", command=self.show_attendance_report)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
    
    def create_header(self, parent):
        """Create header with title and stats"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(
            header_frame,
            text="🏢 Employee Tracker System",
            font=('Helvetica', 18, 'bold'),
            foreground=self.colors['primary']
        )
        title.pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(
            header_frame,
            text="📊 Total: 0 employees",
            font=('Helvetica', 11),
            foreground=self.colors['secondary']
        )
        self.stats_label.pack(side=tk.RIGHT)
    
    def create_search_bar(self, parent):
        """Create search bar"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_employees())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=35)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            search_frame,
            text="➕ Add Employee",
            style='Success.TButton',
            command=self.show_add_dialog
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_treeview(self, parent):
        """Create employee list treeview"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Name', 'Position', 'Department', 'Hire Date', 'Salary', 'Status')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        # Column widths
        widths = {'ID': 60, 'Name': 160, 'Position': 140, 'Department': 130, 
                 'Hire Date': 110, 'Salary': 110, 'Status': 100}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 120), anchor='center' if col == 'ID' else 'w')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def create_details_panel(self, parent):
        """Create employee details panel with proper background"""
        # Details Frame with background
        details_frame = ttk.LabelFrame(
            parent, 
            text="👤 Employee Details", 
            padding=15,
            style='Details.TLabelframe'
        )
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main container with background color
        self.details_container = tk.Frame(
            details_frame,
            bg=self.colors['bg_light'],
            relief='flat'
        )
        self.details_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(
            self.details_container,
            highlightthickness=0,
            bg=self.colors['bg_light']
        )
        scrollbar = ttk.Scrollbar(
            self.details_container, 
            orient="vertical", 
            command=canvas.yview
        )
        
        # Scrollable frame with background
        self.scrollable_frame = tk.Frame(
            canvas,
            bg=self.colors['bg_light']
        )
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder when no employee selected"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Placeholder with background
        placeholder_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.colors['bg_light'],
            height=400,
            width=400
        )
        placeholder_frame.pack(expand=True, fill=tk.BOTH)
        placeholder_frame.pack_propagate(False)
        
        # Placeholder message
        placeholder = tk.Label(
            placeholder_frame,
            text="👈 Select an employee from the list\n\nto view details here",
            font=('Helvetica', 14),
            fg='#7F8C8D',
            bg=self.colors['bg_light'],
            justify='center'
        )
        placeholder.pack(expand=True)
    
    def show_employee_details(self, values):
        """Display employee details with proper background"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Main container with background
        main_container = tk.Frame(
            self.scrollable_frame,
            bg=self.colors['bg_light']
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with employee name
        header_frame = tk.Frame(
            main_container,
            bg=self.colors['white'],
            relief='flat',
            bd=0
        )
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        header_frame.config(height=70)
        
        # Employee name with icon
        name_label = tk.Label(
            header_frame,
            text=f"👤 {values[1]}",
            font=('Helvetica', 18, 'bold'),
            fg=self.colors['primary'],
            bg=self.colors['white']
        )
        name_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Separator
        separator = tk.Frame(
            main_container,
            bg=self.colors['light'],
            height=2
        )
        separator.pack(fill=tk.X, pady=5)
        
        # Details card with white background
        card_frame = tk.Frame(
            main_container,
            bg=self.colors['white'],
            relief='flat',
            bd=1
        )
        card_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Details in a grid
        details = [
            ("📋 Employee ID", values[0]),
            ("👤 Full Name", values[1]),
            ("💼 Position", values[2]),
            ("🏢 Department", values[3]),
            ("📅 Hire Date", values[4]),
            ("💰 Salary", values[5]),
            ("📊 Status", values[6])
        ]
        
        # Create grid with proper spacing
        for i, (label, value) in enumerate(details):
            # Row frame with background
            row_frame = tk.Frame(
                card_frame,
                bg=self.colors['white']
            )
            row_frame.pack(fill=tk.X, pady=5, padx=20)
            
            # Label
            label_widget = tk.Label(
                row_frame,
                text=label + ":",
                font=('Helvetica', 11, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['white'],
                width=18,
                anchor='e'
            )
            label_widget.pack(side=tk.LEFT, padx=(0, 15))
            
            # Value
            value_text = str(value) if value else "N/A"
            
            # Color coding for status
            if label == "📊 Status":
                if "Active" in value_text or "active" in value_text:
                    value_text = "🟢 Active"
                    fg_color = '#27AE60'
                else:
                    value_text = "🔴 Inactive"
                    fg_color = '#E74C3C'
            elif label == "💰 Salary":
                # Keep salary formatting
                fg_color = self.colors['primary']
            else:
                fg_color = self.colors['dark']
            
            value_widget = tk.Label(
                row_frame,
                text=value_text,
                font=('Helvetica', 11),
                fg=fg_color,
                bg=self.colors['white'],
                anchor='w'
            )
            value_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add padding at bottom
        bottom_padding = tk.Frame(
            card_frame,
            bg=self.colors['white'],
            height=10
        )
        bottom_padding.pack(fill=tk.X)
        
        # Update status bar
        self.status_var.set(f"✅ Showing details for: {values[1]}")
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Button grid
        buttons = [
            ('✏️ Edit', self.edit_employee, 'Action.TButton'),
            ('🗑️ Delete', self.delete_employee, 'Danger.TButton'),
            ('✅ Check In', self.check_in, 'Success.TButton'),
            ('❌ Check Out', self.check_out, 'Action.TButton'),
            ('🔄 Refresh', self.load_employees, 'Action.TButton'),
        ]
        
        for text, command, style in buttons:
            btn = ttk.Button(
                button_frame,
                text=text,
                style=style,
                command=command
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
    
    def load_employees(self):
        """Load employees from database"""
        def load_task():
            return self.db.get_all_employees()
        
        self.status_var.set("⏳ Loading employees...")
        task_id = thread_manager.submit_task(load_task)
        
        def check_result():
            try:
                employees = thread_manager.get_result(task_id, timeout=0.1)
                
                # Clear treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Add employees
                for i, emp in enumerate(employees):
                    emp_list = list(emp)
                    if len(emp_list) > 5 and emp_list[5] is not None:
                        emp_list[5] = f"${emp_list[5]:,.2f}"
                    
                    # Status with emoji
                    if len(emp_list) > 6:
                        emp_list[6] = '🟢 Active' if emp_list[6] == 'active' else '🔴 Inactive'
                    
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    self.tree.insert('', 'end', values=emp_list, tags=(tag,))
                
                # Row colors
                self.tree.tag_configure('evenrow', background='white')
                self.tree.tag_configure('oddrow', background='#F8F9FA')
                
                self.stats_label.config(text=f"📊 Total: {len(employees)} employees")
                self.status_var.set(f"✅ Loaded {len(employees)} employees")
                
                # Reset details panel if no selection
                if not self.tree.selection():
                    self.show_placeholder()
                
            except TimeoutError:
                self.root.after(100, check_result)
            except Exception as e:
                self.status_var.set(f"❌ Error: {str(e)}")
        
        self.root.after(100, check_result)
    
    def search_employees(self):
        """Search employees"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.load_employees()
            return
        
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values:
                if search_term in str(values[1]).lower() or search_term in str(values[2]).lower():
                    self.tree.selection_set(item)
                    self.tree.see(item)
                else:
                    self.tree.selection_remove(item)
    
    def on_employee_select(self, event):
        """Display employee details when selected"""
        selection = self.tree.selection()
        if not selection:
            self.show_placeholder()
            return
        
        values = self.tree.item(selection[0], 'values')
        if values and len(values) >= 7:
            # Show details
            self.show_employee_details(values)
        else:
            self.show_placeholder()
    
    def show_add_dialog(self):
        """Show add employee dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Employee")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 600) // 2
        dialog.geometry(f'500x600+{x}+{y}')
        
        # Main container
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            main_frame,
            text="➕ Add New Employee",
            font=('Helvetica', 16, 'bold'),
            foreground=self.colors['primary']
        ).pack(pady=(0, 20))
        
        # Form fields
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ('Full Name', 'entry'),
            ('Position', 'entry'),
            ('Department', 'entry'),
            ('Hire Date', 'entry', 'Format: YYYY-MM-DD'),
            ('Salary', 'entry', 'Enter numeric value')
        ]
        
        entries = {}
        for i, field in enumerate(fields):
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=8)
            
            label = ttk.Label(
                frame,
                text=field[0] + ":",
                font=('Helvetica', 10, 'bold'),
                width=15
            )
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
            
            entries[field[0].lower().replace(' ', '_')] = entry
            
            if len(field) > 2:
                hint = ttk.Label(
                    frame,
                    text=field[2],
                    font=('Helvetica', 8),
                    foreground='gray'
                )
                hint.pack(side=tk.RIGHT)
        
        def save():
            data = {key: entry.get().strip() for key, entry in entries.items()}
            
            if not all(data.values()):
                messagebox.showerror("Error", "⚠️ All fields are required!")
                return
            
            try:
                def add_task():
                    return self.db.add_employee(
                        data['full_name'],
                        data['position'],
                        data['department'],
                        data['hire_date'],
                        float(data['salary'])
                    )
                
                task_id = thread_manager.submit_task(add_task)
                self.status_var.set("⏳ Adding employee...")
                
                def check():
                    try:
                        emp_id = thread_manager.get_result(task_id, timeout=0.1)
                        self.load_employees()
                        self.status_var.set(f"✅ Employee added! ID: {emp_id}")
                        dialog.destroy()
                        messagebox.showinfo("Success", f"Employee added with ID: {emp_id}")
                    except TimeoutError:
                        self.root.after(100, check)
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
                
                self.root.after(100, check)
                
            except ValueError:
                messagebox.showerror("Error", "❌ Invalid salary format!\nPlease enter a number.")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Save Employee",
            style='Success.TButton',
            command=save
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            style='Action.TButton',
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def edit_employee(self):
        """Edit selected employee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first!")
            return
        
        values = self.tree.item(selection[0], 'values')
        if values:
            messagebox.showinfo(
                "Edit Employee",
                f"Editing employee: {values[1]}\n\n"
                f"Current Details:\n"
                f"Position: {values[2]}\n"
                f"Department: {values[3]}\n"
                f"Salary: {values[5]}\n\n"
                "Edit functionality coming soon!"
            )
    
    def delete_employee(self):
        """Delete selected employee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first!")
            return
        
        values = self.tree.item(selection[0], 'values')
        if messagebox.askyesno("Confirm Delete", f"Delete employee '{values[1]}'?"):
            emp_id = values[0]
            
            def delete_task():
                self.db.delete_employee(emp_id)
                return True
            
            task_id = thread_manager.submit_task(delete_task)
            self.status_var.set("⏳ Deleting...")
            
            def check():
                try:
                    thread_manager.get_result(task_id, timeout=0.1)
                    self.load_employees()
                    self.status_var.set("✅ Employee deleted!")
                    self.show_placeholder()
                    messagebox.showinfo("Success", "Employee deleted successfully!")
                except TimeoutError:
                    self.root.after(100, check)
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            self.root.after(100, check)
    
    def check_in(self):
        """Record employee check-in"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first!")
            return
        
        values = self.tree.item(selection[0], 'values')
        emp_id = values[0]
        check_in_time = datetime.now().strftime('%H:%M:%S')
        
        def task():
            self.db.record_attendance(emp_id, check_in_time, None, 'present')
            return True
        
        thread_manager.submit_task(task)
        self.status_var.set(f"✅ Checked in at {check_in_time}")
        messagebox.showinfo("Check In", f"✅ Checked in at {check_in_time}")
    
    def check_out(self):
        """Record employee check-out"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first!")
            return
        
        values = self.tree.item(selection[0], 'values')
        emp_id = values[0]
        check_out_time = datetime.now().strftime('%H:%M:%S')
        
        def task():
            conn = self.db.conn
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE attendance 
                SET check_out = ? 
                WHERE employee_id = ? AND date = ? AND check_out IS NULL
                ORDER BY id DESC LIMIT 1
            ''', (check_out_time, emp_id, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            return True
        
        thread_manager.submit_task(task)
        self.status_var.set(f"✅ Checked out at {check_out_time}")
        messagebox.showinfo("Check Out", f"✅ Checked out at {check_out_time}")
    
    def show_attendance_report(self):
        """Show attendance report"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Attendance Report")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        
        ttk.Label(
            dialog,
            text="📋 Attendance Report",
            font=('Helvetica', 16, 'bold'),
            foreground=self.colors['primary']
        ).pack(pady=10)
        
        columns = ('ID', 'Employee ID', 'Check In', 'Check Out', 'Date', 'Status')
        tree = ttk.Treeview(dialog, columns=columns, show='headings', height=25)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        
        vsb = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        def load_attendance():
            conn = self.db.conn
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM attendance ORDER BY date DESC LIMIT 100')
            return cursor.fetchall()
        
        task_id = thread_manager.submit_task(load_attendance)
        
        def update_report():
            try:
                records = thread_manager.get_result(task_id, timeout=0.1)
                for record in records:
                    tree.insert('', 'end', values=record)
                self.status_var.set(f"✅ Loaded {len(records)} records")
            except TimeoutError:
                self.root.after(100, update_report)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        self.root.after(100, update_report)
    
    def export_data(self):
        """Export employee data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            def export_task():
                employees = self.db.get_all_employees()
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Name', 'Position', 'Department', 'Hire Date', 'Salary', 'Status'])
                    writer.writerows(employees)
                return True
            
            thread_manager.submit_task(export_task)
            self.status_var.set(f"📤 Exported to {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"Data exported to:\n{os.path.basename(filename)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        ╔════════════════════════════════════════════╗
        ║     🏢 EMPLOYEE TRACKER SYSTEM            ║
        ╠════════════════════════════════════════════╣
        ║                                            ║
        ║   Version: 1.0.0                           ║
        ║   Built with: Python 3, Tkinter, SQLite   ║
        ║                                            ║
        ║   ✨ Features:                             ║
        ║   • Employee Management                   ║
        ║   • Attendance Tracking                   ║
        ║   • Search & Filter                       ║
        ║   • Export Data to CSV                    ║
        ║   • Multi-threading Support               ║
        ║                                            ║
        ╚════════════════════════════════════════════╝
        """
        messagebox.showinfo("ℹ️ About", about_text)
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            thread_manager.shutdown()
            self.db.close()
        except:
            pass

def main():
    root = tk.Tk()
    app = EmployeeTrackerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()