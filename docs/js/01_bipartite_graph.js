function draw_bipartite_graph() {

var bartite_data = 'dataset/bipartite_graph.csv';

d3.csv(bartite_data, function(d) {
    data = d.map(function(d) {return [d["name"], d["cluster_no"], +d["spec_cluster"], +d["gmm_cluster"]];});   //Once loaded, copy to dataset.
    console.log(data);
    bipartite_graph()   //Then call other functions that
});

function bipartite_graph() {

var color ={American_Restaurant:"#f44336", Asian_Food:"#b71c1c",
              Asian_Restaurant:"#e91e63", Bakery:"#ad1457", Buffet:"#283593",
              Cafe:"#0277bd", Chinese_Restaurant:"#26c6da",  Deli:"#00695c", Diner:"#2e7d32",
              English_Restaurant:"#8bc34a", European_Restaurant:"#9e9d24", Fast_Food_Restaurant:"#f9a825",
              Food_Court:"#ff8f00", HongKong_Restaurant:"#e65100", Indian_Restaurant:"#bf360c",
              Japanese_Restaurant:"#5d4037", Malay_Restaurant:"#424242", Mediterranean_Restaurant:"#263238",
              Mexican_Restaurant:"#5d4037"};

  //var svg = d3.select("body").append("svg").attr("width", 1300).attr("height", 570).attr("padding",0);

  var margin = {top: 0, right: 0, bottom: 0, left: 0};
  var width = 1300 ,
      height = 500 ;

  var svg = d3.select("#bipartite_graph")
      .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("text").attr("x",330).attr("y",12)
    .attr("class","header").text("Cluster by Sentiment Score");
  svg.append("text").attr("x",1130).attr("y",12)
    .attr("class","header").text("Cluster by Dining Type (Count)");

  var g =[svg.append("g").attr("transform","translate(230,45)")
      ,svg.append("g").attr("transform","translate(1000,45)")];

  var bp=[ viz.bP()
      .data(data)
      .min(10)
      .pad(0.5)
      .height(450)
      .width(200)
      .barSize(35)
      .fill(d=>color[d.primary])
    ,viz.bP()
      .data(data)
      .value(d=>d[3])
      .min(10)
      .pad(0.5)
      .height(450)
      .width(200)
      .barSize(35)
      .fill(d=>color[d.primary])
  ];

  [0,1].forEach(function(i){
    g[i].call(bp[i])

    g[i].append("text").attr("x",-50).attr("y",-8).style("text-anchor","middle").text("Restaurant Type");
    g[i].append("text").attr("x", 250).attr("y",-8).style("text-anchor","middle").text("Cluster No.");

    g[i].append("line").attr("x1",-100).attr("x2",0);
    g[i].append("line").attr("x1",200).attr("x2",300);

    g[i].selectAll(".mainBars")
      .on("mouseover",mouseover)
      .on("mouseout",mouseout);
    g[i].selectAll(".mainBars").append("text").attr("class","label")
      .attr("x",d=>(d.part=="primary"? -30: 30))
      .attr("y",d=>+6)
      .text(d=>d.key)
      .attr("text-anchor",d=>(d.part=="primary"? "end": "start"));

    g[i].selectAll(".mainBars").append("text").attr("class","perc")
      .attr("x",d=>(d.part=="primary"? -180: 80))
      .attr("y",d=>+6)
      .text(function(d){ return d3.format("0.0%")(d.percent)})
      .attr("text-anchor",d=>(d.part=="primary"? "end": "start"));
  });

  function mouseover(d){
    [0,1].forEach(function(i){
      bp[i].mouseover(d);

      g[i].selectAll(".mainBars").select(".perc")
      .text(function(d){ return d3.format("0.0%")(d.percent)});
    });
  }
  function mouseout(d){
    [0,1].forEach(function(i){
      bp[i].mouseout(d);

      g[i].selectAll(".mainBars").select(".perc")
      .text(function(d){ return d3.format("0.0%")(d.percent)});
    });
  }
  d3.select(self.frameElement).style("height", "1800px");
}
}
