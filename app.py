import cadquery as cq
from viktor import ViktorController
from viktor.core import File
from viktor.parametrization import NumberField, ViktorParametrization
from viktor.views import GeometryResult, GeometryView, ImageResult, ImageView


import warnings
warnings.filterwarnings("ignore", category=UserWarning) 
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class Parametrization(ViktorParametrization):
    length = NumberField("Length [mm]", default=30)
    height = NumberField("Height [mm]", default=40)
    bearing_diam = NumberField("Bearing diameter [mm]", default=22)
    thickness = NumberField("Thickness [mm]", default=10)
    padding = NumberField("Padding [mm]", default=8)
    fillet = NumberField("Fillet [mm]", default=2, num_decimals=1, step=0.5)


def generate_assembly(params):
    assy = cq.Assembly()

    (length, height, bearing_diam, thickness, padding) = (params.length, params.height, params.bearing_diam, params.thickness, params.padding)

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

GLTB_PATH = Path(__file__).parent / "output.gltb"
SVG_PATH = Path(__file__).parent / "output.svg"

class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def get_geometry_view(self, params, **kwargs):
        assy, _ = generate_assembly(params)
        cq.occ_impl.exporters.assembly.exportGLTF(assy, str(GLTB_PATH), True)
        return GeometryResult(File.from_path(GLTB_PATH))
    

    @ImageView("Drawing", duration_guess=1)
    def create_result(self, params, **kwargs):
        _, body = generate_assembly(params)
        cq.exporters.export(body, str(SVG_PATH))

        return ImageResult(File.from_path(SVG_PATH))