var act=0;
var sm="";
var figure;


 function getData(symbol){
sm=symbol;
var date = [];
var opendata= [];
var closedata = [];
var highdata = [];
var lowdata = [];
var volume = [];

$.ajax({
		   type: "GET",
		   url: "https://poloniex.com/public?command=returnChartData&currencyPair=BTC_"+sm+"&start=1405699200&end=9999999999&period=14400",
		   data: {limit:10}, 
		   dataType: "json",
		   success: function(data) {
				for(var i=0;i<data.length;i++) {
				date.push(data[i]['date']);
				opendata.push(data[i]['open']);
				closedata.push(data[i]['close']);
				highdata.push(data[i]['high']);
				lowdata.push(data[i]['low']);
				volume.push(data[i]['volume']);
				};
		
			}
			
});
	figure = chartOption(date, opendata, closedata, highdata, lowdata, volume); 
 }

function chartOption(date, opendata, closedata, highdata, lowdata, volume){
var abc = {
    "frames": [], 
    "layout": {
        "autosize": true, 
        "boxmode": "group", 
        "yaxis": {
            "range": [
                0.0006411105555555556, 
                0.006018899444444444
            ], 
            "type": "linear", 
            "autorange": true, 
            "title": ""
        }, 
        "paper_bgcolor": "#000000", 
        "plot_bgcolor": "rgb(0, 0, 0)", 
        "dragmode": "zoom", 
        "showlegend": true, 
        "breakpoints": [], 
        "yaxis2": {
            "title": "", 
            "overlaying": "y", 
            "anchor": "x", 
            "range": [
                -32.98751678333333, 
                626.7628188833334
            ], 
            "type": "linear", 
            "autorange": true, 
            "side": "right"
        }, 
        "titlefont": {
            "color": "#bfbfbf", 
            "size": 18
        }, 
        "xaxis": {
            "showspikes": false, 
            "tickmode": "auto", 
            "title": "Time Frame", 
            "showgrid": true, 
            "zerolinecolor": "rgb(134, 132, 132)", 
            "range": [
                1405694880, 
                1420060319.9999974
            ], 
            "gridcolor": "rgb(67, 67, 67)", 
            "fixedrange": false, 
            "showline": false, 
            "type": "linear", 
            "autorange": false, 
            "rangeslider": {
                "bordercolor": "rgb(148, 145, 145)", 
                "bgcolor": "rgb(0, 0, 0)", 
                "thickness": 0.15, 
                "visible": true, 
                "range": [
                    1405694880, 
                    1420060320
                ], 
                "borderwidth": 1, 
                "autorange": true
            }
        }, 
        "title": "<b>XMR</b>", 
        "hovermode": "closest", 
        "font": {
            "size": 8
        }, 
        "margin": {
            "pad": 5, 
            "r": 15, 
            "b": 15, 
            "l": 20, 
            "t": 100
        }, 
        "legend": {
            "bordercolor": "rgb(202, 202, 202)", 
            "yanchor": "top", 
            "traceorder": "normal", 
            "xanchor": "left", 
            "borderwidth": 1, 
            "y": 1.3290543494456117, 
            "x": 0.0003259975671319549, 
            "font": {
                "color": "rgb(148, 145, 145)", 
                "size": 11
            }
        }, 
        "undefined": {
            "rangeslider": {
                "visible": true
            }
        }
    }, 
    "data": [
        {
            "autobinx": true, 
            "uid": "9cc5cf", 
            "lowsrc": "krischal:0:72e67c", 
            "type": "ohlc", 
            "autobiny": true, 
            "opensrc": "krischal:0:387e86", 
            "xsrc": "krischal:0:50e130", 
            "high": highdata, 
            "visible": true, 
            "highsrc": "krischal:0:fd32a4", 
            "low": lowdata, 
            "decreasing": {
                "line": {
                    "color": "rgb(190, 4, 5)"
                }, 
                "name": "Decreasing"
            }, 
            "close": closedata , 
            "x":date, 
            "increasing": {
                "line": {
                    "color": "rgb(3, 159, 3)"
                }, 
                "name": "Increasing"
            }, 
            "open": opendata, 
            "closesrc": "krischal:0:7161cd", 
            "mode": "markers"
        }, 
        {
            "uid": "bba0b1", 
            "yaxis": "y2", 
            "ysrc": "krischal:0:286abd", 
            "connectgaps": false, 
            "xsrc": "krischal:0:50e130", 
            "mode": "lines", 
            "decreasing": {
                "line": {
                    "color": "#7F7F7F"
                }
            }, 
            "y": volume, 
            "x": date, 
            "line": {
                "color": "rgba(23, 190, 207, 0.39)", 
                "shape": "spline"
            }, 
            "increasing": {
                "line": {
                    "color": "#17BECF"
                }
            }, 
            "type": "timeseries", 
            "name": "Volume"
        }
    ]
}
return abc;
}