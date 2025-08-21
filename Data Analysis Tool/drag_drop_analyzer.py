#!/usr/bin/env python3
"""
Which Wich Data Analysis Tool - Drag & Drop GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import threading
from restaurant_ai_analyzer import RestaurantDataAI

class DragDropAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Which Wich Data Analysis Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.analyzer = RestaurantDataAI()
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
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root, 
            text="Drag & Drop your CSV or Excel files here", 
            font=("Arial", 12),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=5)
        
        # Drag and Drop Zone
        self.drop_frame = tk.Frame(
            self.root,
            bg='#ecf0f1',
            relief='ridge',
            bd=2,
            height=150
        )
        self.drop_frame.pack(pady=20, padx=20, fill='x')
        self.drop_frame.pack_propagate(False)
        
        # Drop zone label
        self.drop_label = tk.Label(
            self.drop_frame,
            text="📁 Drop your Toast data file here\n\nSupported formats: .csv, .xlsx, .xls\n\nOr click 'Browse Files' below",
            font=("Arial", 11),
            bg='#ecf0f1',
            fg='#34495e',
            justify='center'
        )
        self.drop_label.pack(expand=True)
        
        # Make the drop zone clickable
        self.drop_frame.bind("<Button-1>", self.browse_file)
        self.drop_label.bind("<Button-1>", self.browse_file)
        
        # Enable drag and drop (works on Windows)
        self.drop_frame.drop_target_register('DND_Files')
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Browse button
        browse_button = tk.Button(
            self.root,
            text="📂 Browse Files",
            command=self.browse_file,
            font=("Arial", 10),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=5
        )
        browse_button.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=300
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
            height=15,
            width=90,
            font=("Consolas", 9),
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.results_text.pack(pady=5, padx=20, fill='both', expand=True)
        
        # Export button
        self.export_button = tk.Button(
            self.root,
            text="💾 Export Analysis (JSON)",
            command=self.export_analysis,
            font=("Arial", 10),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            state='disabled'
        )
        self.export_button.pack(pady=10)
        
        # Initial message
        self.log_message("🚀 Ready to analyze your Toast data!")
        self.log_message("💡 Tip: Drag and drop your CSV or Excel file onto the drop zone above")
        
    def handle_drop(self, event):
        """Handle drag and drop files"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]  # Take the first file
                self.analyze_file(file_path)
        except Exception as e:
            self.log_message(f"❌ Error handling dropped file: {e}")
    
    def browse_file(self, event=None):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Toast Data File",
            filetypes=[
                ("All Supported", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.analyze_file(file_path)
    
    def analyze_file(self, file_path):
        """Analyze the selected file"""
        if not os.path.exists(file_path):
            self.log_message(f"❌ File not found: {file_path}")
            return
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Update drop zone
        file_name = os.path.basename(file_path)
        self.drop_label.config(text=f"📄 Analyzing: {file_name}\n\nPlease wait...")
        
        # Start progress bar
        self.progress.start()
        
        # Run analysis in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self.run_analysis, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def run_analysis(self, file_path):
        """Run the analysis in a separate thread"""
        try:
            file_name = os.path.basename(file_path)
            self.log_message(f"🔍 Loading {file_name}...")
            
            # Load the data
            file_ext = os.path.splitext(file_path.lower())[1]
            
            if file_ext in ['.xlsx', '.xls']:
                # Handle Excel files
                import pandas as pd
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                if len(sheet_names) > 1:
                    # Use first sheet for now - could add sheet selection later
                    sheet_name = sheet_names[0]
                    self.log_message(f"📊 Using sheet: {sheet_name}")
                    success = self.analyzer.load_data(file_path, sheet_name=sheet_name)
                else:
                    success = self.analyzer.load_data(file_path)
            else:
                success = self.analyzer.load_data(file_path)
            
            if success:
                self.log_message("✅ Data loaded successfully!")
                
                # Show data overview
                rows = len(self.analyzer.data)
                cols = len(self.analyzer.data.columns)
                self.log_message(f"📋 Data Overview: {rows:,} rows, {cols} columns")
                
                # Generate insights
                self.log_message("🧠 Generating AI insights...")
                insights = self.analyzer.generate_ai_insights()
                
                self.log_message("\n💡 AI INSIGHTS FOR WHICH WICH:")
                for i, insight in enumerate(insights, 1):
                    self.log_message(f"   {i}. {insight}")
                
                # Sales analysis
                sales_data = self.analyzer.analyze_sales_trends()
                if 'error' not in sales_data:
                    self.log_message("\n📈 SALES SUMMARY:")
                    self.log_message(f"   💰 Total Revenue: ${sales_data['total_revenue']:,.2f}")
                    self.log_message(f"   📅 Daily Average: ${sales_data['daily_average']:,.2f}")
                    self.log_message(f"   🕐 Peak Hour: {sales_data['peak_hour']}:00")
                    self.log_message(f"   📆 Best Day: {sales_data['best_day']}")
                
                # Menu analysis
                menu_data = self.analyzer.analyze_menu_performance()
                if 'error' not in menu_data:
                    self.log_message("\n🍖 MENU PERFORMANCE:")
                    self.log_message(f"   📋 Unique Items: {menu_data['total_unique_items']}")
                    self.log_message(f"   💵 Avg Item Price: ${menu_data['average_item_price']:.2f}")
                
                self.log_message(f"\n✅ Analysis complete!")
                
                # Enable export button
                self.export_button.config(state='normal')
                
                # Update drop zone
                self.root.after(0, lambda: self.drop_label.config(
                    text=f"✅ Analysis Complete!\n\n{file_name}\n\nDrop another file to analyze again"
                ))
                
            else:
                self.log_message("❌ Failed to load data file")
                
        except Exception as e:
            self.log_message(f"❌ Error during analysis: {e}")
        
        finally:
            # Stop progress bar
            self.root.after(0, self.progress.stop)
    
    def log_message(self, message):
        """Add message to results area"""
        def update_text():
            self.results_text.insert(tk.END, message + "\n")
            self.results_text.see(tk.END)
        
        # Call from main thread
        self.root.after(0, update_text)
    
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

# Fallback for systems without drag-and-drop support
def setup_drag_drop_fallback():
    """Set up basic drag and drop support"""
    try:
        # Try to enable basic file drop support
        import tkinter.dnd as dnd
        return True
    except:
        return False

if __name__ == "__main__":
    try:
        app = DragDropAnalyzer()
        app.run()
    except Exception as e:
        print(f"GUI Error: {e}")
        print("Falling back to command line version...")
        
        # Fallback to file browser
        from tkinter import filedialog
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        file_path = filedialog.askopenfilename(
            title="Select Toast Data File",
            filetypes=[
                ("All Supported", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls")
            ]
        )
        
        if file_path:
            from restaurant_ai_analyzer import RestaurantDataAI
            analyzer = RestaurantDataAI()
            if analyzer.load_data(file_path):
                insights = analyzer.generate_ai_insights()
                for insight in insights:
                    print(f"💡 {insight}")
                analyzer.export_analysis("analysis_results.json")
                print("✅ Analysis exported to analysis_results.json")
