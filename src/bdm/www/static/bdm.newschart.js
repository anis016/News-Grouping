$(function () { 
	Highcharts.chart('chart', {
		chart: {
			plotBackgroundColor: null,
			plotBorderWidth: null,
			plotShadow: false,
			type: 'pie'
		},
		title: {
			text: 'Similar News. Jan, 2015 to Dec, 2017' + newsstats
		},
		tooltip: {
			pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
		},
		plotOptions: {
			pie: {
				allowPointSelect: true,
				cursor: 'pointer',
				dataLabels: {
					enabled: true,
					format: '<b>{point.name}</b>: {point.percentage:.1f} %',
					style: {
						color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
					},
					connectorColor: 'silver'
				}
			}
		},
		series: [{
			name: 'News',
			data: [
				{ name: 'Unlike News', y: 90.33 },
				{
					name: 'Similar News',
					y: 9.34,
					sliced: true,
					selected: true
				},
			]
		}]
	});	
});