#!/usr/bin/env python3
"""
BPMN Decision Tree Path Tracer
Traces paths from start to each destination (Problem Solver, Liquidation Palletizer, Sellable Palletizer, Cleaner)
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, deque

class BPMNPathTracer:
    def __init__(self, xml_file):
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        
        # Extract namespace
        self.ns = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'
        }
        
        # Build graph structures
        self.tasks = {}
        self.flows = {}
        self.incoming = defaultdict(list)
        self.outgoing = defaultdict(list)
        
        self._parse_bpmn()
    
    def _parse_bpmn(self):
        """Parse BPMN XML to build graph"""
        process = self.root.find('.//bpmn:process', self.ns)
        
        if process is None:
            raise ValueError("No process found in BPMN file")
        
        # Parse tasks
        for task in process.findall('.//bpmn:task', self.ns):
            task_id = task.get('id')
            task_name = task.get('name', '')
            self.tasks[task_id] = task_name
            
            # Get incoming flows
            for incoming in task.findall('.//bpmn:incoming', self.ns):
                flow_id = incoming.text
                self.incoming[task_id].append(flow_id)
            
            # Get outgoing flows
            for outgoing in task.findall('.//bpmn:outgoing', self.ns):
                flow_id = outgoing.text
                self.outgoing[task_id].append(flow_id)
        
        # Parse sequence flows
        for flow in process.findall('.//bpmn:sequenceFlow', self.ns):
            flow_id = flow.get('id')
            source = flow.get('sourceRef')
            target = flow.get('targetRef')
            self.flows[flow_id] = (source, target)
    
    def find_destinations(self):
        """Find all destination tasks"""
        destinations = {
            'Problem Solver': [],
            'Liquidation Palletizer': [],
            'Sellable Palletizer': [],
            'Cleaner': []
        }
        
        for task_id, task_name in self.tasks.items():
            if 'Problem Solve' in task_name:
                destinations['Problem Solver'].append(task_id)
            elif 'Liquidation Palletizer' in task_name or 'Liquidaton Palletizer' in task_name:
                destinations['Liquidation Palletizer'].append(task_id)
            elif 'Sellable Palletizer' in task_name:
                destinations['Sellable Palletizer'].append(task_id)
            elif 'Cleaner' in task_name:
                destinations['Cleaner'].append(task_id)
        
        return destinations
    
    def find_start_tasks(self):
        """Find tasks with no incoming flows (start points)"""
        start_tasks = []
        for task_id in self.tasks.keys():
            if task_id not in self.incoming or len(self.incoming[task_id]) == 0:
                start_tasks.append(task_id)
        return start_tasks
    
    def trace_path(self, start_task_id, end_task_id, visited=None):
        """Trace path from start to end using BFS"""
        if visited is None:
            visited = set()
        
        queue = deque([(start_task_id, [start_task_id])])
        visited.add(start_task_id)
        
        while queue:
            current, path = queue.popleft()
            
            if current == end_task_id:
                return path
            
            # Follow outgoing flows
            for flow_id in self.outgoing.get(current, []):
                if flow_id in self.flows:
                    _, target = self.flows[flow_id]
                    if target not in visited:
                        visited.add(target)
                        queue.append((target, path + [target]))
        
        return None
    
    def get_all_paths_to_destination(self, destination_task_id):
        """Get all paths leading to a destination"""
        start_tasks = self.find_start_tasks()
        all_paths = []
        
        for start_id in start_tasks:
            path = self.trace_path(start_id, destination_task_id)
            if path:
                all_paths.append(path)
        
        return all_paths
    
    def print_path_analysis(self):
        """Print analysis of all paths to destinations"""
        destinations = self.find_destinations()
        start_tasks = self.find_start_tasks()
        
        print("=" * 80)
        print("BPMN DECISION TREE PATH ANALYSIS")
        print("=" * 80)
        print(f"\nStart Tasks: {len(start_tasks)}")
        for st in start_tasks:
            print(f"  - {self.tasks.get(st, st)}")
        
        print(f"\nDestinations Found:")
        for dest_type, task_ids in destinations.items():
            print(f"  {dest_type}: {len(task_ids)} endpoint(s)")
        
        print("\n" + "=" * 80)
        
        for dest_type, task_ids in destinations.items():
            if not task_ids:
                continue
            
            print(f"\n{dest_type.upper()}")
            print("-" * 80)
            
            for dest_id in task_ids:
                dest_name = self.tasks.get(dest_id, dest_id)
                print(f"\n  Destination: {dest_name}")
                
                # Find paths
                paths = []
                for start_id in start_tasks:
                    path = self.trace_path(start_id, dest_id)
                    if path:
                        paths.append(path)
                
                print(f"  Found {len(paths)} path(s):")
                
                for i, path in enumerate(paths[:5], 1):  # Show first 5 paths
                    path_names = [self.tasks.get(t, t) for t in path]
                    print(f"\n  Path {i}:")
                    for j, task_name in enumerate(path_names, 1):
                        indent = "    " + "  " * (j - 1)
                        print(f"{indent}{j}. {task_name}")
                
                if len(paths) > 5:
                    print(f"\n  ... and {len(paths) - 5} more path(s)")

def main():
    import sys
    
    xml_file = "bpmn.xml"
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
    
    try:
        tracer = BPMNPathTracer(xml_file)
        tracer.print_path_analysis()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

