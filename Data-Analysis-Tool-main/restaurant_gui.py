import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import json
from pathlib import Path
import threading
from typing import Dict, Any, Optional

# Import your foundation classes
from restaurant_data_foundation import RestaurantDataAnalyzer, ColumnMapping

class RestaurantAnalysisGUI:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("system")  # or "dark" or "light"
        ctk.set_default_color_theme("blue")
        
        # Initialize analyzer
        self.analyzer = RestaurantDataAnalyzer()
        self.current_file = None
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Restaurant Data Analysis Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_sidebar(self):
        """Create the left sidebar with controls"""
        self.sidebar = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # Push content to top
        
        # Title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Restaurant Data\nAnalysis Tool", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # File Operations Section
        file_frame = ctk.CTkFrame(self.sidebar)
        file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(file_frame, text="1. Load Data", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        
        self.load_button = ctk.CTkButton(
            file_frame, 
            text="Load CSV/Excel File",
            command=self.load_file
        )
        self.load_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.file_label = ctk.CTkLabel(file_frame, text="No file loaded", text_color="gray")
        self.file_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Column Mapping Section
        mapping_frame = ctk.CTkFrame(self.sidebar)
        mapping_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(mapping_frame, text="2. Map Columns", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        
        self.auto_map_button = ctk.CTkButton(
            mapping_frame,
            text="Auto-Detect Columns",
            command=self.auto_map_columns,
            state="disabled"
        )
        self.auto_map_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.manual_map_button = ctk.CTkButton(
            mapping_frame,
            text="Manual Mapping",
            command=self.open_column_mapping,
            state="disabled"
        )
        self.manual_map_button.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Data Cleaning Section
        cleaning_frame = ctk.CTkFrame(self.sidebar)
        cleaning_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(cleaning_frame, text="3. Clean Data", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        
        self.remove_duplicates_var = ctk.BooleanVar(value=True)
        self.remove_duplicates_check = ctk.CTkCheckBox(
            cleaning_frame,
            text="Remove Duplicates",
            variable=self.remove_duplicates_var
        )
        self.remove_duplicates_check.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        
        self.missing_data_var = ctk.StringVar(value="report")
        self.missing_data_menu = ctk.CTkOptionMenu(
            cleaning_frame,
            values=["report", "drop_rows", "drop_cols"],
            variable=self.missing_data_var
        )
        self.missing_data_menu.grid(row=2, column=0, padx=10, pady=(2, 10), sticky="ew")
        
        # Analysis Section
        analysis_frame = ctk.CTkFrame(self.sidebar)
        analysis_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(analysis_frame, text="4. Analyze", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        
        self.analyze_button = ctk.CTkButton(
            analysis_frame,
            text="Run Analysis",
            command=self.run_analysis,
            state="disabled"
        )
        self.analyze_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.export_button = ctk.CTkButton(
            analysis_frame,
            text="Export Report",
            command=self.export_report,
            state="disabled"
        )
        self.export_button.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Configure grid weights for sidebar frames
        for frame in [file_frame, mapping_frame, cleaning_frame, analysis_frame]:
            frame.grid_columnconfigure(0, weight=1)
    
    def create_main_content(self):
        """Create the main content area with tabs"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Data Preview Tab
        self.data_tab = self.tabview.add("Data Preview")
        self.create_data_preview_tab()
        
        # Column Mapping Tab
        self.mapping_tab = self.tabview.add("Column Mapping")
        self.create_mapping_tab()
        
        # Analysis Results Tab
        self.results_tab = self.tabview.add("Analysis Results")
        self.create_results_tab()
    
    def create_data_preview_tab(self):
        """Create data preview tab content"""
        # Data info frame
        info_frame = ctk.CTkFrame(self.data_tab)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="Data Information:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        
        self.data_info_text = ctk.CTkTextbox(info_frame, height=100)
        self.data_info_text.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Data preview frame
        preview_frame = ctk.CTkFrame(self.data_tab)
        preview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(preview_frame, text="Data Preview (First 10 rows):", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )
        
        # Treeview for data preview
        self.tree_frame = tk.Frame(preview_frame)
        self.tree_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        self.data_tree = ttk.Treeview(self.tree_frame)
        
        # Scrollbars for treeview
        tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.data_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        self.data_tab.grid_rowconfigure(1, weight=1)
        self.data_tab.grid_columnconfigure(0, weight=1)
    
    def create_mapping_tab(self):
        """Create column mapping tab content"""
        # Instructions
        instructions = ctk.CTkLabel(
            self.mapping_tab, 
            text="Map your data columns to analysis fields. Auto-detection will be attempted first.",
            font=ctk.CTkFont(size=12)
        )
        instructions.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Mapping frame
        self.mapping_frame = ctk.CTkScrollableFrame(self.mapping_tab)
        self.mapping_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.mapping_frame.grid_columnconfigure(1, weight=1)
        
        self.mapping_tab.grid_rowconfigure(1, weight=1)
        self.mapping_tab.grid_columnconfigure(0, weight=1)
        
        # Will be populated when data is loaded
        self.mapping_widgets = {}
    
    def create_results_tab(self):
        """Create analysis results tab content"""
        self.results_text = ctk.CTkTextbox(self.results_tab)
        self.results_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.results_tab.grid_rowconfigure(0, weight=1)
        self.results_tab.grid_columnconfigure(0, weight=1)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.status_bar)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.progress_bar.set(0)
    
    def update_status(self, message: str, progress: float = None):
        """Update status bar"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
    
    def load_file(self):
        """Load data file"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("All Supported", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        def load_thread():
            try:
                self.update_status("Loading file...", 0.2)
                
                # Handle Excel sheet selection
                if file_path.lower().endswith(('.xlsx', '.xls')):
                    excel_file = pd.ExcelFile(file_path)
                    if len(excel_file.sheet_names) > 1:
                        sheet_name = self.select_excel_sheet(excel_file.sheet_names)
                        if not sheet_name:
                            self.update_status("Ready", 0)
                            return
                    else:
                        sheet_name = None
                else:
                    sheet_name = None
                
                self.update_status("Processing data...", 0.5)
                
                # Load data
                success = self.analyzer.load_data(file_path, sheet_name)
                
                if success:
                    self.current_file = file_path
                    self.file_label.configure(text=Path(file_path).name, text_color="green")
                    
                    # Update UI
                    self.update_data_preview()
                    self.create_mapping_widgets()
                    
                    # Enable buttons
                    self.auto_map_button.configure(state="normal")
                    self.manual_map_button.configure(state="normal")
                    
                    self.update_status("File loaded successfully", 1.0)
                    
                    # Switch to data preview tab
                    self.tabview.set("Data Preview")
                    
                else:
                    self.update_status("Failed to load file", 0)
                    messagebox.showerror("Error", "Failed to load the selected file")
                
            except Exception as e:
                self.update_status("Error loading file", 0)
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
        
        # Run in thread to prevent UI freezing
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def select_excel_sheet(self, sheet_names):
        """Dialog to select Excel sheet"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Select Excel Sheet")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        selected_sheet = None
        
        ctk.CTkLabel(dialog, text="Select sheet to load:").pack(pady=10)
        
        sheet_var = ctk.StringVar(value=sheet_names[0])
        sheet_menu = ctk.CTkOptionMenu(dialog, values=sheet_names, variable=sheet_var)
        sheet_menu.pack(pady=10)
        
        def confirm():
            nonlocal selected_sheet
            selected_sheet = sheet_var.get()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="OK", command=confirm).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=cancel).pack(side="left", padx=5)
        
        dialog.wait_window()
        return selected_sheet
    
    def update_data_preview(self):
        """Update the data preview tab"""
        if self.analyzer.data is None:
            return
        
        # Update data info
        data_info = self.analyzer.inspect_data()
        info_text = f"""Shape: {data_info['shape'][0]} rows × {data_info['shape'][1]} columns
Memory Usage: {data_info['memory_usage'] / 1024:.1f} KB
Missing Values: {sum(data_info['missing_values'].values())} total

Columns: {', '.join(data_info['columns'])}"""
        
        self.data_info_text.delete("1.0", "end")
        self.data_info_text.insert("1.0", info_text)
        
        # Update data preview tree
        df = self.analyzer.data.head(10)
        
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Configure columns
        self.data_tree["columns"] = list(df.columns)
        self.data_tree["show"] = "headings"
        
        # Configure column headings and widths
        for col in df.columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100, minwidth=50)
        
        # Insert data
        for index, row in df.iterrows():
            self.data_tree.insert("", "end", values=list(row))
    
    def create_mapping_widgets(self):
        """Create column mapping widgets"""
        # Clear existing widgets
        for widget in self.mapping_widgets.values():
            widget.destroy()
        self.mapping_widgets.clear()
        
        if self.analyzer.data is None:
            return
        
        # Get available columns
        columns = [""] + list(self.analyzer.data.columns)
        
        # Create mapping widgets for each field
        fields = [
            ("date", "Date/Time Column"),
            ("item_name", "Item Name Column"),
            ("price", "Price Column"),
            ("quantity", "Quantity Column"),
            ("category", "Category Column"),
            ("order_id", "Order ID Column"),
            ("employee", "Employee Column"),
            ("payment_method", "Payment Method Column"),
            ("customer_id", "Customer ID Column"),
            ("tax", "Tax Column"),
            ("discount", "Discount Column"),
            ("tip", "Tip Column"),
            ("cost", "Cost Column")
        ]
        
        row = 0
        for field_name, display_name in fields:
            # Label
            label = ctk.CTkLabel(self.mapping_frame, text=display_name)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            # Dropdown
            var = ctk.StringVar()
            dropdown = ctk.CTkOptionMenu(self.mapping_frame, values=columns, variable=var)
            dropdown.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            
            self.mapping_widgets[field_name] = (var, dropdown)
            row += 1
    
    def auto_map_columns(self):
        """Auto-detect column mappings"""
        if self.analyzer.data is None:
            return
        
        def map_thread():
            try:
                self.update_status("Auto-detecting columns...", 0.5)
                mapping = self.analyzer.auto_map_columns()
                
                # Update mapping widgets
                for field_name, (var, dropdown) in self.mapping_widgets.items():
                    column_name = getattr(mapping, field_name, None)
                    if column_name:
                        var.set(column_name)
                    else:
                        var.set("")
                
                self.update_status("Column mapping completed", 1.0)
                
                # Switch to mapping tab
                self.tabview.set("Column Mapping")
                
                # Enable analyze button
                self.analyze_button.configure(state="normal")
                
            except Exception as e:
                self.update_status("Error in auto-mapping", 0)
                messagebox.showerror("Error", f"Error in auto-mapping: {str(e)}")
        
        thread = threading.Thread(target=map_thread)
        thread.daemon = True
        thread.start()
    
    def open_column_mapping(self):
        """Open manual column mapping"""
        self.tabview.set("Column Mapping")
    
    def run_analysis(self):
        """Run the data analysis"""
        def analysis_thread():
            try:
                self.update_status("Preparing analysis...", 0.2)
                
                # Get current mapping from widgets
                mapping_dict = {}
                for field_name, (var, dropdown) in self.mapping_widgets.items():
                    if var.get() and var.get() != "":
                        mapping_dict[field_name] = var.get()
                
                # Set mapping
                if mapping_dict:
                    self.analyzer.set_column_mapping(**mapping_dict)
                
                self.update_status("Cleaning data...", 0.4)
                
                # Clean data
                self.analyzer.clean_data(
                    remove_duplicates=self.remove_duplicates_var.get(),
                    handle_missing=self.missing_data_var.get()
                )
                
                self.update_status("Running analysis...", 0.7)
                
                # Generate analysis
                report = self.analyzer.generate_analysis()
                
                self.update_status("Formatting results...", 0.9)
                
                # Display results
                self.display_results(report)
                
                self.update_status("Analysis completed", 1.0)
                
                # Enable export button
                self.export_button.configure(state="normal")
                
                # Switch to results tab
                self.tabview.set("Analysis Results")
                
            except Exception as e:
                self.update_status("Error in analysis", 0)
                messagebox.showerror("Error", f"Error in analysis: {str(e)}")
        
        thread = threading.Thread(target=analysis_thread)
        thread.daemon = True
        thread.start()
    
    def display_results(self, report: Dict[str, Any]):
        """Display analysis results"""
        # Clear existing results
        self.results_text.delete("1.0", "end")
        
        # Format and display results
        result_text = "🍕 RESTAURANT DATA ANALYSIS RESULTS\n"
        result_text += "=" * 50 + "\n\n"
        
        # Basic metrics
        if 'basic_metrics' in report and 'error' not in report['basic_metrics']:
            metrics = report['basic_metrics']
            result_text += "📊 BASIC METRICS:\n"
            result_text += f"  • Total Revenue: ${metrics.get('total_revenue', 0):,.2f}\n"
            result_text += f"  • Total Transactions: {metrics.get('transaction_count', 0):,}\n"
            result_text += f"  • Average Transaction: ${metrics.get('average_transaction', 0):.2f}\n"
            result_text += f"  • Largest Transaction: ${metrics.get('max_transaction', 0):.2f}\n"
            result_text += f"  • Smallest Transaction: ${metrics.get('min_transaction', 0):.2f}\n\n"
        
        # Temporal analysis
        if 'temporal_analysis' in report and 'error' not in report['temporal_analysis']:
            temporal = report['temporal_analysis']
            result_text += "⏰ TIME PATTERNS:\n"
            if 'date_range' in temporal:
                date_range = temporal['date_range']
                result_text += f"  • Date Range: {date_range.get('start')} to {date_range.get('end')}\n"
                result_text += f"  • Total Days: {date_range.get('total_days', 0)}\n"
            
            if 'hourly_sales' in temporal:
                hourly = temporal['hourly_sales']
                if 'sum' in hourly:
                    best_hour = max(hourly['sum'].items(), key=lambda x: x[1])
                    result_text += f"  • Peak Hour: {best_hour[0]}:00 (${best_hour[1]:,.2f})\n"
            
            if 'daily_sales' in temporal:
                daily = temporal['daily_sales']
                if 'sum' in daily:
                    best_day = max(daily['sum'].items(), key=lambda x: x[1])
                    result_text += f"  • Best Day: {best_day[0]} (${best_day[1]:,.2f})\n"
            result_text += "\n"
        
        # Item performance
        if 'item_performance' in report and 'error' not in report['item_performance']:
            items = report['item_performance']
            result_text += "🍽️ MENU PERFORMANCE:\n"
            result_text += f"  • Total Unique Items: {items.get('total_unique_items', 0)}\n"
            
            if 'most_ordered_items' in items:
                result_text += "  • Top 5 Most Ordered:\n"
                for i, (item, count) in enumerate(list(items['most_ordered_items'].items())[:5], 1):
                    result_text += f"    {i}. {item}: {count} orders\n"
            
            if 'top_revenue_items' in items:
                result_text += "  • Top 5 Revenue Generators:\n"
                for i, (item, stats) in enumerate(list(items['top_revenue_items'].items())[:5], 1):
                    revenue = stats.get('sum', 0) if isinstance(stats, dict) else stats
                    result_text += f"    {i}. {item}: ${revenue:,.2f}\n"
            result_text += "\n"
        
        # Order analysis
        if 'order_analysis' in report and 'error' not in report['order_analysis']:
            orders = report['order_analysis']
            result_text += "🛒 ORDER PATTERNS:\n"
            result_text += f"  • Total Orders: {orders.get('total_orders', 0):,}\n"
            result_text += f"  • Average Items per Order: {orders.get('average_items_per_order', 0):.1f}\n"
            result_text += f"  • Average Order Value: ${orders.get('average_order_value', 0):.2f}\n"
            result_text += f"  • Largest Order: ${orders.get('largest_order_value', 0):.2f}\n"
            result_text += f"  • Single Item Orders: {orders.get('single_item_orders', 0):,}\n\n"
        
        # Data overview
        if 'data_overview' in report:
            overview = report['data_overview']
            result_text += "📋 DATA QUALITY:\n"
            result_text += f"  • Dataset Shape: {overview.get('shape', [0, 0])[0]} rows × {overview.get('shape', [0, 0])[1]} columns\n"
            total_missing = sum(overview.get('missing_values', {}).values())
            result_text += f"  • Missing Values: {total_missing:,}\n"
            result_text += f"  • Memory Usage: {overview.get('memory_usage', 0) / 1024:.1f} KB\n"
        
        self.results_text.insert("1.0", result_text)
    
    def export_report(self):
        """Export analysis report"""
        if not hasattr(self.analyzer, 'report') or self.analyzer.report is None:
            messagebox.showerror("Error", "No analysis results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Analysis Report",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.analyzer.save_report(file_path)
                messagebox.showinfo("Success", f"Report saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    try:
        app = RestaurantAnalysisGUI()
        app.run()
    except ImportError as e:
        if "customtkinter" in str(e):
            print("CustomTkinter not installed. Installing...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
            print("Please restart the application.")
        else:
            print(f"Import error: {e}")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
