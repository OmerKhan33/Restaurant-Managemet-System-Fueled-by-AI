# from connection import create_connection
# from pymongo import MongoClient
# import json
# import time

# # MongoDB connection
# mongo_client = MongoClient("mongodb://localhost:27017/")
# mongo_db = mongo_client["your_mongo_db"]

# # Mapping PostgreSQL tables to MongoDB collections
# TABLE_TO_COLLECTION = {
#     "orders": mongo_db["orders"],
#     "order_items": mongo_db["order_items"],
#     "users": mongo_db["users"],
#     "checkouts": mongo_db["checkouts"]
# }

# def sync_changes():
#     pg_conn = create_connection()
#     if pg_conn is None:
#         return

#     pg_cursor = pg_conn.cursor()

#     try:
#         try:
#             pg_cursor.create_replication_slot('sync_slot', output_plugin='wal2json')
#             print("✅ Replication slot created")
#         except Exception as slot_error:
#             if 'already exists' in str(slot_error):
#                 print("ℹ️ Replication slot already exists, continuing...")
#             else:
#                 raise slot_error

#         pg_cursor.start_replication('sync_slot', decode=True)
#         print("🚀 Starting real-time sync...")

#         while True:
#             msg = pg_cursor.read_message()
#             if msg:
#                 payload = json.loads(msg.payload)
#                 if 'change' in payload:
#                     for change in payload['change']:
#                         table_name = change['table']
#                         operation = change['kind']

#                         if table_name not in TABLE_TO_COLLECTION:
#                             continue

#                         collection = TABLE_TO_COLLECTION[table_name]

#                         if operation == 'insert':
#                             new_data = {col['name']: col['value'] for col in change['columnvalues']}
#                             collection.insert_one(new_data)
#                         elif operation == 'update':
#                             new_data = {col['name']: col['value'] for col in change['columnvalues']}
#                             collection.update_one({"id": new_data['id']}, {"$set": new_data})
#                         elif operation == 'delete':
#                             old_data = {col['name']: col['value'] for col in change['oldkeys']['keyvalues']}
#                             collection.delete_one({"id": old_data['id']})

#                         print(f"✅ Applied {operation} on {table_name} (id: {new_data.get('id', old_data.get('id'))})")
#             else:
#                 time.sleep(0.1)

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         pg_cursor.close()
#         pg_conn.close()
#         mongo_client.close()

# if __name__ == "__main__":
#     sync_changes()
# MongoDB connection
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['dbms_proj']
mongo_orders_collection = mongo_db['orders']

@app.route('/sync_orders')
def sync_orders():
    conn = create_connection()
    if not conn:
        flash("PostgreSQL connection failed.")
        return redirect(url_for('index'))

    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute("SELECT id, summary, item_names, quantities FROM orders")
    orders = cursor.fetchall()

    # Clear MongoDB collection first (optional, to avoid duplicates)
    mongo_orders_collection.delete_many({})

    # Insert into MongoDB
    for order in orders:
        order_doc = {
            'order_id': order[0],
            'summary': order[1],
            'item_names': order[2],
            'quantities': order[3]
        }
        mongo_orders_collection.insert_one(order_doc)

    cursor.close()
    conn.close()

    flash("✅ Orders synced to MongoDB successfully!")
    return redirect(url_for('index'))