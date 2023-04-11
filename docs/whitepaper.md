# What is TraceXRPL (WIP)

## Introduction

TraceXRPL allows manufacturers to document the lifecycle of their products in an immutable, tamper-proof way. Utilizing NFTs, we mirror physical products on the XRPL, record product information via the URI, and connect them to other NFTs that are minted as the production stage advances. This inherently authenticates products, creates producer-to-consumer trust, and eliminates the susceptibility of supply chain misinformation.

## Use Cases

### Use Case 1

A consumer purchases, or preorders a bag online, and with their receipt they are able to claim an NFT that represents this bag. As the company produces the bag, each stage of production is represented and minted as an NFT that is connected to the consumers bag/NFT.  Using their NFTokenID, the consumer can then view their product history and authenticity online. 

![Authenticity Example](./images/authenticity_example.png)

Populated by data from the XRPL, Product Metadata and Product History are stored as NFTs and can **not** be changed. 

### Use Case 2

Other luxury products, such as watches, have communities of enthusiasts and professionals that still have trouble verifying if products are real. Even though some watch manufacturers have serial number lookups, the serial number can be taken from a real model and put on the fake. With TraceXRPL, the products serial number is linked to an NFT, the production lifecycle recorded as NFTs, and only one NFT will have the matching serial number. On top of this, the owner of the watch will own it digitally, further proving the watch is authentic.

## Features

### Current Features

1. Ability to mint a product as an NFT
2. Add custom production steps and update a products production status via NFTs
3. NFTs are all connected and easily queried

### To Do List

1. Further develop on-ledger storage to store more metadata about a product, such as a watches face, band, etc.
2. Finish creating API (most important endpoint will return JSON of all on-chain/off-chain data about a product)
3. Code refactoring
4. Conversion to celery for task management
5. Create [recommended TXT](https://xrpl.org/nftoken.html#txt-record-format) / .well-known paths
6. Allow other wallets to claim product NFT
7. Create business sign-in & create a real UI
8. Shopify App and WordPress Plugin

## Technical Design

### On-Chain vs Off-Chain storage

Storing data on-chain is an integral part of the projects purpose, which means we are storing everything that can reasonably be stored on the XRPL via the URIs of NFTs. 

#### Product Model and Product

The Product Model is the data that every NFT Product inherits. A Product Model is currently a UUID, name, orginization, image, and the default production stage.

When a Product is minted, it inherits the Product Model, and the URI contains the following JSON 
```
{
'org': 'Test', # Product Orginization. MAX length 30 
'product': 'Bag', # Product Name. MAX length 20
'model': 0, # Increases by 1 for each product created. MAX length 10
'creation': 1679606084 # Epoch creation date. MAX length 12 
}
```

A new Product row is created in the SQL database, which includes the NFTokenID, Transaction Hash, Product Stage Number and the Product Models UUID.

#### Product Stages

The Product Stages represent the different stages of production that the business has created for a certain Product Model. These stages are stored in a SQL database and include the Product Model UUID, Stage Name and the chronological Stage Number.

When a Product is assigned a certain product stage, a NFT is minted representing the product stage, and the URI contains the following JSON

```
{
'date': 1679606122, # Epoch creation date MAX length 12
'stage': 1, # Product Stage number MAX length 3
'max': 4, # Total number of Product Stages for product MAX length 3
'id': 0000099B00000000 # Last 16 of Product NFTokenID
}
```

Last 16 digits of NFTOKENID are the unique identifier and removes unnecessary 'identification' data, because all our minted NFTs have the same flags, transfer fee and issuer. The Product NFT can be owned by external wallets, but the product stage NFTs will always stay in the issuers wallet.
