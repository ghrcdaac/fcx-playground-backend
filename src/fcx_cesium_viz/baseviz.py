class CesiumViz():
  def formulate_body(self, script: str) -> str:
    print('Formaulate a predefined HTML BODY structure with the custom script')
    return \
      f"""
          <!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="utf-8">
            <!-- Include the CesiumJS JavaScript and CSS files -->
            <script src="https://cesium.com/downloads/cesiumjs/releases/1.96/Build/Cesium/Cesium.js"></script>
            <script src="https://releases.jquery.com/git/jquery-git.min.js"></script>
            <link href="https://cesium.com/downloads/cesiumjs/releases/1.96/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
            </head>
          <body>
            <div id="cesiumContainer"></div>
              <script type="module">
                {script}
              </script>
            </div>
          </body>
          </html>
    """

  def add_script(self, url: str) -> str:
    print('add script that creates cesium viewer and loads it with various kinds of data (czml, 3dtilesets, etc))')
    pass

  def generate_html(self, url: str) -> str:
    print('Generate html file with cesium script and body')
    script = self.add_script(url)
    html = self.formulate_body(script)
    print("HTML generation complete.")
    return html