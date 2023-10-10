# variable declarations

model = {
    "id": "Flight Track",
    "name": "P3",
    "availability": "{}/{}",
    "model": {
        "gltf":"https://fcx-czml.s3.amazonaws.com/img/p3.gltf",
        "scale": 1.0,
        "maximumScale": 1000.0
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

TrackColor = {'P3B': [0, 255, 128, 255],
              'ER2': [0, 255, 255, 128]}

modelP3B = {
        "gltf":"https://fcx-czml.s3.amazonaws.com/img/p3.gltf",
        "scale": 5.0,
        "maximumScale": 1000.0
}

modelER2 = {
    "gltf":"https://fcx-czml.s3.amazonaws.com/img/er2.gltf",
    "scale": 900.0,
    "minimumPixelSize": 500,
    "maximumScale": 1000.0
}