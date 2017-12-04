$(function () { 
	var myChart = Highcharts.chart('chart', {
		chart: {
			type: 'bar'
		},
		title: {
			text: 'New Similarity Consumption'
		},
		xAxis: {
			categories: ['Apples', 'Bananas', 'Oranges']
		},
		yAxis: {
			title: {
				text: 'Fruit eaten'
			}
		},
		series: [{
			name: 'Jane',
			data: [1, 0, 4]
		}, {
			name: 'John',
			data: [5, 7, 3]
		}]
	});
});
