# Serverless Test
## GET /product
``` json
{
    "TableName": "product",
    "Key": {
        "id": {
            "S": "$input.params('id')"
        }
    }
}
```
``` json
{
    "id": $input.json('$.Item.id.S'),
    "name": $input.json('$.Item.name.S'),
    "price": $input.json('$.Item.price.N')
}
```

## POST /product
``` json
{
    "TableName": "product",
    "Item": {
        "id": {
            "S": $input.json('$.id')
        },
        "name": {
            "S": $input.json('$.name')
        },
        "price": {
            "N": "$input.json('$.price')"
        }
    }
}
```
``` json
{"message": "User Created"}
```