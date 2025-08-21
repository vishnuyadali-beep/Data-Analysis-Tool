#!/usr/bin/env python3
"""
Test the Restaurant AI Analyzer with real Toast data (CSV or Excel)
"""

from restaurant_ai_analyzer import RestaurantDataAI
import os

def main():
    # Initialize the AI analyzer
    analyzer = RestaurantDataAI()
    
    # Get file from user
    print("🍽️  Which Wich Data Analysis Tool")
    print("Supports: CSV (.csv) and Excel (.xlsx, .xls) files")
    print()
    
    csv_file = input("Enter your Toast data filename: ")
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ File '{csv_file}' not found. Make sure the file is in your current directory.")
        return
    
    print(f"\n🔍 Loading {csv_file}...")
    
    # Detect file type and handle accordingly
    file_ext = os.path.splitext(csv_file.lower())[1]
    
    if file_ext in ['.xlsx', '.xls']:
        # For Excel files, check if user wants to specify a sheet
        import pandas as pd
        try:
            excel_file = pd.ExcelFile(csv_file)
            sheet_names = excel_file.sheet_names
            print(f"📊 Available sheets: {sheet_names}")
            
            if len(sheet_names) > 1:
                sheet_choice = input(f"Enter sheet name (or press Enter for '{sheet_names[0]}'): ").strip()
                sheet_name = sheet_choice if sheet_choice else sheet_names[0]
            else:
                sheet_name = sheet_names[0]
            
            # Load with specific sheet
            success = analyzer.load_data(csv_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            return
    else:
        # Load CSV or other formats
        success = analyzer.load_data(csv_file)
    
    if success:
        print("\n📊 Data loaded successfully!")
        
        # Show basic info about the data
        print(f"\n📋 DATA OVERVIEW:")
        print(f"Rows: {len(analyzer.data):,}")
        print(f"Columns: {len(analyzer.data.columns)}")
        
        # Show first few rows to verify
        print(f"\n📄 First 3 rows:")
        print(analyzer.data.head(3).to_string())
        
        print(f"\n🏷️  All columns: {list(analyzer.data.columns)}")
        
        # Generate AI insights
        print("\n🧠 Generating AI insights...")
        insights = analyzer.generate_ai_insights()
        
        print(f"\n💡 AI INSIGHTS FOR WHICH WICH:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        # Export full analysis
        print(f"\n📤 Exporting detailed analysis...")
        results = analyzer.export_analysis("which_wich_analysis.json")
        
        print(f"\n✅ Analysis complete! Check 'which_wich_analysis.json' for full results.")
        
        # Show detailed sales summary if available
        sales_data = analyzer.analyze_sales_trends()
        if 'error' not in sales_data:
            print(f"\n📈 DETAILED SALES SUMMARY:")
            print(f"   💰 Total Revenue: ${sales_data['total_revenue']:,.2f}")
            print(f"   📅 Daily Average: ${sales_data['daily_average']:,.2f}")
            print(f"   🕐 Peak Hour: {sales_data['peak_hour']}:00 (${sales_data['peak_hour_sales']:,.2f})")
            print(f"   📆 Best Day: {sales_data['best_day']} (${sales_data['best_day_average']:,.2f})")
            print(f"   📊 Date Range: {sales_data['date_range']['start']} to {sales_data['date_range']['end']}")
        
        # Show menu performance
        menu_data = analyzer.analyze_menu_performance() 
        if 'error' not in menu_data:
            print(f"\n🍖 MENU PERFORMANCE:")
            print(f"   📋 Total Menu Items: {menu_data['total_unique_items']}")
            print(f"   💵 Average Item Price: ${menu_data['average_item_price']:.2f}")
            
            if menu_data['top_revenue_items']:
                top_item = list(menu_data['top_revenue_items'].keys())[0]
                print(f"   🏆 Top Revenue Item: '{top_item}'")
        
    else:
        print("❌ Failed to load data file. Check the filename and format.")
        print("Supported formats: .csv, .xlsx, .xls")

if __name__ == "__main__":
    main()