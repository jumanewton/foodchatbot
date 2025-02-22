import mysql.connector
from mysql.connector import Error

# Establish database connection
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='root',
    database='pandeyji_eatery'
)

def get_order_status(order_id: str):
    try:
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor = connection.cursor()
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error retrieving order status: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
# this code snippet is a helper function to interact with the database.
def get_next_order_id():
    cursor = None  # Define cursor before try block
    try:
        query = "SELECT MAX(order_id) FROM orders"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        
        # Ensure result is not None before adding 1
        return (result[0] + 1) if result and result[0] else 1

    except Error as e:
        print(f"Error retrieving next order ID: {e}")
        return 1  # Safe fallback in case of error

    finally:
        if cursor:
            cursor.close()
# The above code snippet is a helper function to interact with the database.

def insert_order(food_item: str, quantity: int, order_id: int):
    try:
        cursor = connection.cursor()
        cursor.callproc("insert_order_item", (food_item, quantity, order_id))
        connection.commit()
        cursor.close()
        return 1
    except Error as e:
        print(f"Error inserting order: {e}")
        connection.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()

# The above code snippet is a helper function to interact with the database.

def get_order_total(order_id: int):
    try:
        query = "SELECT get_total_order_price(%s)"  # Use %s as a placeholder
        cursor = connection.cursor()
        cursor.execute(query, (order_id,))  # Pass order_id correctly as a tuple
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] else 0  # Ensure it returns a float
    except Error as e:
        print(f"Error retrieving order total: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()

# The above code snippet is a helper function to interact with the database.

def insert_order_tracking(order_id: int, status: str):
    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        connection.commit()
        cursor.close()
        return 1
    except Error as e:
        print(f"Error inserting order tracking: {e}")   
        connection.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()