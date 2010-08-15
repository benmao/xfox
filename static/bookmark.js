$(document).ready(function(){
	$("#bookmark").click(function(event){
		var bookmark = $("#bookmark")
		bookmark.attr("class","bookmarking")
		var href =bookmark.attr("href");
		$.ajax({
			type: "POST",
			url: href,
			dataType: "json",
			beforeSend:function(){
				bookmark.attr("href","#"); 
			},
			success: function(json){
				if (json.error){
					alert(json.error);
				}
				if (json.result){
					bookmark.attr("class",json.result);
					if (json.result =="bookmarked"){
						bookmark.attr("href",href.replace("action=do","action=un"));
					}else{
						bookmark.attr("href",href.replace("action=un","action=do"));
					}
				}
			}
		});
		return false;
	});
	
});
