$(document).ready(function(){
	var content = $("textarea[name='content']");
	if (content[0] && typeof(localStorage) != 'undefined'){
		if (localStorage.getItem(window.location.pathname)){
			content.val(localStorage.getItem(window.location.pathname));
		}
		setInterval(autosave,5000);
	}
	else{
		return;
	}

	function autosave(){
		localStorage.setItem(window.location.pathname,content.val());
		//alert(content.val());
	}
	
	function clear(){
		localStorage.removeItem(window.location.pathname);
		content.val("");
	}
	
	$("#btn_clear").live("click",function(){
		clear();
	})
})
