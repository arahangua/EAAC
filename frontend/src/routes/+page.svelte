<script>
   import { onMount } from 'svelte';
   import { Network} from 'vis-network';
   import {DataSet} from 'vis-data';
   
   let results = [];
   let container;
   let network;

    async function fetchQuery() {
    const response = await fetch('http://localhost:8080/query', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
        query: 'MATCH (n)-[r]->(m) RETURN n,r,m',
        parameters: {}
        })
    });

    if (response.ok) {
        const data = await response.json();
        results = data.result;
        console.log(data.result)
        return data.result
    } else {
        console.error('Failed to fetch data');
    }
       
    }
    // Render graph
    async function renderGraph(data){
        const nodes = new DataSet();  // Use DataSet for managing nodes
        const edges = new DataSet();  // Use DataSet for managing edges

    data.forEach(entry => {
        const sourceNode = { id: entry[0].Id, label: entry[0].Labels.join(", "), ...entry[0].Props };
        const targetNode = { id: entry[2].Id, label: entry[2].Labels.join(", "), ...entry[2].Props };

        if (!nodes.get(sourceNode.id)) {
            nodes.update(sourceNode);
        }
        
        if (!nodes.get(targetNode.id)) {
            nodes.update(targetNode);
        }

        edges.add({ from: sourceNode.id, to: targetNode.id, label: entry[1].Type, ...entry[1].Props });
    });

    const graphData = {
        nodes: nodes,
        edges: edges
    };
  
      network = new Network(container, graphData, {});

    }


    onMount(async () => {
    const data = await fetchQuery();
    // console.debug(data);
    renderGraph(data);
    });
</script>
  
<main>
    <h1>Results from Neo4j:</h1>
    <!-- {#each results as result}
      <p>{JSON.stringify(result)}</p>
    {/each} -->
    <div bind:this={container} style="height: 500px;"></div> <!-- Graph container -->
    
</main>
  