import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Any, Optional
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ColumnMapping:
    """Define the expected data structure"""
    date: Optional[str] = None
    item_name: Optional[str] = None
    price: Optional[str] = None
    quantity: Optional[str] = None
    category: Optional[str] = None
    order_id: Optional[str] = None
    employee: Optional[str] = None
    payment_method: Optional[str] = None
    customer_id: Optional[str] = None
    tax: Optional[str] = None
    discount: Optional[str] = None
    tip: Optional[str] = None
    cost: Optional[str] = None

class DataLoader:
    """Handle loading and initial processing of restaurant data"""
    
    @staticmethod
    def load_file(file_path: str, sheet_name: str = None) -> pd.DataFrame:
        """Load CSV or Excel file with proper error handling"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.csv':
            # Try different encodings for CSV
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print(f"✅ Loaded CSV with {encoding} encoding: {len(df)} rows")
                    return df
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not read CSV with any encoding")
            
        elif file_ext in ['.xlsx', '.xls']:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"✅ Loaded Excel sheet '{sheet_name}': {len(df)} rows")
            else:
                # Show available sheets and load first one
                excel_file = pd.ExcelFile(file_path)
                print(f"📋 Available sheets: {excel_file.sheet_names}")
                df = pd.read_excel(file_path, sheet_name=excel_file.sheet_names[0])
                print(f"✅ Loaded sheet '{excel_file.sheet_names[0]}': {len(df)} rows")
            return df
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    @staticmethod
    def inspect_data(df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data overview"""
        return {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'sample_data': df.head().to_dict('records'),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'date_like_columns': [col for col in df.columns if any(keyword in col.lower() 
                                 for keyword in ['date', 'time', 'created', 'timestamp'])]
        }

class DataCleaner:
    """Handle data cleaning and standardization"""
    
    @staticmethod
    def clean_currency_column(series: pd.Series) -> pd.Series:
        """Clean currency columns (remove $, commas, etc.)"""
        if series.dtype == 'object':
            # Remove currency symbols and convert to float
            cleaned = series.str.replace(r'[\$,]', '', regex=True)
            return pd.to_numeric(cleaned, errors='coerce')
        return series
    
    @staticmethod
    def clean_date_column(series: pd.Series) -> pd.Series:
        """Standardize date formats"""
        return pd.to_datetime(series, errors='coerce')
    
    @staticmethod
    def clean_text_column(series: pd.Series) -> pd.Series:
        """Clean text data"""
        return series.str.strip().str.title()
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        before_count = len(df)
        df_cleaned = df.drop_duplicates(subset=subset)
        removed_count = before_count - len(df_cleaned)
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} duplicate rows")
        return df_cleaned
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'report') -> pd.DataFrame:
        """Handle missing values based on strategy"""
        missing_summary = df.isnull().sum()
        missing_pct = (missing_summary / len(df) * 100).round(2)
        
        print("Missing Values Summary:")
        for col, count in missing_summary.items():
            if count > 0:
                print(f"  {col}: {count} ({missing_pct[col]}%)")
        
        if strategy == 'drop_rows':
            return df.dropna()
        elif strategy == 'drop_cols':
            return df.dropna(axis=1)
        else:  # report only
            return df

class ColumnMapper:
    """Handle column mapping and detection"""
    
    DETECTION_PATTERNS = {
        'date': ['date', 'time', 'created', 'order_date', 'timestamp', 'datetime', 'closed'],
        'item_name': ['item', 'product', 'menu', 'name', 'description', 'dish', 'food'],
        'price': ['price', 'amount', 'total', 'cost', 'revenue', 'value', 'sales', 'gross'],
        'quantity': ['qty', 'quantity', 'count', 'units', 'sold', 'ordered'],
        'category': ['category', 'type', 'group', 'section', 'class', 'department'],
        'payment_method': ['payment', 'method', 'card', 'cash', 'tender'],
        'employee': ['employee', 'staff', 'server', 'cashier', 'user', 'waiter'],
        'order_id': ['order', 'ticket', 'transaction', 'id', 'receipt', 'check'],
        'customer_id': ['customer', 'guest', 'phone', 'email', 'client'],
        'tax': ['tax', 'gst', 'vat', 'sales_tax'],
        'discount': ['discount', 'promo', 'coupon', 'comp'],
        'tip': ['tip', 'gratuity', 'service'],
        'cost': ['cost', 'cogs', 'ingredient_cost']
    }
    
    @classmethod
    def auto_detect_columns(cls, df: pd.DataFrame) -> ColumnMapping:
        """Automatically detect column mappings"""
        columns_lower = df.columns.str.lower().str.strip()
        mapping = ColumnMapping()
        
        for field_name, keywords in cls.DETECTION_PATTERNS.items():
            for col_lower in columns_lower:
                if any(keyword in col_lower for keyword in keywords):
                    original_col = df.columns[columns_lower.get_loc(col_lower)]
                    setattr(mapping, field_name, original_col)
                    break
        
        return mapping
    
    @staticmethod
    def create_manual_mapping(**kwargs) -> ColumnMapping:
        """Create manual column mapping"""
        return ColumnMapping(**kwargs)
    
    @staticmethod
    def validate_mapping(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, bool]:
        """Validate that mapped columns exist in dataframe"""
        validation = {}
        for field_name, column_name in mapping.__dict__.items():
            if column_name is not None:
                validation[field_name] = column_name in df.columns
        return validation

class SalesAnalyzer:
    """Core sales analysis functionality"""
    
    @staticmethod
    def calculate_basic_metrics(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, Any]:
        """Calculate fundamental sales metrics"""
        if not mapping.price:
            return {"error": "Price column required"}
        
        price_series = DataCleaner.clean_currency_column(df[mapping.price])
        
        return {
            'total_revenue': float(price_series.sum()),
            'transaction_count': len(df),
            'average_transaction': float(price_series.mean()),
            'median_transaction': float(price_series.median()),
            'max_transaction': float(price_series.max()),
            'min_transaction': float(price_series.min()),
            'std_transaction': float(price_series.std())
        }
    
    @staticmethod
    def analyze_temporal_patterns(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, Any]:
        """Analyze sales patterns over time"""
        if not mapping.date or not mapping.price:
            return {"error": "Date and price columns required"}
        
        df_temp = df.copy()
        df_temp['clean_date'] = DataCleaner.clean_date_column(df_temp[mapping.date])
        df_temp['clean_price'] = DataCleaner.clean_currency_column(df_temp[mapping.price])
        
        # Remove invalid dates/prices
        df_temp = df_temp.dropna(subset=['clean_date', 'clean_price'])
        
        # Extract time components
        df_temp['hour'] = df_temp['clean_date'].dt.hour
        df_temp['day_of_week'] = df_temp['clean_date'].dt.day_name()
        df_temp['date_only'] = df_temp['clean_date'].dt.date
        df_temp['month'] = df_temp['clean_date'].dt.to_period('M')
        
        return {
            'date_range': {
                'start': str(df_temp['date_only'].min()),
                'end': str(df_temp['date_only'].max()),
                'total_days': (df_temp['date_only'].max() - df_temp['date_only'].min()).days
            },
            'hourly_sales': df_temp.groupby('hour')['clean_price'].agg(['sum', 'count', 'mean']).round(2).to_dict(),
            'daily_sales': df_temp.groupby('day_of_week')['clean_price'].agg(['sum', 'count', 'mean']).round(2).to_dict(),
            'daily_totals': df_temp.groupby('date_only')['clean_price'].sum().round(2).to_dict()
        }
    
    @staticmethod
    def analyze_item_performance(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, Any]:
        """Analyze individual item performance"""
        if not mapping.item_name:
            return {"error": "Item name column required"}
        
        df_temp = df.copy()
        df_temp['clean_item'] = DataCleaner.clean_text_column(df_temp[mapping.item_name])
        
        # Basic item stats
        item_counts = df_temp['clean_item'].value_counts()
        
        result = {
            'total_unique_items': len(item_counts),
            'most_ordered_items': item_counts.head(10).to_dict(),
            'item_frequency_distribution': {
                'ordered_once': (item_counts == 1).sum(),
                'ordered_2_5_times': ((item_counts >= 2) & (item_counts <= 5)).sum(),
                'ordered_more_than_5': (item_counts > 5).sum()
            }
        }
        
        # Add revenue analysis if price column available
        if mapping.price:
            df_temp['clean_price'] = DataCleaner.clean_currency_column(df_temp[mapping.price])
            item_revenue = df_temp.groupby('clean_item')['clean_price'].agg(['sum', 'mean', 'count']).round(2)
            result['top_revenue_items'] = item_revenue.nlargest(10, 'sum').to_dict('index')
            result['highest_avg_price_items'] = item_revenue.nlargest(10, 'mean').to_dict('index')
        
        return result

class OrderAnalyzer:
    """Analyze order-level patterns"""
    
    @staticmethod
    def analyze_order_composition(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, Any]:
        """Analyze what makes up typical orders"""
        if not mapping.order_id:
            return {"error": "Order ID column required"}
        
        df_temp = df.copy()
        
        # Order-level aggregations
        agg_dict = {}
        if mapping.price:
            agg_dict[mapping.price] = ['sum', 'count']
        else:
            agg_dict[mapping.item_name] = 'count'
        
        order_stats = df_temp.groupby(mapping.order_id).agg(agg_dict).round(2)
        
        # Flatten column names
        order_stats.columns = ['_'.join(col).strip() for col in order_stats.columns]
        
        if mapping.price:
            price_col = f"{mapping.price}_sum"
            items_col = f"{mapping.price}_count"
        else:
            price_col = None
            items_col = f"{mapping.item_name}_count"
        
        result = {
            'total_orders': len(order_stats),
            'average_items_per_order': float(order_stats[items_col].mean()),
            'median_items_per_order': float(order_stats[items_col].median()),
            'max_items_in_order': int(order_stats[items_col].max()),
            'single_item_orders': int((order_stats[items_col] == 1).sum())
        }
        
        if price_col:
            result.update({
                'average_order_value': float(order_stats[price_col].mean()),
                'median_order_value': float(order_stats[price_col].median()),
                'largest_order_value': float(order_stats[price_col].max())
            })
        
        return result

class ReportGenerator:
    """Generate comprehensive reports"""
    
    @staticmethod
    def generate_summary_report(df: pd.DataFrame, mapping: ColumnMapping) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        
        report = {
            'data_overview': DataLoader.inspect_data(df),
            'column_mapping': mapping.__dict__,
            'basic_metrics': SalesAnalyzer.calculate_basic_metrics(df, mapping),
            'temporal_analysis': SalesAnalyzer.analyze_temporal_patterns(df, mapping),
            'item_performance': SalesAnalyzer.analyze_item_performance(df, mapping),
            'order_analysis': OrderAnalyzer.analyze_order_composition(df, mapping),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    @staticmethod
    def save_report(report: Dict[str, Any], output_path: str = "restaurant_analysis_report.json"):
        """Save report to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Report saved to {output_path}")

# Main analysis class that ties everything together
class RestaurantDataAnalyzer:
    """Main class for restaurant data analysis"""
    
    def __init__(self):
        self.data = None
        self.mapping = None
        self.report = None
    
    def load_data(self, file_path: str, sheet_name: str = None) -> bool:
        """Load data from file"""
        try:
            self.data = DataLoader.load_file(file_path, sheet_name)
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def inspect_data(self) -> Dict[str, Any]:
        """Inspect the loaded data"""
        if self.data is None:
            return {"error": "No data loaded"}
        return DataLoader.inspect_data(self.data)
    
    def auto_map_columns(self) -> ColumnMapping:
        """Automatically detect column mappings"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        self.mapping = ColumnMapper.auto_detect_columns(self.data)
        
        print("🔍 Auto-detected columns:")
        for field, column in self.mapping.__dict__.items():
            if column:
                print(f"  {field}: {column}")
        
        # Validate mapping
        validation = ColumnMapper.validate_mapping(self.data, self.mapping)
        invalid_mappings = [field for field, valid in validation.items() if not valid]
        if invalid_mappings:
            print(f"⚠️  Invalid mappings: {invalid_mappings}")
        
        return self.mapping
    
    def set_column_mapping(self, **kwargs) -> ColumnMapping:
        """Manually set column mappings"""
        self.mapping = ColumnMapper.create_manual_mapping(**kwargs)
        print("✅ Manual column mapping set")
        return self.mapping
    
    def clean_data(self, remove_duplicates: bool = True, handle_missing: str = 'report') -> pd.DataFrame:
        """Clean the data"""
        if self.data is None:
            print("❌ No data loaded")
            return None
        
        cleaned_data = self.data.copy()
        
        if remove_duplicates:
            cleaned_data = DataCleaner.remove_duplicates(cleaned_data)
        
        cleaned_data = DataCleaner.handle_missing_values(cleaned_data, handle_missing)
        
        self.data = cleaned_data
        return cleaned_data
    
    def generate_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis"""
        if self.data is None or self.mapping is None:
            return {"error": "Data and column mapping required"}
        
        self.report = ReportGenerator.generate_summary_report(self.data, self.mapping)
        return self.report
    
    def save_report(self, output_path: str = "restaurant_analysis_report.json"):
        """Save analysis report"""
        if self.report is None:
            print("❌ No report generated yet")
            return
        
        ReportGenerator.save_report(self.report, output_path)

# Example usage
if __name__ == "__main__":
    print("🍕 Restaurant Data Analysis Foundation")
    print("="*50)
    
    # Example workflow
    analyzer = RestaurantDataAnalyzer()
    
    print("\nExample workflow:")
    print("1. analyzer.load_data('your_data.csv')")
    print("2. analyzer.inspect_data()  # See what your data looks like")
    print("3. analyzer.auto_map_columns()  # Auto-detect columns")
    print("4. analyzer.set_column_mapping(date='Order Date', price='Total')  # Manual mapping if needed")
    print("5. analyzer.clean_data()  # Clean the data") 
    print("6. analyzer.generate_analysis()  # Run analysis")
    print("7. analyzer.save_report()  # Save results")