#!/usr/bin/env python3
"""
Which Wich Data Analysis Tool - Simple GUI (No Drag-Drop)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import threading
from restaurant_ai_analyzer import RestaurantDataAI

class SimpleAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Which Wich Data Analysis Tool")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.analyzer = RestaurantDataAI()
        self.current_file = None
        self.available_sheets = []
        self.setup_gui()
        
    def setup_gui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="🍽️ Which Wich Data Analysis Tool", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=10, padx=20, fill='x')
        
        # Browse button
        browse_button = tk.Button(
            file_frame,
            text="📂 Select Toast Data File",
            command=self.browse_file,
            font=("Arial", 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8
        )
        browse_button.pack(side='left')
        
        # File info label
        self.file_label = tk.Label(
            file_frame,
            text="No file selected",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.file_label.pack(side='left', padx=(10, 0))
        
        # Excel sheet selection (hidden initially)
        self.sheet_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.sheet_frame.pack(pady=5, padx=20, fill='x')
        
        self.sheet_label = tk.Label(
            self.sheet_frame,
            text="📊 Select Excel Sheet:",
            font=("Arial", 10),
            bg='#f0f0f0'
        )
        
        self.sheet_combo = ttk.Combobox(
            self.sheet_frame,
            width=30,
            state='readonly'
        )
        self.sheet_combo.bind('<<ComboboxSelected>>', self.on_sheet_selected)
        
        # Analyze button
        self.analyze_button = tk.Button(
            self.root,
            text="🧠 Analyze Data",
            command=self.analyze_current_selection,
            font=("Arial", 12),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            state='disabled'
        )
        self.analyze_button.pack(pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Results area
        results_label = tk.Label(
            self.root,
            text="📊 Analysis Results",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        results_label.pack(pady=(20, 5))
        
        self.results_text = scrolledtext.ScrolledText(
            self.root,
            height=20,
            width=100,
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.results_text.pack(pady=5, padx=20, fill='both', expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # Export button
        self.export_button = tk.Button(
            button_frame,
            text="💾 Export Analysis (JSON)",
            command=self.export_analysis,
            font=("Arial", 10),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=5,
            state='disabled'
        )
        self.export_button.pack(side='left', padx=5)
        
        # Clear button
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear Results",
            command=self.clear_results,
            font=("Arial", 10),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=5
        )
        clear_button.pack(side='left', padx=5)
        
        # Initial message
        self.log_message("🚀 Which Wich Data Analysis Tool Ready!")
        self.log_message("📁 Click 'Select Toast Data File' to begin")
        self.log_message("💡 Supports: CSV (.csv) and Excel (.xlsx, .xls) files")
        
    def browse_file(self):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Toast Data File",
            filetypes=[
                ("All Supported", "*.csv;*.xlsx;*.xls"),
                ("Excel files", "*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            file_name = os.path.basename(file_path)
            self.file_label.config(text=f"Selected: {file_name}")
            
            # Check if it's an Excel file and show sheets
            file_ext = os.path.splitext(file_path.lower())[1]
            if file_ext in ['.xlsx', '.xls']:
                self.load_excel_sheets(file_path)
            else:
                self.hide_sheet_selection()
                self.analyze_button.config(state='normal')
    
    def load_excel_sheets(self, file_path):
        """Load and display Excel sheet options"""
        try:
            import pandas as pd
            excel_file = pd.ExcelFile(file_path)
            self.available_sheets = excel_file.sheet_names
            
            # Show sheet selection
            self.sheet_label.pack(side='left')
            self.sheet_combo.pack(side='left', padx=(10, 0))
            
            # Populate combobox
            self.sheet_combo['values'] = self.available_sheets
            
            # Suggest best sheets for analysis
            suggested_sheets = [
                'All data', 'Sales by day', 'Time of day (totals)', 
                'Revenue summary', 'Menu Item', 'Sales'
            ]
            
            # Select the best default sheet
            default_sheet = None
            for suggested in suggested_sheets:
                for sheet in self.available_sheets:
                    if suggested.lower() in sheet.lower():
                        default_sheet = sheet
                        break
                if default_sheet:
                    break
            
            if not default_sheet:
                default_sheet = self.available_sheets[0]
            
            self.sheet_combo.set(default_sheet)
            self.analyze_button.config(state='normal')
            
            self.log_message(f"📊 Excel file loaded with {len(self.available_sheets)} sheets")
            self.log_message(f"💡 Recommended: '{default_sheet}' (auto-selected)")
            
        except Exception as e:
            self.log_message(f"❌ Error loading Excel sheets: {e}")
    
    def hide_sheet_selection(self):
        """Hide Excel sheet selection widgets"""
        self.sheet_label.pack_forget()
        self.sheet_combo.pack_forget()
    
    def on_sheet_selected(self, event=None):
        """Handle sheet selection change"""
        selected_sheet = self.sheet_combo.get()
        if selected_sheet:
            self.log_message(f"📋 Selected sheet: '{selected_sheet}'")
    
    def analyze_current_selection(self):
        """Analyze the currently selected file/sheet"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select a file first!")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Start analysis
        self.progress.start()
        self.analyze_button.config(state='disabled')
        
        # Determine sheet name for Excel files
        sheet_name = None
        file_ext = os.path.splitext(self.current_file.lower())[1]
        if file_ext in ['.xlsx', '.xls'] and self.sheet_combo.get():
            sheet_name = self.sheet_combo.get()
        
        # Run analysis in separate thread
        thread = threading.Thread(
            target=self.run_analysis, 
            args=(self.current_file, sheet_name)
        )
        thread.daemon = True
        thread.start()
    
    def run_analysis(self, file_path, sheet_name=None):
        """Run the analysis in a separate thread"""
        try:
            file_name = os.path.basename(file_path)
            
            if sheet_name:
                self.log_message(f"🔍 Analyzing: {file_name} (Sheet: {sheet_name})")
            else:
                self.log_message(f"🔍 Analyzing: {file_name}")
            
            # Load the data
            if sheet_name:
                success = self.analyzer.load_data(file_path, sheet_name=sheet_name)
            else:
                success = self.analyzer.load_data(file_path)
            
            if success:
                self.log_message("✅ Data loaded successfully!")
                
                # Show data overview
                rows = len(self.analyzer.data)
                cols = len(self.analyzer.data.columns)
                self.log_message(f"📋 Data Overview: {rows:,} rows, {cols} columns")
                
                # Show column mapping
                if self.analyzer.column_mapping:
                    self.log_message("\n🏷️  Detected Data Columns:")
                    for data_type, column in self.analyzer.column_mapping.items():
                        self.log_message(f"   {data_type}: {column}")
                
                # Generate insights
                self.log_message("\n🧠 Generating AI insights...")
                insights = self.analyzer.generate_ai_insights()
                
                self.log_message("\n💡 AI INSIGHTS FOR WHICH WICH:")
                for i, insight in enumerate(insights, 1):
                    self.log_message(f"   {i}. {insight}")
                
                # Sales analysis
                sales_data = self.analyzer.analyze_sales_trends()
                if 'error' not in sales_data:
                    self.log_message("\n📈 SALES ANALYSIS:")
                    self.log_message(f"   💰 Total Revenue: ${sales_data['total_revenue']:,.2f}")
                    self.log_message(f"   📅 Daily Average: ${sales_data['daily_average']:,.2f}")
                    if 'peak_hour' in sales_data:
                        self.log_message(f"   🕐 Peak Hour: {sales_data['peak_hour']}:00")
                    if 'best_day' in sales_data:
                        self.log_message(f"   📆 Best Day: {sales_data['best_day']}")
                    
                    date_range = sales_data.get('date_range', {})
                    if date_range:
                        self.log_message(f"   📅 Period: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}")
                else:
                    self.log_message(f"\n⚠️  Sales Analysis: {sales_data.get('error', 'Unknown error')}")
                
                # Menu analysis
                menu_data = self.analyzer.analyze_menu_performance()
                if 'error' not in menu_data:
                    self.log_message("\n🍖 MENU PERFORMANCE:")
                    self.log_message(f"   📋 Unique Items: {menu_data['total_unique_items']}")
                    self.log_message(f"   💵 Avg Item Price: ${menu_data['average_item_price']:.2f}")
                    
                    # Show top items
                    if menu_data.get('top_revenue_items'):
                        top_items = list(menu_data['top_revenue_items'].keys())[:3]
                        self.log_message(f"   🏆 Top Items: {', '.join(top_items)}")
                else:
                    self.log_message(f"\n⚠️  Menu Analysis: {menu_data.get('error', 'Unknown error')}")
                
                self.log_message(f"\n✅ Analysis Complete! 🎉")
                
                # Enable export button
                self.root.after(0, lambda: self.export_button.config(state='normal'))
                
            else:
                self.log_message("❌ Failed to load data file")
                
        except Exception as e:
            self.log_message(f"❌ Error during analysis: {e}")
        
        finally:
            # Stop progress bar and re-enable button
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.analyze_button.config(state='normal'))
    
    def log_message(self, message):
        """Add message to results area"""
        def update_text():
            self.results_text.insert(tk.END, message + "\n")
            self.results_text.see(tk.END)
        
        # Call from main thread
        self.root.after(0, update_text)
    
    def clear_results(self):
        """Clear the results area"""
        self.results_text.delete(1.0, tk.END)
        self.export_button.config(state='disabled')
    
    def export_analysis(self):
        """Export analysis results"""
        try:
            output_file = filedialog.asksaveasfilename(
                title="Save Analysis Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if output_file:
                self.analyzer.export_analysis(output_file)
                self.log_message(f"💾 Analysis exported to: {output_file}")
                messagebox.showinfo("Export Complete", f"Analysis saved to:\n{output_file}")
        
        except Exception as e:
            self.log_message(f"❌ Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export: {e}")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleAnalyzerGUI()
    app.run()
