import warnings

# supress user- and deprecation warnings resulting from cadquery module
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from viktor import ViktorController
from viktor.core import File
from viktor.parametrization import NumberField, ViktorParametrization
from viktor.views import GeometryResult, GeometryView, ImageResult, ImageView

# OpenCascade library
import cadquery as cq

class Parametrization(ViktorParametrization):
    length = NumberField("Length", default=30, suffix="mm")
    height = NumberField("Height", default=40, suffix="mm")
    bearing_diam = NumberField("Bearing diameter", default=22, suffix="mm")
    thickness = NumberField("Thickness", default=10, suffix="mm")
    padding = NumberField("Padding", default=8, suffix="mm")
    fillet = NumberField("Fillet", default=2, num_decimals=1, step=0.5, suffix="mm")


def generate_assembly(params):
    """
    Defines the CAD geometry using the parametrization.
    """
    assy = cq.Assembly()

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

    assy.add(body, color=cq.Color(1, 0.27, 0.0), name="body")
    return assy, body


class Controller(ViktorController):
    label = "pillow block"
    parametrization = Parametrization

    @GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def get_geometry_view(self, params, **kwargs):
        """
        Renders the 3D model. First it (re-)generates the assembly. Then,
        exports the gltf data to a temporary file, which is passed to
        GeometryResult and displayed as a GeometryView.
        """
        assy, _ = generate_assembly(params)
        glb = File()  # temporary file to store 3D model as gltf data
        cq.occ_impl.exporters.assembly.exportGLTF(assy, glb.source, True)
        return GeometryResult(geometry=glb)

    @ImageView("Drawing", duration_guess=1)
    def create_result(self, params, **kwargs):
        """
        Renders the 2D schematic. First it (re-)generates the assembly. Then,
        exports the svg to a temporary file, which is passed to
        ImageResult and displayed as an ImageView.
        """
        _, body = generate_assembly(params)
        svg = File()  # temporary file to store 2D schematic as svg
        cq.exporters.export(body, svg.source, exportType=cq.exporters.ExportTypes.SVG)
        return ImageResult(svg)
