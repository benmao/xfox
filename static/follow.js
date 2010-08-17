$(document).ready(function(){
	$("a.followhandler").live("click",function(){
        key = $(this).attr("href").replace('#','');
        obj = $(this).parent().parent();
        $.ajax({
            type:'POST',
            url: '/a/followread/',
            dataType: "json",
            data: 'key='+key,
            success:function(json){
                if (json.result){
                    obj.remove();
                }
            }
        });
        return false;
    });
})
