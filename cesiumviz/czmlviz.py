from cesiumviz.cesiumviz import CesiumViz

class CZMLViz(CesiumViz):
  def add_script(self, czml_path: str) -> str:
    print('add script that creates cesium viewer and loads it with various kinds of data (czml, 3dtilesets, etc))')
    s1= \
      """
      Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhYTg3MTQxNS01ZTIwLTQ4MmItYjA5NS1hYWM3MWQ0OTNkYTMiLCJpZCI6MTA1ODMzLCJpYXQiOjE2NjE0MzkwOTB9.IWdoSi1zjC7fl7Ncj0YVJgXMfjX3K-RmRcGtjp2xryo";
                
      const viewer = new Cesium.Viewer("cesiumContainer", {
        terrainProvider: Cesium.createWorldTerrain(),
        shouldAnimate: true,
      });
    
      loadCZMLData()
    
      function loadCZMLData() {
      """
    s2 = \
      f"""
        Cesium.CzmlDataSource.load("{czml_path}")
      """
    s3 = \
      """
        .then(async (dataSource) => {
          viewer.dataSources.add(dataSource);
          // zoom to entity, SET CAMERA ANGLE
          viewer.zoomTo(dataSource,  new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-10), 40000));

          // only apply to czml for flight entities
          const flightEntity = dataSource.entities.getById("Flight Track");
          if (flightEntity) {
              // set camera view
              flightEntity.viewFrom = new Cesium.Cartesian3(-30000, -70000, 50000);
              
              // set camera to track entity
              viewer.trackedEntity = flightEntity;

              // fix orientation
              flightEntity.orientation = new Cesium.CallbackProperty((time, _result) => fixOrientation(flightEntity, time), false);

              function fixOrientation(entity, time) {
                  const position = entity.position.getValue(time);
                  let { heading, pitch, roll, correctionOffsets } = entity.properties.getValue(time);
                  // only the heading should change with respect to the position.
                  if(!correctionOffsets) {
                      correctionOffsets = {
                          heading: 0,
                          pitch: 0,
                          roll: 0
                      }
                  }
                  // fix the pitch and roll rotations
                  heading = heading + Cesium.Math.toRadians(correctionOffsets.heading);
                  pitch = pitch + Cesium.Math.toRadians(correctionOffsets.pitch);
                  roll = roll + Cesium.Math.toRadians(correctionOffsets.roll);
                  const hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
                  const fixedOrientation = Cesium.Transforms.headingPitchRollQuaternion(
                      position,
                      hpr
                  );
                  return fixedOrientation;
              }
          }
        });
      }
      """
    return s1 + s2 + s3