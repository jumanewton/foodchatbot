from fastapi import FastAPI
from fastapi import  Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()
# in-memory storage for the orders
# this will be replaced with a database in the future
inprogress_order = {}

@app.post("/")
async def handle_request(request: Request):
    # retrieve the JSON data from the request
    payload = await request.json()
    # extract the necesary information from the payload
    # based on the structure of webhook request
    # intent = payload.get("queryResult", {}).get("intent", {}).get("displayName")
    query_result = payload.get("queryResult", {})
    intent = query_result.get("intent", {}).get("displayName", "")
    parameters = query_result.get("parameters", {})
    output_contexts = query_result.get("outputContexts", [])
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
    # handle the intent
    intent_handler_dict={
        "track.order -  context: tracking-order": track_order,
        "order.complete - context: ongoing-order": complete_order,
        # "order.remove - context: ongoing-order": remove_order,
        "order.add - context: ongoing-order": add_order
    }
    response = intent_handler_dict.get(intent)(parameters, session_id)
    return response

def add_order(parameters: dict, session_id: str):
    # add the order to the inprogress_order
    food_items = parameters.get("food-item")
    quantities = parameters.get("number")
    if len(food_items) != len(quantities):
        fullfilment_text = "Please provide the quantity for each food item"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_order:
            current_food_dict = inprogress_order[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_order[session_id] = current_food_dict
        else:
            inprogress_order[session_id] = new_food_dict
        
        order_str = generic_helper.get_str_from_food_dict(inprogress_order[session_id])
        fullfilment_text = f"So far, you have ordered {order_str}. Anything else you would like to add?"
    return JSONResponse(
        content={
            "fulfillmentText": fullfilment_text
        }
    )

def track_order(parameters: dict, session_id: str):
    # track the order based on the parameters
    order_id = parameters.get("order_id")
    status = db_helper.get_order_status(order_id) 
    # return the tracking status
    if status:
        fullfilment_text = f"Your status for order {order_id} is {status}"
    else:
        fullfilment_text = f"No order found with order ID: {order_id}"
    return JSONResponse(
        content={
            "fulfillmentText": fullfilment_text
        }
    )
    


def remove_order(parameters: dict, session_id: str):
    pass

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fullfilment_text = "I am sorry, I could not find any order to complete. Can you please add an order first?"
    else:
        order = inprogress_order[session_id]
        # Save the order in the database
        order_id = save_to_db(order)
        if order_id == 0:
            fullfilment_text = "There was an error while saving the order. Please try again."
        else:
            order_total = db_helper.get_order_total(order_id)
            fullfilment_text = f"Your order has been placed successfully. \nYour order ID is {order_id}, you can use it for tracking.\nYour order total is {order_total:.2f}, which you can pay at the time of delivery."
    
        del inprogress_order[session_id]  # Delete the session order only after successful execution

    return JSONResponse(
        content={
            "fulfillmentText": fullfilment_text  # 
        }
    )



def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order(food_item, quantity, next_order_id)
        if rcode == 0:
            return 0
    db_helper.insert_order_tracking(next_order_id, "In Progress")
    return next_order_id
