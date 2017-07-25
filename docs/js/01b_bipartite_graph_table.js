function draw_bipartite_table() {

  var bartite_datatable = 'dataset/bipartite_table_final.csv';

  //# d3.csvParseRows(string[, row]) <> Equivalent to dsvFormat(",").parseRows.

    d3.csv(bartite_datatable, function(data2) {
    //var parsedCSV = d3.dsvFormat(",").parseRows(data2);         //var parsedCSV = d3.csvparseRows(data2);
    data2 = data2.map(function(data2)
            {return [data2["venue_name"], data2["spe_clus_id"],
              +data2["med_senti_score"], data2["new_venue_type"]];});   //Once loaded, copy to dataset.

    var container = d3.select('#myTable')
                      .append("tbody")
                        .selectAll("tr")
                            .data(data2).enter()
                            .append("tr")
                        .selectAll("td")
                            .data(function(d) { return d; }).enter()
                            .append("td")
                            .text(function(d) { return d; })

    console.log(data2)

    $("[class*=label]").mouseover(function() {
      var selected_label =  $(event.target).text();
      console.log(selected_label);
      });

    // filter table
    $(document).ready(function($) {
      $('table').hide();

      $("[class*=label]").mouseout(function() {
        $('table').hide();

      $("[class*=label]").mouseover(function() {
        $('table').show();
        var selected_label =  $(event.target).text();
        var selection = selected_label;
        var dataset = $('tbody').find('tr');
        // show all rows first
        dataset.show();
        // filter the rows that should be hidden
        dataset.filter(function(index, item) {
          return $(item).find('td:nth-child(4)').text().split(',').indexOf(selection) === -1;
        }).hide();

      });
    });
  });
  });
}
