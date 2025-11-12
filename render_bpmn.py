#!/usr/bin/env python3
"""
BPMN Diagram Renderer
Converts BPMN XML to a visual diagram (PNG/SVG)
"""

import sys
import os

try:
    from bpmn_python import bpmn_diagram_rep as diagram
    from bpmn_python import bpmn_diagram_layouter as layouter
    from bpmn_python import bpmn_to_image as image_exporter
except ImportError:
    print("Installing required packages...")
    os.system("pip install bpmn-python")
    try:
        from bpmn_python import bpmn_diagram_rep as diagram
        from bpmn_python import bpmn_diagram_layouter as layouter
        from bpmn_python import bpmn_to_image as image_exporter
    except ImportError:
        print("Error: Could not import bpmn-python. Please install it manually:")
        print("  pip install bpmn-python")
        sys.exit(1)

def render_bpmn_to_image(xml_file, output_file="bpmn_diagram.png"):
    """Render BPMN XML file to an image"""
    try:
        # Read BPMN XML
        with open(xml_file, 'r', encoding='utf-8') as f:
            bpmn_xml = f.read()
        
        # Parse BPMN diagram
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml(bpmn_xml)
        
        # Layout the diagram
        layouter.BpmnDiagramGraphLayouter(bpmn_graph).layout()
        
        # Export to image
        image_exporter.BpmnDiagramImageExporter(bpmn_graph).export_diagram(output_file)
        
        print(f"✓ Successfully rendered BPMN diagram to: {output_file}")
        return True
    except Exception as e:
        print(f"Error rendering BPMN diagram: {e}")
        return False

if __name__ == "__main__":
    xml_file = "bpmn.xml"
    
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
    
    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' not found!")
        sys.exit(1)
    
    output_file = "bpmn_diagram.png"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    render_bpmn_to_image(xml_file, output_file)

