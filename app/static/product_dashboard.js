$('table tbody tr .modalActivate').on('click', async function(e){
    $("#loading").css("display", "");

    var transhash=$(this).closest('tr').data('transhash')
    var nftokenid=$(this).closest('tr').data('nftokenid')
    var date=$(this).closest('tr').data('date')

    $("#nftokenid").html(nftokenid)
    $("#transhash").html(transhash)
    $("#date").html(date)
    $("#nftokenid_input").val(nftokenid)

    var stagesHtml = ""
    // Use API to eliminate excessive processing
        await fetch(`/api/get_product_stages/${nftokenid}`).then(response => response.json())
        .then(data => {
            stagesHtml = ''
            for(x in data) {
                i = data[x]
                if(i.active) {
                    var creation = new Date(i.date * 1000);
                    stagesHtml += `<p><strong>${i.stage_name}: </strong>${creation.toLocaleString()} <a href="https://testnet.xrpl.org/nft/${i.validating_id}" target="_blank">Validated</a></p>`   
                } else {
                    stagesHtml += `<p><strong>${i.stage_name}: </strong><s>Not Active</s></p>`
                }
            }
            $("#product_stages").html(stagesHtml)
        })
        await fetch(`/api/get_metafield_dashboard/${nftokenid}`).then(response => response.json())
        .then(data => {
            metaHtml = ''
            if(data.type === 'not_created') {
                for(x in data) {
                    if(data[x] !== 'not_created') {
                        metaHtml += `
                        <div class="input-group mb-3">
                            <span class="input-group-text" id="${data[x]}-addon">${data[x]}</span>
                            <input type="text" class="form-control" name="${data[x]}" placeholder="${data[x]}" aria-label="${data[x]}" aria-describedby="${data[x]}-addon" required>
                        </div>
                      `
                    }
                    console.log(data[x])
                }
                metaHtml += `
                <input type="hidden" name="type" value="create_meta">
                <input type="hidden" name="nftokenid" value="${nftokenid}">
    
                <button type="submit" class="btn btn-primary m-1">Create NFT Metadata</button>
                `
            } else if(data.type === 'created') {
                metaHtml = ''
                for(const [key, value] of Object.entries(data.uri)) {
                    metaHtml += `
                    <p><strong>${key}: </strong>${value}</p>
                  `
                }
                console.log(data)
                metaHtml += `
                <a href="https://testnet.xrpl.org/nft/${data.nftokenid}" target="_blank">Validated</a>
                `
            }
            
            $("#product_metadata").html(metaHtml)
        })
    $("#loading").css("display", "none");
    $("#rowmodal").modal("show");
});