// set the dimensions and margins of the graph
var margin = { top: 50, right: 30, bottom: 40, left: 60 },
  width = 700 - margin.left - margin.right,
  height = 500 - margin.top - margin.bottom;


function drawLine(selector, dataUrl, chartTitle) {
  // append the d3 svg object to the body of the page using the selector
  var chart = d3.select(selector)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
      "translate(" + margin.left + "," + margin.top + ")")

  // Load in data
  d3.csv(dataUrl,
    function (d) {
      return { Dates: d3.timeParse("%Y-%m-%d")(d.Dates), Prices: d.Prices }
    },

    function (data) {

      // Add X axis
      var x = d3.scaleTime()
        .domain(d3.extent(data, function (d) { return d.Dates; }))
        .range([0, width]);
      chart.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

      // Add Y axis
      var y = d3.scaleLinear()
        .domain([0, d3.max(data, function (d) { return +d.Prices; })])
        .range([height, 0]);
      chart.append("g")
        .call(d3.axisLeft(y));

      // Add the line
      chart.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
          .x(function (d) { return x(d.Dates) })
          .y(function (d) { return y(d.Prices) })
        )

      // Add title
      chart.append("text")
        .attr("y", 1)
        .attr("x", 9)
        .attr("dy", "-.5em")
        .attr("dx", "2em")
        .style("text-anchor", "start")
        .text(chartTitle);

    })
}

var dailyUrl = "https://raw.githubusercontent.com/mohyour/natural-gas-data/master/data/daily_natural_gas_prices.csv"
var monthlyUrl = "https://raw.githubusercontent.com/mohyour/natural-gas-data/master/data/monthly_natural_gas_prices.csv"
var dailyTitle = "Henry Hub Natural Gas Spot Price (Dollars per Million Btu) - Daily Prices"
var monthlyTitle = "Henry Hub Natural Gas Spot Price (Dollars per Million Btu - Monthly Prices"

// Draw line charts
drawLine("#daily_prices", dailyUrl, dailyTitle)
drawLine("#monthly_prices", monthlyUrl, monthlyTitle)
