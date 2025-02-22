import re

def extract_session_id(session_str: str):
    match = re.search(r"sessions/([^/]+)/contexts/", session_str)
    if match:
        session_id = match.group(1)
        return session_id
    return ""

def get_str_from_food_dict(food_dict: dict):
    items = [f"{quantity} {food}" for food, quantity in food_dict.items()]
    if len(items) > 1:
        return " and ".join([", ".join(items[:-1]), items[-1]]) if len(items) > 2 else " and ".join(items)
    return items[0] if items else ""

if __name__ == "__main__":
    session_str = "projects/newtonai-fsqe/agent/sessions/b2be3947-9b61-f3d4-d208-8aac486ba206/contexts/ongoing-order"
    print(extract_session_id(session_str)) # b2be3947-9b61-f3d4-d208-8aac486ba206
    food_dict = {"pizza": 2, "burger": 3}
    print(get_str_from_food_dict(food_dict)) # 2 pizza and 3 burger