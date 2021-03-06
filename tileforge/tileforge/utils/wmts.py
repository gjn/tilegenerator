from math import ceil

from tempita import Template
from pyproj import Proj, transform

capabilities = """<?xml version="1.0" encoding="UTF-8"?>
<Capabilities version="1.0.0" xmlns="http://www.opengis.net/wmts/1.0" xmlns:ows="http://www.opengis.net/ows/1.1"
              xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns:gml="http://www.opengis.net/gml"
              xsi:schemaLocation="http://schemas.opengis.net/wmts/1.0/wmtsGetCapabilities_response.xsd">
  <ows:ServiceIdentification> </ows:ServiceIdentification>
  <ows:ServiceProvider> </ows:ServiceProvider>
  <ows:OperationsMetadata>
    <ows:Operation name="GetTile">
      <ows:DCP>
        <ows:HTTP><ows:Get xlink:href="{{wmts_gettile}}" /></ows:HTTP>
      </ows:DCP>
    </ows:Operation>
  </ows:OperationsMetadata>
  <!-- <ServiceMetadataURL xlink:href="" /> -->
  <Contents>

  {{for layer in layers}}
    <Layer>
      <ows:Title>{{layer.name}}</ows:Title>
      <ows:Identifier>{{layer.name}}</ows:Identifier>
      <Style isDefault="true">
        <ows:Identifier>default</ows:Identifier>
      </Style>
      <Format>{{layer.format()}}</Format>
      <Dimension>
        <ows:Identifier>{{layer.metadata.get("dimension")}}</ows:Identifier>
      </Dimension>
      <ResourceURL format="{{layer.format()}}" resourceType="tile"
                   template="{{wmts_gettile}}/1.0.0/{{layer.name}}/default/{{layer.metadata.get("dimension")}}/{{layer.metadata.get("matrix_set", layer.name)}}/{TileMatrix}/{TileRow}/{TileCol}.{{layer.extension}}" />
      <TileMatrixSetLink>
        <TileMatrixSet>{{layer.metadata.get("matrix_set", layer.name)}}</TileMatrixSet>
      </TileMatrixSetLink>
    </Layer>
  {{endfor}}

  {{for key, matrix_set in matrix_sets.iteritems()}}
    <TileMatrixSet>
      <ows:Identifier>{{key}}</ows:Identifier>
      <ows:SupportedCRS>urn:ogc:def:crs:{{matrix_set["crs"]}}</ows:SupportedCRS>
    {{for matrix in matrix_set["matrices"]}}
      <TileMatrix>
        <ows:Identifier>{{matrix["id"]}}</ows:Identifier>
        <ScaleDenominator>{{matrix["scale"]}}</ScaleDenominator> <!-- resolution: {{matrix["resolution"]}} -->
        <TopLeftCorner>{{matrix["topleft"]}}</TopLeftCorner>
        <TileWidth>{{matrix["tilewidth"]}}</TileWidth>
        <TileHeight>{{matrix["tileheight"]}}</TileHeight>
        <MatrixWidth>{{matrix["matrixwidth"]}}</MatrixWidth>
        <MatrixHeight>{{matrix["matrixheight"]}}</MatrixHeight>
      </TileMatrix>
    {{endfor}}
    </TileMatrixSet>
  {{endfor}}
  </Contents>
</Capabilities>
"""

meters_per_unit = {
    "feet": 3.28084,
    "meters": 1,
    "degrees": 111118.752,
    "inch": 39.3700787
}

def to_wsg84(srs, x, y):
    return transform(Proj(init=srs.lower()),
                     Proj(proj="latlong", datum="WGS84"), x, y)

def matrix_sets(layers):
    sets = {}
    for layer in layers:
        matrix_set_id = layer.metadata.get("matrix_set", layer.name)
        if matrix_set_id not in sets:
            matrix_set = {"crs": layer.srs.replace(':', '::'), "matrices": []}
            for i, resolution in enumerate(layer.resolutions):
                col = int(ceil(((layer.bbox[2] - layer.bbox[0]) / layer.size[0]) / resolution))
                row = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / resolution))
                if hasattr(layer, 'yorigin') and layer.yorigin == 'top':
                    maxy = layer.bbox[1]
                else:
                    maxy = layer.bbox[1] + (row * layer.size[1] * resolution) 

                matrix_set["matrices"].append({
                    "id": i,
                    "tilewidth": layer.size[0],
                    "tileheight": layer.size[1],
                    "matrixwidth": col,
                    "matrixheight": row,
                    "resolution": resolution,
                    "scale": resolution * meters_per_unit[layer.units] / 0.00028, # 0.000028 correxpond to 0.28 mm per pixel
                    "topleft": "%f %f"%(layer.bbox[0], maxy)
                })
            sets[matrix_set_id] = matrix_set

    return sets

def wmts_capabilities(layers, metadata):
    tmpl = Template(capabilities, namespace={'to_wsg84': to_wsg84})
    return tmpl.substitute(wmts_gettile=metadata.get('wmts_gettile'),
                          layers=layers, matrix_sets=matrix_sets(layers))
    

def main():
    from sys import argv
    from TileCache import Service
    service = Service.load(argv[1])
    print wmts_capabilities(service.layers.values(), service.metadata)

if __name__ == "__main__":
    main()
