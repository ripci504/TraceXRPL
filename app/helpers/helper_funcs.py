import json
from celery import Celery
from xrpl.utils import str_to_hex

# A NFTOKENID is usually 64 characters/256 bits long
# Since issuer will always own these NFTs, we can remove 
# the issuer account identifier and transfer fee/identity flag fields

def shrink_nftokenid(nftokenid):
    if len(nftokenid) == 16:
        return str(nftokenid)
    elif len(nftokenid) == 19:
        return str(nftokenid[3:])
    return str(nftokenid[48:])

def expand_nftokenid(nftokenid, nftokenidexpanded):
    if len(nftokenid) == 16:
        nftoken = nftokenidexpanded[:48] + nftokenid
        return nftoken
    elif len(nftokenid) == 19:
        nftoken = nftokenidexpanded[:48] + nftokenid[3:]
        return nftoken
    else:
        return str(nftokenid)

def shrink_json(nftokenobject):
    nftokenuri = str_to_hex(str(json.dumps(nftokenobject, separators=(',', ':'))))
    if len(nftokenuri) > 256:
        return 'object too big'
    else:
        return nftokenuri
    
def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
