# BPMN Diagram Viewer

This directory contains tools to visualize your BPMN XML file as a diagram.

## Method 1: HTML Viewer (Recommended)

The easiest way to view your BPMN diagram is using the HTML viewer:

1. **Open `bpmn-viewer.html` in a web browser**
   - Simply double-click the file, or
   - Open it in Chrome, Firefox, Edge, or Safari

2. The diagram will automatically load and display with interactive controls:
   - **Zoom In/Out**: Adjust the zoom level
   - **Reset Zoom**: Return to 100% zoom
   - **Fit Viewport**: Automatically fit the entire diagram to the screen
   - **Download as SVG**: Export the diagram as an SVG file

**Note**: Make sure `bpmn.xml` is in the same directory as `bpmn-viewer.html`

## Method 2: Python Script

If you prefer to generate a static image file:

1. **Install dependencies**:
   ```bash
   pip install bpmn-python
   ```

2. **Run the script**:
   ```bash
   python render_bpmn.py
   ```

   Or specify custom input/output files:
   ```bash
   python render_bpmn.py bpmn.xml output.png
   ```

## Method 3: Online Tools

You can also use online BPMN viewers:
- **bpmn.io**: https://bpmn.io/viewer/ (drag and drop your XML file)
- **Camunda Modeler**: Download from https://camunda.com/download/modeler/

## Your BPMN File

Your `bpmn.xml` file contains:
- A complex process workflow with multiple decision points
- Tasks, gateways, and sequence flows
- Complete diagram layout information

The diagram includes:
- Start events
- Multiple decision gateways (Yes/No questions)
- Various tasks (Complete TREX, Cleaner, etc.)
- End events
- Text annotations for decision labels

