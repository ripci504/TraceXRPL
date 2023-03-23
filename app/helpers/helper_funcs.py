# A NFTOKENID is usually 64 characters/256 bits long
# Since issuer will always own these NFTs, we can remove 
# the issuer account identifier and transfer fee/identity flag fields

def shrink_nftokenid(nftokenid):
    if len(nftokenid) == 16:
        return str(nftokenid)
    return str(nftokenid[48:])
