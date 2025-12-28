from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Shopify AI Analytics Service")

class QuestionRequest(BaseModel):
    store_id: str
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    intent = classify_intent(request.question)

    if intent == "unknown":
        return {
            "answer": "Please provide more details such as product name or time range so I can help you better.",
            "confidence": "low"
        }

    plan = plan_query(intent, request.question)
    query = generate_shopifyql(plan)
    data = execute_query(query)
    answer = explain_result(data, plan)

    return {
        "answer": answer,
        "confidence": "medium"
    }


def classify_intent(question: str) -> str:
    q = question.lower()

    if any(word in q for word in ["inventory", "stock", "reorder", "out of stock"]):
        return "inventory"

    if any(word in q for word in ["sale", "revenue", "top", "selling"]):
        return "sales"

    if any(word in q for word in ["customer", "repeat", "returning"]):
        return "customers"

    return "unknown"



def plan_query(intent: str, question: str) -> dict:
    plan = {
        "intent": intent,
        "table": None,
        "metrics": [],
        "time_range_days": 30
    }

    if intent == "inventory":
        plan["table"] = "inventory_levels"
        plan["metrics"] = ["available", "sold_per_day"]
        plan["time_range_days"] = 30

    elif intent == "sales":
        plan["table"] = "orders"
        plan["metrics"] = ["total_sales", "units_sold"]
        plan["time_range_days"] = 7

    elif intent == "customers":
        plan["table"] = "customers"
        plan["metrics"] = ["repeat_customers"]
        plan["time_range_days"] = 90

    return plan



def generate_shopifyql(plan: dict) -> str:
    table = plan["table"]
    metrics = plan["metrics"]
    days = plan["time_range_days"]

    if not table or not metrics:
        return ""

    metrics_clause = ", ".join(metrics)

    shopifyql = f"""
    FROM {table}
    SHOW {metrics_clause}
    SINCE -{days}d
    """
    print("Generated ShopifyQL:")
    print(shopifyql.strip())
    
    return shopifyql.strip()
    
def execute_query(shopifyql: str) -> dict:
    """
    Mock execution of ShopifyQL query.
    """

    # Inventory mock
    if "inventory_levels" in shopifyql:
        return {
            "average_daily_sales": 10,
            "current_inventory": 40
        }

    # Sales mock
    if "orders" in shopifyql:
        return {
            "top_products": [
                {"name": "Product A", "units_sold": 120},
                {"name": "Product B", "units_sold": 95}
            ]
        }

    # Customers mock
    if "customers" in shopifyql:
        return {
            "repeat_customers": 32
        }

    return {}



def explain_result(data: dict, plan: dict) -> str:
    intent = plan["intent"]

    if intent == "inventory":
        daily_sales = data.get("average_daily_sales", 0)
        current_inventory = data.get("current_inventory", 0)

        recommended_reorder = max((daily_sales * 7) - current_inventory, 0)

        return (
            f"Based on recent sales, you sell about {daily_sales} units per day. "
            f"To avoid running out of stock next week, you should reorder at least "
            f"{recommended_reorder} units."
        )

    if intent == "sales":
        products = data.get("top_products", [])
        if not products:
            return "There were no sales in the selected period."

        product_list = ", ".join(
            [f"{p['name']} ({p['units_sold']} units)" for p in products]
        )

        return f"Your top selling products recently were: {product_list}."

    if intent == "customers":
        repeat_count = data.get("repeat_customers", 0)
        return f"You had {repeat_count} customers who placed repeat orders recently."

    return "Unable to generate insights from the available data."


