# variable declarations

model = {
    "id": "Flight Track",
    "name": "ER2",
    "availability": "{}/{}",
    "model": {
        "gltf": "https://s3.amazonaws.com/visage-czml/iphex_HIWRAP/img/er2.gltf",
        "scale": 100.0,
        "minimumPixelSize": 32,
        "maximumScale": 150.0
    },
    "position": {
        "cartographicDegrees": []
    },
    "path": {
        "material": {
            "solidColor": {
                "color": {
                    "rgba": [0, 255, 128, 255]
                }
            }
        },
        "width": 1,
        "resolution": 5
    },
    "properties": {
        "roll": {},
        "pitch": {},
        "heading": {}
    }
}

czml_head = {
    "id": "document",
    "name": "wall czml",
    "version": "1.0"
}