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
        self.data_type = "unknown"  # transaction, summary, or mixed
        
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
            self._determine_data_type()
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    # Keep the old method for backward compatibility
    def load_csv(self, file_path: str) -> bool:
        """Legacy method - use load_data() instead"""
        return self.load_data(file_path)
    
    def _determine_data_type(self):
        """Determine if this is transaction-level data or summary data"""
        if self.data is None:
            return
            
        # Look for clues in column names and data patterns
        columns_lower = [col.lower() for col in self.data.columns]
        
        # Summary data indicators
        summary_indicators = ['total', 'sum', 'average', 'count', 'daily', 'weekly', 'monthly']
        transaction_indicators = ['order_id', 'transaction_id', 'timestamp', 'receipt']
        
        summary_score = sum(1 for col in columns_lower if any(indicator in col for indicator in summary_indicators))
        transaction_score = sum(1 for col in columns_lower if any(indicator in col for indicator in transaction_indicators))
        
        if summary_score > transaction_score:
            self.data_type = "summary"
        elif transaction_score > summary_score:
            self.data_type = "transaction"
        else:
            self.data_type = "mixed"
            
        print(f"🔍 Data type detected: {self.data_type}")
    
    def _auto_detect_columns(self):
        """Enhanced AI-powered column detection for restaurant data"""
        columns = self.data.columns.str.lower()
        
        # Enhanced patterns with more variations
        patterns = {
            'date': ['date', 'time', 'created', 'order_date', 'timestamp', 'day', 'week', 'month'],
            'item_name': ['item', 'product', 'menu', 'name', 'description', 'dish'],
            'price': ['price', 'amount', 'total', 'cost', 'revenue', 'sales', 'value'],
            'quantity': ['qty', 'quantity', 'count', 'units', 'orders', 'sold'],
            'category': ['category', 'type', 'group', 'section', 'department'],
            'payment': ['payment', 'method', 'card', 'cash', 'tender'],
            'employee': ['employee', 'staff', 'server', 'cashier', 'waiter'],
            'order_id': ['order', 'ticket', 'transaction', 'receipt', 'id'],
            'customer': ['customer', 'guest', 'phone', 'email', 'patron']
        }
        
        for data_type, keywords in patterns.items():
            for col in columns:
                if any(keyword in col for keyword in keywords):
                    self.column_mapping[data_type] = self.data.columns[columns.get_loc(col)]
                    break
        
        print("Detected columns:")
        for key, value in self.column_mapping.items():
            print(f"  {key}: {value}")
    
    def analyze_data_quality(self) -> Dict[str, Any]:
        """Analyze data quality and provide insights"""
        if self.data is None:
            return {"error": "No data loaded"}
            
        try:
            total_rows = len(self.data)
            total_cols = len(self.data.columns)
            
            # Missing data analysis
            missing_data = self.data.isnull().sum()
            missing_percentage = (missing_data / total_rows * 100).round(2)
            
            # Duplicate analysis
            duplicates = self.data.duplicated().sum()
            
            # Data types
            data_types = self.data.dtypes.to_dict()
            
            # Numeric columns analysis
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
            
            quality_score = 100
            issues = []
            
            if duplicates > 0:
                quality_score -= min(20, duplicates / total_rows * 100)
                issues.append(f"{duplicates} duplicate records found")
                
            if missing_data.sum() > 0:
                missing_ratio = missing_data.sum() / (total_rows * total_cols)
                quality_score -= min(30, missing_ratio * 100)
                issues.append(f"{missing_data.sum()} missing values across dataset")
            
            return {
                'total_records': total_rows,
                'total_columns': total_cols,
                'missing_data': missing_data.to_dict(),
                'missing_percentage': missing_percentage.to_dict(),
                'duplicates': int(duplicates),
                'quality_score': max(0, round(quality_score, 1)),
                'issues': issues,
                'numeric_columns': numeric_cols,
                'data_types': {k: str(v) for k, v in data_types.items()}
            }
        except Exception as e:
            return {"error": f"Data quality analysis failed: {e}"}
    
    def analyze_summary_data(self) -> Dict[str, Any]:
        """Analyze summary-style data (daily/weekly totals)"""
        if self.data is None:
            return {"error": "No data loaded"}
            
        try:
            results = {}
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {"error": "No numeric columns found for analysis"}
            
            for col in numeric_cols:
                col_data = self.data[col].dropna()
                if len(col_data) > 0:
                    results[col] = {
                        'total': float(col_data.sum()),
                        'average': float(col_data.mean()),
                        'max': float(col_data.max()),
                        'min': float(col_data.min()),
                        'std': float(col_data.std()) if len(col_data) > 1 else 0,
                        'trend': self._calculate_trend(col_data)
                    }
            
            return results
        except Exception as e:
            return {"error": f"Summary analysis failed: {e}"}
    
    def analyze_business_opportunities(self) -> Dict[str, Any]:
        """Identify specific business opportunities and growth areas"""
        opportunities = []
        
        if self.data is None:
            return {"error": "No data loaded"}
            
        try:
            summary_data = self.analyze_summary_data()
            if 'error' not in summary_data:
                # Revenue optimization opportunities
                for col_name, stats in summary_data.items():
                    if 'sales' in col_name.lower() or 'revenue' in col_name.lower():
                        if stats['trend'] == 'decreasing':
                            opportunities.append({
                                'type': 'revenue_recovery',
                                'priority': 'HIGH',
                                'issue': f'{col_name} is declining',
                                'impact': stats['total'],
                                'recommendation': 'Implement immediate revenue recovery strategies'
                            })
                        elif stats['trend'] == 'stable' and stats['std'] < stats['average'] * 0.1:
                            opportunities.append({
                                'type': 'growth_potential',
                                'priority': 'MEDIUM',
                                'issue': f'{col_name} has low variation - untapped potential',
                                'impact': stats['total'] * 0.15,  # Potential 15% increase
                                'recommendation': 'Focus on growth initiatives'
                            })
                
                # Customer frequency opportunities
                for col_name, stats in summary_data.items():
                    if 'guest' in col_name.lower() or 'customer' in col_name.lower():
                        avg_daily = stats['average']
                        if avg_daily < 200:  # Low traffic threshold
                            opportunities.append({
                                'type': 'customer_acquisition',
                                'priority': 'HIGH',
                                'issue': f'Low customer volume ({avg_daily:.0f}/day)',
                                'impact': (250 - avg_daily) * 7 * 4,  # Monthly impact
                                'recommendation': 'Launch customer acquisition campaigns'
                            })
            
            return {'opportunities': opportunities}
            
        except Exception as e:
            return {"error": f"Business opportunity analysis failed: {e}"}
    
    def generate_strategic_recommendations(self) -> Dict[str, List[str]]:
        """Generate specific, actionable business recommendations"""
        recommendations = {
            'immediate_actions': [],
            'marketing_strategies': [],
            'operational_improvements': [],
            'revenue_optimization': [],
            'long_term_strategy': []
        }
        
        if self.data is None:
            return recommendations
            
        try:
            summary_data = self.analyze_summary_data()
            opportunities = self.analyze_business_opportunities()
            quality_data = self.analyze_data_quality()
            
            # Immediate Actions (0-30 days)
            if 'error' not in summary_data:
                declining_metrics = []
                stable_metrics = []
                
                for col_name, stats in summary_data.items():
                    if stats['trend'] == 'decreasing':
                        declining_metrics.append((col_name, stats))
                    elif stats['trend'] == 'stable':
                        stable_metrics.append((col_name, stats))
                
                if declining_metrics:
                    recommendations['immediate_actions'].append(
                        f"🚨 URGENT: Address declining {declining_metrics[0][0]} - implement daily monitoring"
                    )
                    recommendations['immediate_actions'].append(
                        "📊 Conduct immediate staff meeting to identify causes of performance decline"
                    )
                
                # Check for low customer counts
                for col_name, stats in summary_data.items():
                    if 'guest' in col_name.lower() and stats['average'] < 150:
                        recommendations['immediate_actions'].append(
                            "🎯 Launch flash promotion this week - customer count below optimal threshold"
                        )
            
            # Marketing Strategies (1-3 months)
            customer_metrics = []
            revenue_metrics = []
            
            if 'error' not in summary_data:
                for col_name, stats in summary_data.items():
                    if 'guest' in col_name.lower() or 'customer' in col_name.lower():
                        customer_metrics.append(stats['average'])
                    elif 'sales' in col_name.lower() or 'revenue' in col_name.lower():
                        revenue_metrics.append(stats['average'])
            
            if customer_metrics and customer_metrics[0] < 200:
                recommendations['marketing_strategies'].extend([
                    "📱 Implement social media advertising campaign - target 25% customer increase",
                    "🎁 Create loyalty program to increase repeat visits by 30%",
                    "📧 Launch email marketing to inactive customers from your POS database"
                ])
            elif customer_metrics and customer_metrics[0] > 300:
                recommendations['marketing_strategies'].extend([
                    "⭐ Focus on premium offerings - you have strong customer base",
                    "📈 Upselling training for staff to increase average ticket size",
                    "🏆 Implement VIP program for high-value customers"
                ])
            
            # Operational Improvements
            if len(self.data) >= 7:  # Weekly data available
                recommendations['operational_improvements'].extend([
                    "📅 Analyze daily patterns to optimize staff scheduling",
                    "🍽️ Review menu performance - identify low-performing items to remove",
                    "⏰ Implement peak-hour operational efficiency improvements"
                ])
            
            # Revenue Optimization
            if 'error' not in summary_data:
                total_revenue = sum(stats['total'] for col_name, stats in summary_data.items() 
                                 if 'sales' in col_name.lower() or 'revenue' in col_name.lower())
                
                if total_revenue > 0:
                    recommendations['revenue_optimization'].extend([
                        f"💰 Target 15% revenue increase = ${total_revenue * 0.15:,.0f} monthly potential",
                        "🎯 Focus on high-margin items - conduct menu engineering analysis",
                        "💳 Optimize payment processing - reduce transaction times by 20%",
                        "🥤 Implement strategic upselling - beverages and appetizers"
                    ])
            
            # Long-term Strategy (3-12 months)
            recommendations['long_term_strategy'].extend([
                "📊 Implement advanced POS analytics for real-time decision making",
                "🏪 Consider expansion opportunities based on current performance trends",
                "🤖 Automate inventory management to reduce waste by 10-15%",
                "👥 Develop staff performance incentives tied to customer satisfaction",
                "📈 Create quarterly business reviews using data-driven insights"
            ])
            
            # Data quality recommendations
            if quality_data.get('quality_score', 100) < 90:
                recommendations['immediate_actions'].insert(0,
                    "🔧 Improve data collection processes - clean data drives better decisions"
                )
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Strategic recommendation generation failed: {e}"}
    
    def calculate_revenue_impact(self) -> Dict[str, Any]:
        """Calculate potential revenue impact of recommendations"""
        if self.data is None:
            return {"error": "No data loaded"}
            
        try:
            summary_data = self.analyze_summary_data()
            impact_analysis = {}
            
            if 'error' not in summary_data:
                # Calculate baseline metrics
                total_revenue = 0
                total_customers = 0
                
                for col_name, stats in summary_data.items():
                    if 'sales' in col_name.lower() or 'revenue' in col_name.lower():
                        total_revenue = stats['total']
                    elif 'guest' in col_name.lower() or 'customer' in col_name.lower():
                        total_customers = stats['total']
                
                if total_revenue > 0:
                    # Conservative improvement estimates
                    impact_analysis = {
                        'customer_acquisition_25%': {
                            'monthly_impact': total_revenue * 0.25,
                            'annual_impact': total_revenue * 0.25 * 12,
                            'strategy': 'Marketing campaigns and promotions'
                        },
                        'average_ticket_15%': {
                            'monthly_impact': total_revenue * 0.15,
                            'annual_impact': total_revenue * 0.15 * 12,
                            'strategy': 'Upselling and menu optimization'
                        },
                        'operational_efficiency_10%': {
                            'monthly_impact': total_revenue * 0.10,
                            'annual_impact': total_revenue * 0.10 * 12,
                            'strategy': 'Improved processes and waste reduction'
                        },
                        'combined_impact': {
                            'monthly_impact': total_revenue * 0.50,  # Combined effect
                            'annual_impact': total_revenue * 0.50 * 12,
                            'strategy': 'All recommendations implemented'
                        }
                    }
            
            return impact_analysis
            
        except Exception as e:
            return {"error": f"Revenue impact calculation failed: {e}"}
    
    def _calculate_trend(self, data_series) -> str:
        """Calculate if data is trending up, down, or stable"""
        if len(data_series) < 2:
            return "insufficient_data"
            
        # Simple trend calculation
        first_half = data_series[:len(data_series)//2].mean()
        second_half = data_series[len(data_series)//2:].mean()
        
        change_percent = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def generate_advanced_insights(self) -> List[str]:
        """Generate beautifully formatted, professional insights with business recommendations"""
        insights = []
        
        if self.data is None:
            return ["❌ No data loaded for analysis"]
        
        # Header Section
        insights.append("═══ 🎯 BUSINESS STRATEGY & INTELLIGENCE REPORT ═══")
        insights.append("")
        
        # Executive Summary with Revenue Impact
        revenue_impact = self.calculate_revenue_impact()
        if 'error' not in revenue_impact and revenue_impact:
            insights.append("💰 EXECUTIVE SUMMARY - REVENUE OPPORTUNITIES")
            insights.append("─" * 50)
            
            if 'combined_impact' in revenue_impact:
                monthly_potential = revenue_impact['combined_impact']['monthly_impact']
                annual_potential = revenue_impact['combined_impact']['annual_impact']
                insights.append(f"🚀 TOTAL GROWTH POTENTIAL: ${monthly_potential:,.0f}/month | ${annual_potential:,.0f}/year")
                insights.append("")
        
        # Strategic Recommendations Section - THE MAIN EVENT
        recommendations = self.generate_strategic_recommendations()
        if 'error' not in recommendations:
            insights.append("🎯 IMMEDIATE ACTION PLAN (Next 30 Days)")
            insights.append("─" * 50)
            for i, action in enumerate(recommendations.get('immediate_actions', []), 1):
                insights.append(f"{i}. {action}")
            insights.append("")
            
            insights.append("📈 MARKETING & GROWTH STRATEGIES (1-3 Months)")
            insights.append("─" * 50)
            for i, strategy in enumerate(recommendations.get('marketing_strategies', []), 1):
                insights.append(f"{i}. {strategy}")
            insights.append("")
            
            insights.append("⚙️ OPERATIONAL IMPROVEMENTS")
            insights.append("─" * 50)
            for i, improvement in enumerate(recommendations.get('operational_improvements', []), 1):
                insights.append(f"{i}. {improvement}")
            insights.append("")
            
            insights.append("💰 REVENUE OPTIMIZATION TACTICS")
            insights.append("─" * 50)
            for i, tactic in enumerate(recommendations.get('revenue_optimization', []), 1):
                insights.append(f"{i}. {tactic}")
            insights.append("")
        
        # Data Quality Section (Condensed)
        quality_data = self.analyze_data_quality()
        if 'error' not in quality_data:
            insights.append("📊 DATA QUALITY & PERFORMANCE METRICS")
            insights.append("─" * 50)
            
            score = quality_data['quality_score']
            if score >= 95:
                status_emoji = "🟢"
                status_text = "EXCELLENT"
            elif score >= 80:
                status_emoji = "🟡" 
                status_text = "GOOD"
            else:
                status_emoji = "🔴"
                status_text = "NEEDS IMPROVEMENT"
                
            insights.append(f"{status_emoji} Data Quality: {score}/100 - {status_text}")
        
        # Performance Metrics Section (Condensed but insightful)
        if self.data_type == "summary":
            summary_data = self.analyze_summary_data()
            if 'error' not in summary_data:
                # Sort metrics by total value for better presentation
                sorted_metrics = sorted(summary_data.items(), key=lambda x: x[1]['total'], reverse=True)
                
                for i, (col_name, stats) in enumerate(sorted_metrics[:3]):  # Top 3 metrics only
                    display_name = col_name.replace('_', ' ').title()
                    insights.append(f"{i+1}. {display_name}: ${stats['total']:,.0f} total | ${stats['average']:,.0f} avg")
                    
                    if stats['trend'] == 'increasing':
                        insights.append("   📈 TRENDING UP - Maintain momentum!")
                    elif stats['trend'] == 'decreasing':
                        insights.append("   📉 NEEDS ATTENTION - See action plan above")
                    else:
                        insights.append("   ➡️  STABLE - Growth opportunity available")
            insights.append("")
        
        # Financial Impact Projections
        if 'error' not in revenue_impact and revenue_impact:
            insights.append("💎 PROJECTED FINANCIAL IMPACT")
            insights.append("─" * 50)
            
            for strategy_name, impact_data in revenue_impact.items():
                if strategy_name != 'combined_impact':
                    strategy_display = strategy_name.replace('_', ' ').title()
                    monthly = impact_data['monthly_impact']
                    insights.append(f"• {strategy_display}: +${monthly:,.0f}/month")
            insights.append("")
        
        # Long-term Strategy
        if recommendations.get('long_term_strategy'):
            insights.append("🚀 LONG-TERM GROWTH STRATEGY (3-12 Months)")
            insights.append("─" * 50)
            for i, strategy in enumerate(recommendations['long_term_strategy'][:3], 1):  # Top 3
                insights.append(f"{i}. {strategy}")
            insights.append("")
        
        # Call to Action
        insights.append("✅ NEXT STEPS")
        insights.append("─" * 50)
        insights.append("1. 📋 Review and prioritize the immediate action items above")
        insights.append("2. 🎯 Select 2-3 marketing strategies to implement this month") 
        insights.append("3. 💰 Track progress weekly and adjust strategies based on results")
        insights.append("4. 📊 Schedule monthly data reviews to monitor improvement")
        insights.append("")
        insights.append("═══ 📈 YOUR BUSINESS SUCCESS ROADMAP IS READY! ═══")
        
        return insights
    
    def analyze_sales_trends(self) -> Dict[str, Any]:
        """Analyze temporal sales patterns - optimized for data type"""
        # For summary data, skip this analysis gracefully
        if self.data_type == "summary":
            return {"skipped": "Sales trend analysis not applicable for summary data", "type": "summary_data"}
            
        if 'date' not in self.column_mapping or 'price' not in self.column_mapping:
            return {"skipped": "Missing required columns for sales analysis", "type": "missing_columns"}
        
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
        """Analyze which menu items are performing best/worst - optimized for data type"""
        # For summary data, skip this analysis gracefully
        if self.data_type == "summary":
            return {"skipped": "Menu analysis not applicable for summary data", "type": "summary_data"}
            
        if 'item_name' not in self.column_mapping or 'price' not in self.column_mapping:
            return {"skipped": "Missing required columns for menu analysis", "type": "missing_columns"}
        
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
        """Main insights method - now uses the advanced version"""
        return self.generate_advanced_insights()
    
    def export_analysis(self, output_file: str = "analysis_results.json"):
        """Export all analysis results including business recommendations to JSON for C++ frontend"""
        results = {
            'column_mapping': self.column_mapping,
            'data_type': self.data_type,
            'data_quality': self.analyze_data_quality(),
            'summary_analysis': self.analyze_summary_data(),
            'business_opportunities': self.analyze_business_opportunities(),
            'strategic_recommendations': self.generate_strategic_recommendations(),
            'revenue_impact_projections': self.calculate_revenue_impact(),
            'sales_trends': self.analyze_sales_trends(),
            'menu_performance': self.analyze_menu_performance(),
            'ai_insights': self.generate_ai_insights(),
            'generated_at': datetime.now().isoformat(),
            'business_summary': {
                'total_data_points': len(self.data) if self.data is not None else 0,
                'analysis_type': 'Business Strategy & Intelligence Report',
                'focus_areas': ['Revenue Growth', 'Customer Acquisition', 'Operational Efficiency']
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Business Strategy Analysis exported to {output_file}")
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the AI analyzer
    analyzer = RestaurantDataAI()
    
    # Example of how to use it
    print("Enhanced Restaurant Data Analysis AI - Ready")
    print("Supports: CSV (.csv) and Excel (.xlsx, .xls) files")
    print("Now with advanced AI insights and better data handling!")
    print("Usage:")
    print("1. analyzer.load_data('your_toast_data.csv')  # For CSV")
    print("   analyzer.load_data('your_toast_data.xlsx') # For Excel")  
    print("   analyzer.load_data('data.xlsx', sheet_name='Sales') # Specific sheet")
    print("2. insights = analyzer.generate_ai_insights()")
    print("3. analyzer.export_analysis('results.json')")