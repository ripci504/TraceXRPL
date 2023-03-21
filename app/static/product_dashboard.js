$('table tbody tr .modalActivate').on('click',function(e){
    var transhash=$(this).closest('tr').data('transhash')
    var nftokenid=$(this).closest('tr').data('nftokenid')
    var date=$(this).closest('tr').data('date')

    $("#nftokenid").html(nftokenid)
    $("#transhash").html(transhash)
    $("#date").html(date)
    $("#nftokenid_input").val(nftokenid)

    var stagesHtml = ""
    // Use API to eliminate excessive processing
        fetch(`/api/get_product_stages/${nftokenid}`).then(response => response.json())
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
    $("#rowmodal").modal("show");
});