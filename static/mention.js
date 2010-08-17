$(document).ready(function(){
	$("a.mentionhandler").live("click",function(){
		key = $(this).attr("href").replace('#','');
		obj = $(this).parent().parent();
		$.ajax({
			type:'POST',
			url: '/a/mention/read/',
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
});
