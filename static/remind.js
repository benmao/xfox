$(document).ready(function(){
    //Check remind every 1 Minute
    function check_remind(){
        var mention = $("#mention");
		var follow = $("#follow");
        if (mention[0]){ // logined user
            $.ajax({
                type:'POST',
                url: '/a/remind/',
                dataType:'json',
                success:function(json){
					/*handler mention */
                    if (json.mention > 0){
                        mention.attr("class","mention");
                        mention.text("提醒("+json.mention+")");
                    }
                    else{
                        mention.attr("class","");
                        mention.text("提醒");
                    }
					
					/* handler follow */
					if (json.follow > 0){
						follow.attr("class","mention");
						follow.text("Follow("+json.follow+")")
					}else{
						follow.attr("class","");
						follow.text("Follow");
					}
                }
            })
        };
    }
    //check_remind();
    //setInterval(check_remind,1000*60); //1 minute
})
