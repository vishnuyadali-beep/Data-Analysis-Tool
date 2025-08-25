
#!/usr/bin/env python3
"""
Debug tool to inspect Toast data structure
"""

from restaurant_ai_analyzer import RestaurantDataAI
import pandas as pd

def debug_toast_data():
    """Debug what's actually in the Toast Excel file"""
    
    print("🔍 Toast Data Structure Inspector")
    print("=" * 50)
    
    file_path = "SalesSummary_2025-05-01_2025-05-31.xlsx"
    
    try:
        # Load Excel file and show all sheets
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names
        
        print(f"📊 Found {len(sheets)} sheets in your Toast file:")
        for i, sheet in enumerate(sheets, 1):
            print(f"   {i:2d}. {sheet}")
        
        print("\n" + "=" * 50)
        
        # Recommended sheets for analysis
        recommended = [
            "Sales by day",
            "Time of day (totals)", 
            "All data",
            "Revenue summary",
            "Net sales summary"
        ]
        
        print("🎯 RECOMMENDED SHEETS FOR ANALYSIS:")
        for rec in recommended:
            if rec in sheets:
                print(f"   ✅ {rec}")
            else:
                # Find similar sheets
                similar = [s for s in sheets if any(word in s.lower() for word in rec.lower().split())]
                if similar:
                    print(f"   📋 {rec} (Try: {similar[0]})")
                else:
                    print(f"   ❌ {rec} (not found)")
        
        print("\n" + "=" * 50)
        
        # Analyze top 5 most promising sheets
        promising_sheets = []
        for rec in recommended:
            if rec in sheets:
                promising_sheets.append(rec)
        
        # Add a few more that might be good
        for sheet in sheets:
            if any(keyword in sheet.lower() for keyword in ['sales', 'revenue', 'day', 'time']):
                if sheet not in promising_sheets:
                    promising_sheets.append(sheet)
        
        # Limit to top 5
        promising_sheets = promising_sheets[:5]
        
        print(f"📋 INSPECTING TOP {len(promising_sheets)} SHEETS:")
        
        for sheet_name in promising_sheets:
            print(f"\n--- SHEET: '{sheet_name}' ---")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"   📊 Size: {len(df)} rows × {len(df.columns)} columns")
                print(f"   📋 Columns: {list(df.columns)}")
                
                # Show first few rows
                if len(df) > 0:
                    print(f"   📄 Sample data:")
                    print(df.head(2).to_string(max_cols=6, max_colwidth=20))
                
                # Quick analysis potential
                analyzer = RestaurantDataAI()
                analyzer.data = df
                analyzer._auto_detect_columns()
                
                if analyzer.column_mapping:
                    print(f"   🏷️  AI detected: {analyzer.column_mapping}")
                else:
                    print(f"   ⚠️  No standard columns detected")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error reading sheet: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def quick_analyze_sheet(sheet_name):
    """Quick analysis of a specific sheet"""
    file_path = "SalesSummary_2025-05-01_2025-05-31.xlsx"
    
    print(f"\n🚀 QUICK ANALYSIS: '{sheet_name}'")
    print("=" * 50)
    
    analyzer = RestaurantDataAI()
    
    if analyzer.load_data(file_path, sheet_name=sheet_name):
        print("✅ Data loaded successfully!")
        
        # Show basic info
        print(f"📊 Data: {len(analyzer.data)} rows × {len(analyzer.data.columns)} columns")
        print(f"📋 Columns: {list(analyzer.data.columns)}")
        
        # Show detected mappings
        if analyzer.column_mapping:
            print(f"🏷️  AI Mappings: {analyzer.column_mapping}")
        
        # Try generating insights
        insights = analyzer.generate_ai_insights()
        print(f"\n💡 AI INSIGHTS:")
        for insight in insights:
            print(f"   • {insight}")
    else:
        print("❌ Failed to load sheet")

if __name__ == "__main__":
    # Run the debug analysis
    debug_toast_data()
    
    # Ask user which sheet to analyze
    print("\n" + "=" * 50)
    sheet_choice = input("🎯 Enter sheet name to analyze (or press Enter to skip): ").strip()
    
    if sheet_choice:
        quick_analyze_sheet(sheet_choice)
    
    print("\n✅ Debug complete!")
