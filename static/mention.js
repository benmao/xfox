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
	
	//Check Mention every 1 Minute
	function check_mention(){
		obj = $("#mention");
		if (obj[0]){ // logined user
			$.ajax({
				type:'POST',
				url: '/a/mention/check/',
				dataType:'json',
				success:function(json){
					if (json.count > 0){
						obj.attr("class","mention");
						obj.text("提醒("+json.count+")");
					}
					else{
						obj.attr("class","");
						obj.text("提醒");
					}
				}
			})
		};
	}
	//check_mention();
	setInterval(check_mention,1000*30); //1 minute
});
