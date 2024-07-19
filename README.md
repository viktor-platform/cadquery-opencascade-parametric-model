# OpenCascade modelling in Viktor
This sample app shows how to construct intricate [schematics](.viktor-template/schematic.svg) and [3D models](.viktor-template/3d_model.png) from within Viktor.
![](.viktor-template/cad-demo-cropped.gif)
The goal of this app is to show that Viktor can handle detailed geometries next to those constructed with its built-in geometry module. This is achieved by using an open-source python library ([```CadQuery```](https://cadquery.readthedocs.io/en/latest/index.html)), which allows us to build (parametric) 3D CAD models and output those in high qaulity CAD formats (STEP, AMF, 3MF and GLTF). 

The following functionalities are showcased in this app
- Parametric 3D modelling
- Viktor's Geometry & Image views

## Parametric pillow block
In this template we will see how to view and edit a parametric pillow block for a standard 608-size ball bearing using Viktor:
<img 
    src=".viktor-template/3d_model.png" 
    alt="3D CAD model" 
    style="height=100;width=50;">
Parameters like height, width and bearing diameter in combination with CadQuery's python bindings for OpenCascade modelling are used in ```generate_assembly()```  to construct a parametric 3D model like so
```Python
# obtain parametrization fields
(length, height, bearing_diam, thickness, padding) = (
    params.length,
    params.height,
    params.bearing_diam,
    params.thickness,
    params.padding,
)

body = (
    cq.Workplane("XY")
    .box(length, height, thickness)
    .faces(">Z")
    .workplane()
    .hole(bearing_diam)
    .faces(">Z")
    .workplane()
    .rect(length - padding, height - padding, forConstruction=True)
    .vertices()
    .cboreHole(2.4, 4.4, 2.1)
    .edges("|Z")
    .fillet(params.fillet)
)
```
The assembly is then exported using one of CadQuery's many export funtions to a format that Viktor's GeometryView can display in ```get_geometry_view()```
```Python
assy, _ = generate_assembly(params)
glb = File()  # temporary file to store 3D model as gltf data
cq.occ_impl.exporters.assembly.exportGLTF(assy, glb.source, True)
return GeometryResult(geometry=glb)
```