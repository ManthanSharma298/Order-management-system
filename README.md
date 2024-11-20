## API Documentation

This document describes the endpoints available in the API.
The Flask app is hosted on [Render](https://render.com/)

**Base URL**: `https://order-management-system-hpfs.onrender.com`
#### Notes
1. **First API Request**: The first request may take longer because the server might restart. On restart, the database will be cleared as part of Render's system behavior.  
2. Use tools like `Postman`, `cURL`, or any HTTP client for testing.  
3. Replace `{placeholder}` in the endpoints with actual values as required.

---
### 1. Create item

**Method**: `POST`
**URL**: `https://order-management-system-hpfs.onrender.com/item`

**Body**:
```json
{
	"name": "string",     // Required
	"price": "float",      // Required
	"description": "string" // Optional
}
```

**Example:**
```json
{
	"description": "A powerful laptop",
	"name": "Macbook Air",
	"price": 110000.0
}
```

**Sample response**
```json
{
    "item_id": 1,
    "message": "Item created!"
}
```

### 2. Get all items

**Method**: `GET`
**URL**: `https://order-management-system-hpfs.onrender.com/items`

**Sample response**
```json
[
    {
        "description": "A powerful laptop",
        "id": 1,
        "name": "Macbook Air",
        "price": 110000.0
    },
    {
        "description": "test item",
        "id": 2,
        "name": "Item2",
        "price": 11.45
    }
]
```

### 3. Create an order

**Method**: `POST`
**URL**: `https://order-management-system-hpfs.onrender.com/order

**Body**:
Here `id` is the `id` of the item which we have created
```json
{
	"customer_id": "string",   // Required
	"items": [                 // Required
		{"id": "integer", "qty": "integer"}
	]
}
```

**Example**
```json
{
    "customer_id": "user1",
    "items": [
        {"id": 1, "qty": 1},
        {"id": 2, "qty": 2}
    ]
}
```

**Response**: 
It will return the order's `id`. Please store it, as it will be useful for updating and retrieving information.
```json
{
    "message": "Order created!!",
    "order_id": "d949a48a-a10b-4323-a758-ae5f26e93791"
}
```

---
### 4. Get an Order

**Method**: `GET`  
**URL**: `https://order-management-system-hpfs.onrender.com/order/{order_id}`  

Replace `{order_id}` with the actual ID of the order. For example:  
`https://order-management-system-hpfs.onrender.com/order/d949a48a-a10b-4323-a758-ae5f26e93791`

**Sample response**:
```json
{
  "amount": 225011.45,
  "customer_id": "user1",
  "items": [
    {
      "description": "A powerful laptop",
      "name": "Macbook Air",
      "price": 110000,
      "quantity": 1
    },
    {
      "description": "test item",
      "name": "Item2",
      "price": 11.45,
      "quantity": 1
    },
    {
      "description": "",
      "name": "iPhone 16 Pro",
      "price": 115000,
      "quantity": 1
    }
  ],
  "order_id": "d949a48a-a10b-4323-a758-ae5f26e93791",
  "status": "Order Placed",
  "timestamp": "Wed, 20 Nov 2024 13:11:00 GMT"
}
```

---
### 5. Get order status

**Method**: `GET`  
**URL**: `https://order-management-system-hpfs.onrender.com/order/status/{order_id}`  

Replace `{order_id}` with the actual ID of the order. For example:  
`https://order-management-system-hpfs.onrender.com/order/status/d949a48a-a10b-4323-a758-ae5f26e93791`

**Sample response**
```json
{
  "order_id": "d949a48a-a10b-4323-a758-ae5f26e93791",
  "status": "Order Placed"
}
```

---
### 6. Update order status

**Method**: `PUT`
**URL**: `https://order-management-system-hpfs.onrender.com/order/status/{order_id}`

Replace `{order_id}` with the actual ID of the order. For example:  
`https://order-management-system-hpfs.onrender.com/order/status/d949a48a-a10b-4323-a758-ae5f26e93791`

**Body**:
```json
{
	"status": "string"   // Required
}
```

**Example**
```json
{
	"status": "Shipped"
}
```

**Sample response**:
```json
{
    "message": "Order status updated",
    "order_id": "d949a48a-a10b-4323-a758-ae5f26e93791",
    "status": "Shipped"
}
```

---
### 7. Update order info

**Method**: `PUT`
**URL**: `https://order-management-system-hpfs.onrender.com/order/update/{order_id}`

Replace `{order_id}` with the actual ID of the order. For example:  
`https://order-management-system-hpfs.onrender.com/order/update/d949a48a-a10b-4323-a758-ae5f26e93791`

**Body**:
```json
{
    "items": [       // Required
        {"id": "integer", "qty": "integer"}
    ]
}
```

**Example** 
```json
{
    "items": [
        {"id": 1, "qty": 1},
        {"id": 3, "qty": 2}
    ]
}
```

**Sample response**:
```json
{
    "amount": 340000.0,
    "items": [
        {
            "name": "Macbook Air",
            "price": 110000.0,
            "quantity": 1
        },
        {
            "name": "Iphpne 16 pro",
            "price": 115000.0,
            "quantity": 2
        }
    ],
    "message": "Order updated successfully",
    "order_id": "d949a48a-a10b-4323-a758-ae5f26e93791"
}
```

---
### 8. Cancel order

**Method**: `DELETE`  
**URL**: `https://order-management-system-hpfs.onrender.com/order/cancel/{order_id}`  

Replace `{order_id}` with the actual ID of the order. For example:  
`https://order-management-system-hpfs.onrender.com/order/cancel/d949a48a-a10b-4323-a758-ae5f26e93791`
#### Response
```json
{
    "message": "Order deleted successfully"
}
```
