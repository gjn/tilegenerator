function createLayer(capabilities, config) {
    var contents = capabilities.contents;
    var layers = contents.layers;

    var layerDef;
    for (var i=0, ii=contents.layers.length; i<ii; ++i) {
        if (contents.layers[i].identifier === config.layer) {
            layerDef = contents.layers[i];
            break;
        }
    }

    if (layerDef) {
        // get the default style for the layer
        var style;
        for (var i=0, ii=layerDef.styles.length; i<ii; ++i) {
            style = layerDef.styles[i];
            if (style.isDefault) {
                break;
            }
        }
        // get the default matrixSet for the layer
        if (!config.matrixSet && layerDef.tileMatrixSetLinks.length === 1) {
            config.matrixSet = layerDef.tileMatrixSetLinks[0].tileMatrixSet;
        }
        var matrixSet = contents.tileMatrixSets[config.matrixSet];
        
        return new OpenLayers.Layer.WMTS(
            OpenLayers.Util.applyDefaults(config, {
                url: capabilities.operationsMetadata.GetTile.dcp.http.get,
                name: layerDef.title,
                style: style.identifier,
                format: layerDef.formats.length === 1 ? layerDef.formats[0] : undefined,
                matrixIds: matrixSet.matrixIds
            }));
    }
}

$(document).ready(function() {
    var map_element = document.getElementById("map");
    map_element.addEventListener("dragover", function(evt) {
        evt.stopPropagation();
        evt.preventDefault();
    });
    map_element.addEventListener("drop", function(evt) {
        evt.stopPropagation();
        evt.preventDefault();
        if (evt.dataTransfer.files.length !== 1) {
            alert("Too much files !");
            return;
        } else {
            var reader = new FileReader();
            reader.onloadend = function() {
                var format = new OpenLayers.Format.WMTSCapabilities();
                var capabilities = format.read(this.result);
                for (var i = 0, len = map.layers.length; i < len; i++) {
                    map.removeLayer(map.layers[i]);
                }

                for (var i = 0, len = capabilities.contents.layers.length; i < len; i++) {
                    var layer = createLayer(capabilities, {
                        requestEncoding: "REST",
                        dimensions: ["210111"],
                        params: {
                            "210111": "210111"
                        },
                        formatSuffixMap: {
                            "image/png": "png",
                            "image/jpeg": "jpeg"
                        },
                        visibility: false,
                        layer: capabilities.contents.layers[i].title
                    });
                    map.addLayer(layer);
                }
                map.zoomToMaxExtent();
            }

            reader.readAsText(evt.dataTransfer.files[0]);
        }
    });

    var layerswitcher = new OpenLayers.Control.LayerSwitcher({
        roundedCorner: false,
        div: OpenLayers.Util.getElement("layer-switcher")

    });
    var map = new OpenLayers.Map(map_element, {
        theme: false,
        projection: "EPSG:21781",
        units: "m",
        allOverlays: true,
        resolutions: [4000,3750,3500,3250,3000,2750,2500,2250,2000,1750,1500,1250,1000,750,650,500,250,100,50,20,10,5,2.5,2,1.5,1,0.5],
        maxExtent: new OpenLayers.Bounds(420000,30000,900000,350000),
        controls: [new OpenLayers.Control.Navigation(), 
                   layerswitcher, 
                   new OpenLayers.Control.MousePosition({
                       formatOutput: function(lonLat) {
                           return OpenLayers.Control.MousePosition.prototype.formatOutput.apply(this, arguments) + 
                               "(" + map.getExtent().toBBOX() + ")";
                       }
                   })]
    });
    var fs = new OpenLayers.Control.FullScreen();
    var panel = new OpenLayers.Control.Panel();
    panel.addControls([fs]);
    map.addControl(panel);
});
