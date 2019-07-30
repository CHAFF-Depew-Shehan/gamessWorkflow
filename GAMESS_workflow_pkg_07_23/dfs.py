def dfs(graph, start, visited=None,recent=None):
    if visited is None:
        visited = set()
        recent = set()
    visited.add(start)
    print(start)

    if not graph[start]:
        print('FOUND STATUS')
        recent.add(start)
    
    for next in graph[start] - visited:
        dfs(graph, next, visited, recent)
    print('Status: ' + str(recent) )
    return visited, recent 

graph = {'1': set(['2', '3']),'2': set(['4', '5']),'3': set(['5']),'4': set(['6']),'5': set(['6']), '6': set(['7']), '7': set([])}

lists, status = dfs(graph, '1')
print(lists)
print(status)
