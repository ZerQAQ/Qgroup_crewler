/*
	给index用的
*/

$(document).ready(function(){
	$('#smbtn').click(function(){
		var url = $('#sqlform').attr('action');
		var data = $('#sqlform').serialize();

		$.get(url, data, function(res){
			data = jQuery.parseJSON(res);
			$('#info').empty();
			$('#info').append('<br>共返回<br>' + data.length.toString() + '<br>条搜索结果。')
			var len = data.length;
			var line_div;
			var content_div = document.getElementById('main-content');
			content_div.innerHTML = '';
			for(let i = 0; i < len; i++){
				if(i % 4 == 0){
					line_div = document.createElement('div');
					line_div.className = 'line'
					content_div.appendChild(line_div);
				}
				box_div = document.createElement('div');
				box_div.className = 'box';
				box_div.onclick = function(){window.open('tencent://AddContact/?fromId=45&fromSubId=1&subcmd=all&uin=' + data[i][0].toString());}
				box_div.innerHTML = ' \
				<img class= "head" src =' + data[i][6] + '> </img>\
								<span class="binf">' + data[i][1] + '</span> <br/>\
								<span class="binf">' + data[i][2] + ' ' + data[i][3] + ' </span> <br/>\
								<span class="binf"> ' + data[i][4] + ' </span> <br/>\
								<span class="binf"> ' + data[i][5] + ' </span> <br/>\
				'
				line_div.append(box_div);
			}

		})
	})
})