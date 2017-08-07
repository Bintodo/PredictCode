import pytest
import unittest.mock as mock

import open_cp.network as network
import open_cp.data
import numpy as np
import datetime

def test_PlanarGraphBuilder():
    b = network.PlanarGraphBuilder()
    assert b.add_vertex(0.2, 0.5) == 0
    b.set_vertex(5, 1, 2) 
    b.add_edge(0, 5)
    g = b.build()
    assert g.vertices == {0:(0.2,0.5), 5:(1,2)}
    assert g.edges == [(0,5)]

    b1 = network.PlanarGraphBuilder(g)
    assert b1.add_vertex(5,6) == 6
    b1.add_edge(5,6)
    g1 = b1.build()
    assert g1.vertices == {0:(0.2,0.5), 5:(1,2), 6:(5,6)}
    assert g1.edges == [(0,5), (5,6)]
    # Check haven't mutated g
    assert g.vertices == {0:(0.2,0.5), 5:(1,2)}
    assert g.edges == [(0,5)]

@pytest.fixture
def planar_graph_geo_builder():
    b = network.PlanarGraphGeoBuilder()
    b.add_path([(0,0),(1,1),(5.1,1.2)])
    b.add_path([(2,0),(1,1),(0,5),(5.1,1.2)])
    b.add_path([(0,0),(0,5)])
    return b    

def test_PlanarGraphGeoBuilder(planar_graph_geo_builder):
    b = planar_graph_geo_builder
    assert b.coord_nodes == {(0,0):[0], (1,1):[1,4], (5.1,1.2):[2],
                             (2,0):[3], (0,5):[5]}
    assert b.edges == [(0,1), (1,2), (3,4), (4,5), (5,2), (0,5)]

def test_PlanarGraphGeoBuilder_builds(planar_graph_geo_builder):
    g = planar_graph_geo_builder.build()

    assert g.vertices == {0:(0,0), 1:(1,1), 2:(5.1,1.2), 3:(2,0), 4:(1,1), 5:(0,5)}        
    assert g.edges == [(0,1), (1,2), (3,4), (4,5), (5,2), (0,5)]

@pytest.fixture
def planar_graph_node_builder():
    b = network.PlanarGraphNodeBuilder()
    b.add_path([(0,0),(1,1),(5.1,1.2)])
    b.add_edge(0,0,2,2)
    b.add_path([(1,0),(1,1),(2,2)])
    return b

def test_PlanarGraphNodeBuilder(planar_graph_node_builder):
    b = planar_graph_node_builder
    assert b.coord_nodes == [(0,0), (1,1), (5.1,1.2), (2,2), (1,0)]
    assert b.edges == [(0,1), (1,2), (0,3), (4,1), (1,3)]

def test_PlanarGraphNodeBuilder_builds(planar_graph_node_builder):
    g = planar_graph_node_builder.build()
    
    assert g.vertices == {0:(0,0), 1:(1,1), 2:(5.1,1.2), 3:(2,2), 4:(1,0)}
    assert g.edges == [(0,1), (1,2), (0,3), (4,1), (1,3)]

def test_PlanarGraphNodeBuilder_tolerance():
    b = network.PlanarGraphNodeBuilder()
    b.tolerance = 0.2
    assert b.tolerance == pytest.approx(0.2)
    
    b.add_path([(0,0),(1,1),(5.1,1.2)])
    b.add_edge(0.1,0.01,2,2)
    
    assert b.coord_nodes == [(0,0), (1,1), (5.1,1.2), (2,2)]
    assert b.edges == [(0,1), (1,2), (0,3)]

def test_PlanarGraphNodeOneShot():
    nodes = [(0,0), (1,1), (5.1,1.2), (0.1,0.01), (2,2)]
    b = network.PlanarGraphNodeOneShot(nodes, 0.2)
    
    b.add_path([(0,0),(1,1),(5.1,1.2)])
    b.add_edge(0.1,0.01,2,2)
    
    g = b.build()
    assert set(g.vertices.values()) == {(0,0), (1,1), (5.1,1.2), (2,2)}
    assert len(g.edges) == 3
    assert [g.vertices[x] for x in g.edges[0]] == [(0,0), (1,1)]
    assert [g.vertices[x] for x in g.edges[1]] == [(1,1), (5.1,1.2)]
    assert [g.vertices[x] for x in g.edges[2]] == [(0,0), (2,2)]

def test_PlanarGraph_constructs():
    with pytest.raises(ValueError):
        network.PlanarGraph([(0,1,2), (0,2,3)], [])
        
    with pytest.raises(ValueError):
        network.PlanarGraph([(0,1,2), (1,2,3)], [(0,0)])
        
    g = network.PlanarGraph([(0,1,2), (1,2,3)], [(0,1)])
    assert g.vertices == {0:(1,2), 1:(2,3)}
    assert g.edges == [(0,1)]

@pytest.fixture
def graph1():
    b = network.PlanarGraphGeoBuilder()
    b.add_path([(0,0), (10,0)])
    b.add_path([(0,1), (5,5), (9,1)])
    return b.build()

def test_PlanarGraph_lengths(graph1):
    assert graph1.length(0) == pytest.approx(10)
    assert graph1.length(1) == pytest.approx(np.sqrt(25+16))
    assert graph1.length(2) == pytest.approx(np.sqrt(32))
    
def test_PlanarGraph_as_quads(graph1):
    exp = [ (0,0,10,0), (0,1,5,5), (5,5,9,1) ]
    x = graph1.as_quads()
    np.testing.assert_allclose(x, exp)
    
def test_PlanarGraph_as_lines(graph1):
    exp = [ ((0,0),(10,0)), ((0,1),(5,5)), ((5,5),(9,1)) ]
    x = graph1.as_lines()
    np.testing.assert_allclose(x, exp)

def test_PlanarGraph_project(graph1):
    edge, t = graph1.project_point_to_graph(5,1) 
    assert edge == (0, 1)
    assert t == pytest.approx(0.5)

    edge, t = graph1.project_point_to_graph(-0.5, -0.5)
    assert edge == (0, 1)
    assert t == 0
    
    edge, t = graph1.project_point_to_graph(-0.1, 1)
    assert edge == (2, 3)
    assert t == 0
    
    edge, t = graph1.project_point_to_graph(5, 5.2)
    assert (edge, t) == ((2,3), 1) or (edge, t) == ((3,4), 0)

    edge, t = graph1.project_point_to_graph(9, .4)
    assert edge == (0, 1)
    assert t == pytest.approx(0.9)

    edge, t = graph1.project_point_to_graph(9, .6)
    assert edge == (3, 4)
    assert t == 1

    edge, t = graph1.project_point_to_graph(2.5, 2)
    assert edge == (2, 3)
    assert t == pytest.approx(0.402439024)

def test_io(graph1):
    js = graph1.dump_json()
    import json
    out = json.loads(js)
    assert set(out.keys()) == {"keys", "xcoords", "ycoords", "edges"}
    
    g = network.PlanarGraph.from_json(js)
    assert network.approximately_equal(graph1, g)
    
    b = graph1.dump_bytes()
    g = network.PlanarGraph.from_bytes(b)
    assert network.approximately_equal(graph1, g)

@pytest.fixture
def graph2():
    b = network.PlanarGraphGeoBuilder()
    b.add_path([(0,10), (1,10)])
    b.add_path([(1,10), (2,11), (3, 11), (4,10)])
    b.add_path([(1,10), (2,9), (3, 9), (4,10)])
    b.add_path([(2,9), (2,11)])
    b.add_path([(4,10), (5,10)])
    return b.build()

def test_graph2(graph2):
    assert graph2.vertices == {0:(0,10), 1:(1,10), 2:(2,11), 3:(3,11), 4:(4,10),
                               5:(2,9), 6:(3,9), 7:(5,10)}
    assert graph2.edges == [(0,1), (1,2), (2,3), (3,4), (1,5), (5,6), (6,4), (5,2), (4,7)]

def test_PlanarGraph_find_edge(graph2):
    assert graph2.find_edge(0,1) == (0, 1)
    assert graph2.find_edge(1,0) == (0, -1)
    assert graph2.find_edge(3,4) == (3, 1)
    assert graph2.find_edge(4,3) == (3, -1)
    with pytest.raises(KeyError):
        graph2.find_edge(1,3)

def test_PlanarGraph_neighbours(graph2):
    assert graph2.neighbours(0) == [1]
    assert graph2.neighbours(1) == [0,2,5]
    assert graph2.neighbours(2) == [1,3,5]
    assert graph2.neighbours(3) == [2,4]
    assert graph2.neighbours(4) == [3,6,7]
    assert graph2.neighbours(5) == [1,2,6]
    assert graph2.neighbours(6) == [4,5]
    assert graph2.neighbours(7) == [4]

def test_PlanarGraph_degree(graph2):
    assert graph2.degree(0) == 1
    assert graph2.degree(1) == 3
    assert graph2.degree(3) == 2

def test_PlanarGraph_neighbourhood_edges(graph2):
    assert graph2.neighbourhood_edges(0) == [0]
    assert graph2.neighbourhood_edges(1) == [0,1,4]
    assert graph2.neighbourhood_edges(2) == [1,2,7]
    assert graph2.neighbourhood_edges(3) == [2,3]
    assert graph2.neighbourhood_edges(4) == [3,6,8]
    assert graph2.neighbourhood_edges(5) == [4,5,7]
    assert graph2.neighbourhood_edges(6) == [5,6]
    assert graph2.neighbourhood_edges(7) == [8]
    
def test_PlanarGraph_neighbourhood_paths_between(graph2):
    assert list(graph2.paths_between(0,1,10000)) == [[0,1]]
    
    out = [ tuple(x) for x in graph2.paths_between(0,2,10000) ]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,2), (0,1,5,2), (0,1,5,6,4,3,2)}
    
    out = [ tuple(x) for x in graph2.paths_between(0,3,10000) ]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,2,3), (0,1,5,2,3), (0,1,5,6,4,3), (0,1,2,5,6,4,3)}
    
    out = [ tuple(x) for x in graph2.paths_between(0,7,10000) ]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,2,3,4,7), (0,1,2,5,6,4,7), (0,1,5,6,4,7), (0,1,5,2,3,4,7)}
    
def test_PlanarGraph_neighbourhood_paths_between_length_bound(graph2):
    assert list(graph2.paths_between(0,1,1)) == [[0,1]]
    assert list(graph2.paths_between(0,1,0.9)) == []
    
    assert list(graph2.paths_between(0,2,2)) == []
    assert list(graph2.paths_between(0,2,2.5)) == [[0,1,2]]
    
    assert list(graph2.paths_between(0,6,3)) == []
    assert list(graph2.paths_between(0,6,3.5)) == [[0,1,5,6]]
    out = [ tuple(x) for x in graph2.paths_between(0,6,5.5) ]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,5,6), (0,1,2,5,6)}

def test_PlanarGraph_paths_between_avoiding(graph2):
    assert list(graph2.paths_between_avoiding(0, 2, [(0,1)], 100)) == []
    assert list(graph2.paths_between_avoiding(0, 2, [(1,0)], 100)) == []
    
    out = [tuple(x) for x in graph2.paths_between_avoiding(0, 3, [(1,2), (5,2)], 100)]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,5,6,4,3)}

    out = [tuple(x) for x in graph2.paths_between_avoiding(0, 7, [(1,2), (4,3)], 100)]
    assert len(set(out)) == len(out)
    assert set(out) == {(0,1,5,6,4,7)}

def test_PlanarGraph_edge_paths_between(graph2):
    out = [ tuple(x) for x in graph2.edge_paths_between((0,1), (1,2), 1000)]
    assert len(set(out)) == len(out)
    assert set(out) == {(1,), (1,5,2), (1,5,6,4,3,2)}

    out = [ tuple(x) for x in graph2.edge_paths_between((0,1), (4,7), 1000)]
    assert len(set(out)) == len(out)
    assert set(out) == {(1,2,3,4), (1,2,5,6,4), (1,5,6,4), (1,5,2,3,4)}

    out = [ tuple(x) for x in graph2.edge_paths_between((3,4), (2,5), 1000)]
    assert len(set(out)) == len(out)
    assert set(out) == {(3,2), (4,6,5), (3,2,1,5), (4,6,5,1,2)}

    out = [ tuple(x) for x in graph2.edge_paths_between((3,4), (5,1), 1000)]
    assert len(set(out)) == len(out)
    assert set(out) == {(3,2,1), (3,2,5), (4,6,5), (4,6,5,2,1)}

    out = [ tuple(x) for x in graph2.edge_paths_between((0,1), (1,2), 0)]
    assert len(set(out)) == len(out)
    assert set(out) == {(1,)}

    out = [ tuple(x) for x in graph2.edge_paths_between((0,1), (1,2), 2)]
    assert len(set(out)) == len(out)
    assert set(out) == {(1,)}

    out = [ tuple(x) for x in graph2.edge_paths_between((0,1), (1,2), 3.5)]
    assert len(set(out)) == len(out)
    assert set(out) == {(1,), (1,5,2)}

def test_PlanarGraph_walk_from(graph2):
    search = graph2.walk_from(0, 1)
    assert next(search) == ([0], 0.0)
    with pytest.raises(StopIteration):
        search.send(True)
    search.close()

    search = graph2.walk_from(1, 2)
    assert next(search) == ([1], 0.0)
    assert search.send(True) == ([1,5], pytest.approx(np.sqrt(2)))
    assert search.send(True) == ([1,5,2], pytest.approx(np.sqrt(2)+2))
    assert search.send(True) == ([1,5,2,3], pytest.approx(np.sqrt(2)+3))
    assert search.send(True) == ([1,5,2,3,4], pytest.approx(np.sqrt(2)*2+3))
    assert search.send(True) == ([1,5,2,3,4,7], pytest.approx(np.sqrt(2)*2+4))
    assert search.send(True) == ([1,5,2,3,4,6], pytest.approx(np.sqrt(2)*3+3))
    assert search.send(True) == ([1,5,6], pytest.approx(np.sqrt(2)+1))
    assert search.send(True) == ([1,5,6,4], pytest.approx(np.sqrt(2)*2+1))
    assert search.send(True) == ([1,5,6,4,7], pytest.approx(np.sqrt(2)*2+2))
    assert search.send(True) == ([1,5,6,4,3], pytest.approx(np.sqrt(2)*3+1))
    assert search.send(True) == ([1,5,6,4,3,2], pytest.approx(np.sqrt(2)*3+2))
    assert search.send(True) == ([1,0], 1)
    with pytest.raises(StopIteration):
        search.send(True)

    search = graph2.walk_from(1, 2)
    assert next(search) == ([1], 0.0)
    assert search.send(True) == ([1,5], pytest.approx(np.sqrt(2)))
    assert search.send(False) == ([1,0], 1)
    with pytest.raises(StopIteration):
        search.send(True)

    search = graph2.walk_from(2, 1)
    assert next(search) == ([2], 0.0)
    assert search.send(True) == ([2,5], 2)
    assert search.send(True) == ([2,5,6], 3)
    assert search.send(False) == ([2,5,1], pytest.approx(2+np.sqrt(2)))
    assert search.send(True) == ([2,5,1,0], pytest.approx(3+np.sqrt(2)))
    assert search.send(True) == ([2,3], 1)
    with pytest.raises(StopIteration):
        search.send(False)

def test_TimedNetworkPoints():
    times = [datetime.datetime(2017,8,7,12,30), datetime.datetime(2017,8,7,13,45)]
    locations = [((1,2), 0.4), ((3,4), 0.1)]
    tnp = network.TimedNetworkPoints(times, locations)

    expected_times = [(datetime.datetime(2017,1,1) - x).total_seconds() for x in times]
    np.testing.assert_allclose(expected_times,
        (np.datetime64("2017-01-01") - tnp.timestamps) / np.timedelta64(1, "s"))
    np.testing.assert_allclose(tnp.distances, [0.4, 0.1])
    np.testing.assert_allclose(tnp.start_keys, [1, 3])
    np.testing.assert_allclose(tnp.end_keys, [2, 4])

    with pytest.raises(ValueError):
        network.TimedNetworkPoints([datetime.datetime(2017,8,7,12,30)], locations)

    assert tnp[0] == [np.datetime64("2017-08-07T12:30"), 1, 2, 0.4]
    tnpp = tnp[1:]
    assert np.all(tnpp.timestamps == [np.datetime64("2017-08-07T13:45")])
    assert tnpp.start_keys == [3]
    assert tnpp.end_keys == [4]
    np.testing.assert_allclose(tnpp.distances, [0.1])

    graph = mock.Mock()
    graph.edge_to_coords.return_value = (1.3, 2.4)
    tp = tnp.to_timed_points(graph)
    np.testing.assert_allclose(expected_times,
        (np.datetime64("2017-01-01") - tp.timestamps) / np.timedelta64(1, "s"))
    np.testing.assert_allclose(tp.xcoords, [1.3, 1.3])
    np.testing.assert_allclose(tp.ycoords, [2.4, 2.4])
    assert graph.edge_to_coords.call_args_list == [mock.call(1, 2, 0.4), mock.call(3, 4, 0.1)]

def test_TimedNetworkPoints_from_projection():
    times = [datetime.datetime(2017,8,7,12,30), datetime.datetime(2017,8,7,13,45)]
    xcs = [1.2, 2.3]
    ycs = [4.5, 6.7]
    tp = open_cp.data.TimedPoints.from_coords(times, xcs, ycs)
    graph = mock.Mock()
    graph.project_point_to_graph.return_value = ((1,2), 0.3)

    tnp = network.TimedNetworkPoints.project_timed_points(tp, graph)

    expected_times = [(datetime.datetime(2017,1,1) - x).total_seconds() for x in times]
    np.testing.assert_allclose(expected_times,
        (np.datetime64("2017-01-01") - tnp.timestamps) / np.timedelta64(1, "s"))
    np.testing.assert_allclose(tnp.start_keys, [1, 1])
    np.testing.assert_allclose(tnp.end_keys, [2, 2])
    np.testing.assert_allclose(tnp.distances, [0.3, 0.3])
    graph.project_point_to_graph.call_args_list == [mock.call(1.2, 4.5), mock.call(2.3, 6.7)]
