# Get Product Information

Get all on-chain & off-chain information about a product from a NFTokenID.

**URL** : `/api/get_product_information/<NFTokenID>`

**Method** : `GET`

## Success Response

**Condition** : If the NFTokenID is a valid NFT that is linked to a product in the SQL database.

**Content Example**

```
{
   "status":"success",
   "nftokenid":"000800003A34493ACBADF9199E7BEEE9509773D7FA97D50B0000099B00000000",
   "owner":"raJkqpS2HaMqnQXdJkyrnTCF3JP87MpXq9",
   "transaction_hash":"6F498B0F0C552E19DA3A2736C1E9DC25FE3D811829503E5D8904555DBCEDEC22",
   "data":{
      "product_image":"NemF4Xo5kXG8yQPnC3zP4L.png",
      "product_image_url":"http://127.0.0.1:5000/static/uploads/NemF4Xo5kXG8yQPnC3zP4L.png",
      "product_data":{
         "creation":1680112252,
         "model":0,
         "org":"Test",
         "product":"Bag"
      },
      "product_metadata":{ 
         "uri":{
            "Color":"Black",
            "Random":"Test"
         },
         "validating_id":"000800003A34493ACBADF9199E7BEEE9509773D7FA97D50B16E5DA9C00000001"
      },
      "product_stages":[
         {
            "active":true,
            "date":1680112373,
            "stage_name":"Order Placed",
            "stage_number":1,
            "validating_id":"000800003A34493ACBADF9199E7BEEE9509773D7FA97D50B2DCBAB9D00000002"
         },
         {
            "active":false,
            "date":false,
            "stage_name":"Production",
            "stage_number":2,
            "validating_id":false
         },
         {
            "active":false,
            "date":false,
            "stage_name":"Shipping",
            "stage_number":3,
            "validating_id":false
         },
         {
            "active":false,
            "date":false,
            "stage_name":"Delivered",
            "stage_number":4,
            "validating_id":false
         }
      ]
   }
}
```

If the Product does not have a metadata NFT minted, the product_metadata field is `false`.

## Error Response

**Condition** : The NFTokenID is not found or is not linked to a product in the SQL database.

**Code** : `404`

**Content** : `{}`