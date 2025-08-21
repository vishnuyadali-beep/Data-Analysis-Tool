import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Any
import re
from collections import defaultdict
import os

class RestaurantDataAI:
    def __init__(self):
        self.data = None
        self.column_mapping = {}
        self.insights = {}
        
    def load_data(self, file_path: str, sheet_name: str = None) -> bool:
        """Load and initially process CSV or Excel file"""
        try:
            # Get file extension
            file_ext = os.path.splitext(file_path.lower())[1]
            
            if file_ext == '.csv':
                self.data = pd.read_csv(file_path)
                print(f"📄 Loaded CSV: {len(self.data)} records from {file_path}")
                
            elif file_ext in ['.xlsx', '.xls']:
                # Handle Excel files
                if sheet_name:
                    self.data = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"📊 Loaded Excel sheet '{sheet_name}': {len(self.data)} records from {file_path}")
                else:
                    # Load first sheet by default, but show available sheets
                    excel_file = pd.ExcelFile(file_path)
                    sheet_names = excel_file.sheet_names
                    print(f"📊 Available Excel sheets: {sheet_names}")
                    
                    self.data = pd.read_excel(file_path, sheet_name=sheet_names[0])
                    print(f"📊 Loaded Excel sheet '{sheet_names[0]}': {len(self.data)} records from {file_path}")
                    
                    if len(sheet_names) > 1:
                        print(f"💡 Tip: Use load_data('{file_path}', sheet_name='SheetName') to load a specific sheet")
            
            else:
                print(f"❌ Unsupported file format: {file_ext}")
                print("Supported formats: .csv, .xlsx, .xls")
                return False
            
            self._auto_detect_columns()
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    # Keep the old method for backward compatibility
    def load_csv(self, file_path: str) -> bool:
        """Legacy method - use load_data() instead"""
        return self.load_data(file_path)
    
    def _auto_detect_columns(self):
        """AI-powered column detection for restaurant data"""
        columns = self.data.columns.str.lower()
        
        # Common Toast/POS column patterns
        patterns = {
            'date': ['date', 'time', 'created', 'order_date', 'timestamp'],
            'item_name': ['item', 'product', 'menu', 'name', 'description'],
            'price': ['price', 'amount', 'total', 'cost', 'revenue'],
            'quantity': ['qty', 'quantity', 'count', 'units'],
            'category': ['category', 'type', 'group', 'section'],
            'payment': ['payment', 'method', 'card', 'cash'],
            'employee': ['employee', 'staff', 'server', 'cashier'],
            'order_id': ['order', 'ticket', 'transaction', 'id'],
            'customer': ['customer', 'guest', 'phone', 'email']
        }
        
        for data_type, keywords in patterns.items():
            for col in columns:
                if any(keyword in col for keyword in keywords):
                    self.column_mapping[data_type] = self.data.columns[columns.get_loc(col)]
                    break
        
        print("Detected columns:")
        for key, value in self.column_mapping.items():
            print(f"  {key}: {value}")
    
    def analyze_sales_trends(self) -> Dict[str, Any]:
        """Analyze temporal sales patterns"""
        if 'date' not in self.column_mapping or 'price' not in self.column_mapping:
            return {"error": "Missing date or price columns"}
        
        try:
            # Convert date column to datetime
            date_col = self.column_mapping['date']
            price_col = self.column_mapping['price']
            
            df = self.data.copy()
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # Daily sales trends
            daily_sales = df.groupby(df[date_col].dt.date)[price_col].sum()
            
            # Hourly patterns
            hourly_sales = df.groupby(df[date_col].dt.hour)[price_col].sum()
            peak_hour = hourly_sales.idxmax()
            
            # Weekly patterns  
            weekly_sales = df.groupby(df[date_col].dt.day_name())[price_col].sum()
            best_day = weekly_sales.idxmax()
            
            return {
                'daily_average': float(daily_sales.mean()),
                'peak_hour': int(peak_hour),
                'peak_hour_sales': float(hourly_sales[peak_hour]),
                'best_day': best_day,
                'best_day_average': float(weekly_sales[best_day]),
                'total_revenue': float(df[price_col].sum()),
                'date_range': {
                    'start': str(daily_sales.index.min()),
                    'end': str(daily_sales.index.max())
                }
            }
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def analyze_menu_performance(self) -> Dict[str, Any]:
        """Analyze which menu items are performing best/worst"""
        if 'item_name' not in self.column_mapping or 'price' not in self.column_mapping:
            return {"error": "Missing item name or price columns"}
        
        try:
            item_col = self.column_mapping['item_name']
            price_col = self.column_mapping['price']
            qty_col = self.column_mapping.get('quantity', None)
            
            df = self.data.copy()
            
            # Group by item
            if qty_col and qty_col in df.columns:
                item_stats = df.groupby(item_col).agg({
                    price_col: ['sum', 'mean', 'count'],
                    qty_col: 'sum'
                }).round(2)
            else:
                item_stats = df.groupby(item_col).agg({
                    price_col: ['sum', 'mean', 'count']
                }).round(2)
            
            # Flatten column names
            item_stats.columns = ['_'.join(col).strip() for col in item_stats.columns]
            
            # Top performers
            top_revenue = item_stats.nlargest(5, f'{price_col}_sum')
            top_frequency = item_stats.nlargest(5, f'{price_col}_count')
            
            return {
                'top_revenue_items': top_revenue.to_dict('index'),
                'most_ordered_items': top_frequency.to_dict('index'),
                'total_unique_items': len(item_stats),
                'average_item_price': float(df[price_col].mean())
            }
        except Exception as e:
            return {"error": f"Menu analysis failed: {e}"}
    
    def generate_ai_insights(self) -> List[str]:
        """Generate intelligent insights based on the data"""
        insights = []
        
        # Analyze sales trends
        sales_data = self.analyze_sales_trends()
        if 'error' not in sales_data:
            insights.append(f"Peak sales hour is {sales_data['peak_hour']}:00 with ${sales_data['peak_hour_sales']:.2f} in revenue")
            insights.append(f"{sales_data['best_day']} is your strongest day with an average of ${sales_data['best_day_average']:.2f}")
            insights.append(f"Daily average revenue: ${sales_data['daily_average']:.2f}")
        
        # Analyze menu performance
        menu_data = self.analyze_menu_performance()
        if 'error' not in menu_data:
            top_item = list(menu_data['top_revenue_items'].keys())[0]
            insights.append(f"'{top_item}' is your top revenue generator")
            insights.append(f"You have {menu_data['total_unique_items']} unique menu items")
        
        # Data quality insights
        if self.data is not None:
            total_records = len(self.data)
            insights.append(f"Dataset contains {total_records} transaction records")
            
            # Check for missing data
            missing_data = self.data.isnull().sum().sum()
            if missing_data > 0:
                insights.append(f"Warning: {missing_data} missing data points detected")
        
        return insights
    
    def export_analysis(self, output_file: str = "analysis_results.json"):
        """Export all analysis results to JSON for C++ frontend"""
        results = {
            'column_mapping': self.column_mapping,
            'sales_trends': self.analyze_sales_trends(),
            'menu_performance': self.analyze_menu_performance(),
            'ai_insights': self.generate_ai_insights(),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Analysis exported to {output_file}")
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the AI analyzer
    analyzer = RestaurantDataAI()
    
    # Example of how to use it
    # print("Restaurant Data Analysis AI - Ready")
    # print("Supports: CSV (.csv) and Excel (.xlsx, .xls) files")
    # print("Usage:")
    # print("1. analyzer.load_data('your_toast_data.csv')  # For CSV")
    # print("   analyzer.load_data('your_toast_data.xlsx') # For Excel")  
    # print("   analyzer.load_data('data.xlsx', sheet_name='Sales') # Specific sheet")
    # print("2. insights = analyzer.generate_ai_insights()")
    # print("3. analyzer.export_analysis('results.json')")
    
    # # If you have a sample file, uncomment and modify:
    # analyzer.load_data("sample_toast_data.csv")  # For CSV
    # analyzer.load_data("sample_toast_data.xlsx") # For Excel  
    # analyzer.load_data("sample_toast_data.xlsx", sheet_name="Sales") # Specific Excel sheet
    # insights = analyzer.generate_ai_insights()
    # for insight in insights:
    #     print(f"💡 {insight}")