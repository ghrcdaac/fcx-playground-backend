from cesiumviz import CesiumViz

class TilesViz(CesiumViz):
  def add_script(self, tileset_path: str) -> str:
    p1= \
      """
      Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJhYTg3MTQxNS01ZTIwLTQ4MmItYjA5NS1hYWM3MWQ0OTNkYTMiLCJpZCI6MTA1ODMzLCJpYXQiOjE2NjE0MzkwOTB9.IWdoSi1zjC7fl7Ncj0YVJgXMfjX3K-RmRcGtjp2xryo";
                
      const viewer = new Cesium.Viewer("cesiumContainer", {
        terrainProvider: Cesium.createWorldTerrain(),
        shouldAnimate: true,
      });

      load3DTileData()
    
      function load3DTileData() {
        const tileset = new Cesium.Cesium3DTileset({

      """
    p2 = \
      f"""
        url: "{tileset_path}"
      """
    p3 = \
      """
        });

        tileset.style = new Cesium.Cesium3DTileStyle({
            color: getColorExpression(),
            pointSize: 5.0
          });

        var currentTime = Cesium.JulianDate.fromIso8601("2015-11-10T17:54:00Z")
        var endTime = Cesium.JulianDate.fromIso8601("2015-11-10T23:59:00Z");

        viewer.clock.currentTime = currentTime;
        viewer.clock.multiplier = 10;

        // add the tileset to viewer.
        viewer.scene.primitives.add(tileset);

        viewer.timeline.zoomTo(currentTime, endTime);
        viewer.zoomTo(tileset);
      }
              
      function getColorExpression() {
        // helper to generate color expression,
        //  to style the tileset refer. tilset styling in cesium docs for more info on styling expressions. 
          let reverse = true
          let ascale = 4.346
          let vmin = -10
          let vmax = 30
          let vrange = vmax - vmin
          let hmin = 0.438
          let hrange = 1

          let revScale = ""
          if (reverse) {
              revScale = " * -1.0 + 1.0"
          }
          return `hsla((((clamp(\${value}, ${vmin}, ${vmax}) + ${vmin}) / ${vrange}) ${revScale}) * ${hrange} + ${hmin}, 1.0, 0.5, pow((\${value} - ${vmin})/${vrange}, ${ascale}))`
      }
      """
    return p1 + p2 + p3