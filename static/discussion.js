$(document).ready(function(){
	$("a.closehandler").live("click",function(){
		var key = $(this).attr("href").replace('#','');
		$.ajax({
            type:'POST',
            url: '/a/discussion/close/',
            dataType: "json",
            data: 'key='+key,
            success:function(json){
                if (json.error){
                    alert(json.error);
                }
				if (json.result){
					$("#comment_handler").text("评论已经被关闭啦，嘻嘻");
				}
            }
        });
		return false;
	})
})
