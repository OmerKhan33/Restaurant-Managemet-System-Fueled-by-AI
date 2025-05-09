{% extends 'base.html' %}

{% block content %}
    <style>
        .insights-container {
            padding: 40px;
            max-width: 900px;
            margin: auto;
            background-color: #f4f4f4;
            color: #333;
            border-radius: 10px;
        }

        .insight {
            margin-bottom: 30px;def get_sales_trends():
    # Placeholder for sales data (to be replaced with actual DB queries later)
    return [100, 120, 150, 180, 210]  # Simulated sales trend data

def get_customer_performance():
    # Placeholder for customer performance data
    return {
        "top_customer": "John Doe",
        "total_orders": 250,
        "average_spend": "$15.00"
    }

def get_popular_menu_items():
    # Placeholder for popular menu items
    return ["Burger", "Fries", "Drink"]

            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
        }

        /* Dark mode adjustments */
        [data-theme="dark"] .insights-container {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }

        [data-theme="dark"] .insight {
            background-color: #2a2a2a;
            color: #e0e0e0;
            box-shadow: 0 0 10px rgba(255,255,255,0.05);
        }

        [data-theme="dark"] .insight h3,
        [data-theme="dark"] .insight p,
        [data-theme="dark"] .insights-container h2 {
            color: #e0e0e0 !important;
        }
    </style>

    <div class="insights-container">
        <h2>Data-Driven Insights</h2>
        <div class="insight">
            <h3>Sales Trends</h3>
            <p>Placeholder for sales trends chart/graph.</p>
        </div>
        <div class="insight">
            <h3>Customer Performance</h3>
            <p>Placeholder for customer performance analysis.</p>
        </div>
        <div class="insight">
            <h3>Popular Menu Items</h3>
            <p>Placeholder for popular items list or chart.</p>
        </div>
    </div>
{% endblock %}
