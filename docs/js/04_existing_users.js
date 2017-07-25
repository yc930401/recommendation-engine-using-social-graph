function treemap()
{
  function reSortRoot(root,value_key) {
		//console.log("Calling");
		for (var key in root) {
			if (key == "key") {
				root.name = root.key;
				delete root.key;
			}
			if (key == "values") {
				root.children = [];
				for (item in root.values) {
					root.children.push(reSortRoot(root.values[item],value_key));
				}
				delete root.values;
			}
			if (key == value_key) {
				root.value = parseFloat(root[value_key]);
				delete root[value_key];
			}
		}
		return root;
	}

	$( document ).ready(function() {
		// You can comment out the whole csv section if you just have a JSON file.
    // loadJSONFile('data/portaldata.json');

    	d3.csv("dataset/cluster_updated.csv", function(csv_data){

			// Add, remove or change the key values to change the hierarchy.
      var nested_data = d3.nest()
       				.key(function(d)  { return d.senti_clus_id; })
       				.key(function(d)  { return d.venue_clus_id; })
          			.key(function(d)  { return d.mrt_loc_clus_id; })
				      .entries(csv_data);

			// Creat the root node for the treemap
			var root = {};

			// Add the data to the tree
			root.key = "Niveau de données";
			root.values = nested_data;

			// Change the key names and children values from .next and add values for a chosen column to define the size of the blocks
			root = reSortRoot(root,"Net_Worth");

			// DEBUG
// 			$("#rawdata").html(JSON.stringify(root));

			loadData(root);

		});


	});


}
