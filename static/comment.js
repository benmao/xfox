$(document).ready(function(){
	$("#comment_form").submit(function(){
        $.ajax({
			type:'POST',
			url: '/c/ajax/',
			data: $(this).serialize(),
			beforeSend:function(){
				$("#info").text("正在提交中....");
				$("#submit").attr("disabled",true)
			},
	        success:function(json){
				if(json.success){
					$("#info").text("评论成功了");
					$(":input[name='content']").val("")
					add_comment(decodeURI(json.comment));
					
					//remove localStorage
					if (typeof(localStorage) == 'undefined'){
						localStorage.removeItem(window.location.pathname);
					}
				}
				if (json.error){
					$("#info").text(json.error)
				}
			     $("#submit").attr("disabled",false);
			}
		})
		return false;
	})
	
	function add_comment(comment){
		$("#comment_place").append(comment);
		$("#comment_place h3").text("评论22");
	}
	
})
